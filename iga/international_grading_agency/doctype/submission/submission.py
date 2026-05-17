import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, today, cstr
import uuid


class Submission(Document):

    def before_insert(self):
        self._generate_submission_no()
        self._generate_tracking_id()

    def _generate_submission_no(self):
        if not self.submission_no:
            settings = frappe.get_single("Reference Code Generator")
            # Fall back to sequential naming if Reference Code Generator not configured
            last = frappe.db.sql(
                "SELECT MAX(submission_no) FROM `tabSubmission` WHERE submission_no LIKE 'AA%'"
            )
            last_no = last[0][0] if last and last[0][0] else "AA000000"
            seq = int(last_no[2:]) + 1
            self.submission_no = f"AA{seq:06d}"

    def _generate_tracking_id(self):
        if not self.tracking_id:
            prefix = frappe.db.get_single_value("IGA Grading Settings", "tracking_id_prefix") or "TRK"
            uid = uuid.uuid4().hex[:10].upper()
            self.tracking_id = f"{prefix}-{uid}"

    def validate(self):
        self._validate_subscription()
        if self.submission_source == "Dealer" and not self.dealer:
            frappe.throw(_("Dealer field is required when Submission Source is Dealer."))

    def _validate_subscription(self):
        if not self.subscription:
            return
        sub = frappe.get_doc("Membership Subscriptions", self.subscription)
        if not sub.is_active():
            frappe.throw(_(
                "Membership subscription {0} is not active. "
                "Status: {1}, End Date: {2}"
            ).format(self.subscription, sub.status, sub.end_date))
        if sub.customer != self.customer:
            frappe.throw(_("Subscription {0} does not belong to customer {1}.").format(
                self.subscription, self.customer
            ))

    def on_update(self):
        self._sync_item_counts()
        self._compute_billing_totals()

    def _sync_item_counts(self):
        """Recount Submission Items linked to this submission."""
        count = frappe.db.count("Submission Item", {"parent_submission": self.name})
        total_val = frappe.db.sql(
            "SELECT IFNULL(SUM(declared_value),0) FROM `tabSubmission Item` WHERE parent_submission=%s",
            self.name
        )[0][0]
        frappe.db.set_value("Submission", self.name, {
            "item_count": count,
            "declared_value_total": total_val
        }, update_modified=False)

    def _compute_billing_totals(self):
        """Compute subtotal, VAT, grand total from service fee × item count."""
        if not self.service_tier or not self.item_count:
            return
        service = frappe.get_doc("Service Master", self.service_tier)
        base = service.base_fee or 0
        member_discount = service.member_discount_pct or 0
        bulk_discount = service.bulk_discount_pct if (self.is_bulk and service.is_bulk_eligible) else 0
        total_discount_pct = min(member_discount + bulk_discount, 100)

        subtotal = base * self.item_count
        discount_amount = subtotal * (total_discount_pct / 100)
        discounted = subtotal - discount_amount
        vat_rate = frappe.db.get_single_value("IGA Grading Settings", "vat_rate") or 14
        vat = discounted * (vat_rate / 100)
        grand = discounted + vat

        frappe.db.set_value("Submission", self.name, {
            "subtotal": subtotal,
            "discount_pct": total_discount_pct,
            "vat_amount": round(vat, 2),
            "grand_total": round(grand, 2)
        }, update_modified=False)

    def approve(self, approved_by=None):
        """Mark as Approved. Deduct credit if uses_credit."""
        if self.internal_review_status != "Pending Review":
            frappe.throw(_("Only submissions in 'Pending Review' can be approved."))
        self.internal_review_status = "Approved"
        self.submission_approved_on = now_datetime()
        self.submission_approved_by = approved_by or frappe.session.user
        self.status = "Received"
        if self.uses_credit and self.subscription:
            sub = frappe.get_doc("Membership Subscriptions", self.subscription)
            sub.deduct_credit()
            self.credits_used = 1
        self.save(ignore_permissions=True)

    @frappe.whitelist()
    def generate_proforma_invoice(self):
        """Generate Proforma Invoice for this submission."""
        if self.proforma_invoice_no:
            frappe.throw(_("Proforma Invoice already exists: {0}").format(self.proforma_invoice_no))
        
        # Create Sales Invoice in Draft mode
        invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": self.customer,
            "posting_date": today(),
            "due_date": today(),
            "is_proforma": 1,
            "custom_submission": self.name,
            "custom_tracking_id": self.tracking_id,
            "items": []
        })
        
        # Add service line items
        for item in self.items:
            invoice.append("items", {
                "item_code": self.service_tier,
                "item_name": f"Grading Service - {item.item_reference}",
                "description": f"Certificate: {item.certificate_number}",
                "qty": 1,
                "rate": self.subtotal / self.item_count if self.item_count else 0,
                "custom_submission_item": item.name
            })
        
        # Apply discounts
        if self.discount_pct:
            invoice.discount_amount = self.subtotal * (self.discount_pct / 100)
        
        invoice.insert(ignore_permissions=True)
        
        # Update submission
        self.proforma_invoice_no = invoice.name
        self.save(ignore_permissions=True)
        
        return {
            "invoice_no": invoice.name,
            "grand_total": invoice.grand_total,
            "status": "Draft"
        }

    @frappe.whitelist()
    def get_active_subscription(self):
        """Get active subscription for the customer."""
        if not self.customer:
            return None
        
        subscriptions = frappe.get_all(
            "Membership Subscriptions",
            filters={
                "customer": self.customer,
                "status": "Active"
            },
            fields=["name", "plan", "status", "end_date", "credits_remaining"],
            order_by="end_date desc",
            limit=1
        )
        
        if subscriptions:
            return subscriptions[0]
        
        return None
