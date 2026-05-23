import frappe
import json
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime, today
from frappe.utils import getdate


class Submission(Document):

    def before_insert(self):
        self._generate_submission_no()
        self._generate_tracking_id()

    def _generate_submission_no(self):
        if not self.submission_no:
            last = frappe.db.sql(
                "SELECT MAX(submission_no) FROM `tabSubmission` WHERE submission_no LIKE 'AA%'"
            )
            last_no = last[0][0] if last and last[0][0] else "AA000000"
            seq = int(last_no[2:]) + 1
            self.submission_no = f"AA{seq:05d}"

    def _generate_tracking_id(self):
        if not self.tracking_id:
            prefix = frappe.db.get_single_value("IGA Grading Settings", "tracking_id_prefix") or "TRK"
            import string as _string
            import secrets
            allowed = _string.digits + "ABCDEFGHJKLMNPQRSTUVWXYZ"
            uid = ''.join(secrets.choice(allowed) for _ in range(6))
            self.tracking_id = f"{prefix}-{uid}"

    def validate(self):
        self._validate_subscription()
        if self.submission_source == "Dealer" and not self.dealer:
            frappe.throw(_("Dealer field is required when Submission Source is Dealer."))
        if self.promo_code:
            self._re_validate_promo_code()

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

    def _re_validate_promo_code(self):
        """Server-side promo re-validation (never trust client value)."""
        promo = frappe.get_doc("IGA Promo Code", self.promo_code)
        result = promo.validate_code()
        if not result.get("valid"):
            frappe.throw(_("Promo code {0} is no longer valid: {1}").format(
                self.promo_code, result.get("reason")
            ))

    def on_update(self):
        self._sync_item_counts()
        self._compute_billing_totals()

    def _sync_item_counts(self):
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
        if not self.service_tier or not self.item_count:
            return
        service = frappe.get_doc("Service Master", self.service_tier)
        base = service.base_fee or 0

        base_subtotal = base * self.item_count

        # Sum add-ons from child items
        items = frappe.get_all("Submission Item",
            filters={"parent_submission": self.name},
            fields=["add_ons"]
        )
        addons_subtotal = 0
        # TODO: compute add-ons pricing from Service Master add-on rates
        # For now, set to 0 until AddOn pricing is modeled

        subtotal_before_discount = base_subtotal + addons_subtotal

        bulk_discount_amount = 0
        if self.is_bulk and self.item_count >= 5:
            bulk_discount_amount = round(subtotal_before_discount * 0.10, 2)

        member_discount_pct = service.member_discount_pct or 0
        total_discount_pct = min(member_discount_pct, 100) if not self.is_bulk else min(member_discount_pct, 100)

        subtotal = subtotal_before_discount - bulk_discount_amount
        vat_rate = frappe.db.get_single_value("IGA Grading Settings", "vat_rate") or 14
        vat = round(subtotal * (vat_rate / 100), 2)
        grand = subtotal + vat

        frappe.db.set_value("Submission", self.name, {
            "subtotal": subtotal,
            "base_subtotal": base_subtotal,
            "addons_subtotal": addons_subtotal,
            "subtotal_before_discount": subtotal_before_discount,
            "bulk_discount": bulk_discount_amount,
            "discount_pct": total_discount_pct,
            "vat_amount": vat,
            "grand_total": grand,
            "currency": "EGP"
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

    @frappe.whitelist()
    def get_items_breakdown(self):
        """Compute per-stage counts of submission items."""
        stages = ["Created", "Received", "Grading", "Slabbing", "QC",
                   "Imaging", "Shipped", "Ready for Pickup", "Completed", "On Hold"]
        breakdown = {s: 0 for s in stages}
        items = frappe.get_all("Submission Item",
            filters={"parent_submission": self.name},
            fields=["current_stage"]
        )
        for item in items:
            stage = item.current_stage or "Created"
            if stage in breakdown:
                breakdown[stage] += 1
        return breakdown

    @frappe.whitelist()
    def get_activity(self):
        """Return customer-visible activity timeline."""
        activities = []
        submission = frappe.get_doc("Submission", self.name)

        # Created
        activities.append(self._make_activity(
            "submission_created",
            "Submission created",
            "تم إنشاء التقديم",
            submission.creation
        ))

        # Received
        if submission.received_on:
            activities.append(self._make_activity(
                "submission_received",
                "Items received at IGA facility",
                "تم استلام القطع في منشأة IGA",
                submission.received_on
            ))

        # Grading complete
        if submission.grading_complete_on:
            activities.append(self._make_activity(
                "grading_complete",
                "Grading completed",
                "تم الانتهاء من التقييم",
                submission.grading_complete_on
            ))

        # Invoice issued
        if submission.proforma_invoice:
            activities.append(self._make_activity(
                "invoice_issued",
                f"Proforma invoice {submission.proforma_invoice} issued",
                f"تم إصدار الفاتورة الأولية {submission.proforma_invoice}",
                submission.modified
            ))

        # Sales invoice
        if submission.sales_invoice:
            activities.append(self._make_activity(
                "sales_invoice_issued",
                f"Sales invoice {submission.sales_invoice} issued",
                f"تم إصدار فاتورة المبيعات {submission.sales_invoice}",
                submission.modified
            ))

        # Completed
        if submission.completed_on:
            activities.append(self._make_activity(
                "submission_completed",
                "Submission completed and delivered",
                "تم الانتهاء من التقديم والتسليم",
                submission.completed_on
            ))

        # Sort by date ascending
        activities.sort(key=lambda a: a["date"])
        return activities

    def _make_activity(self, activity_id, desc_en, desc_ar, date_val):
        return {
            "id": f"{self.name}-{activity_id}",
            "date": cstr(date_val) if date_val else now_datetime().isoformat(),
            "description": desc_en,
            "descriptionAr": desc_ar
        }


@frappe.whitelist()
def compute_quote(service_tier, category, is_bulk=0, items=None):
    """Compute pricing quote with full breakdown. Called by POST /submissions/quote."""
    items = items or []
    item_count = len(items)

    service = frappe.get_doc("Service Master", service_tier)
    base = service.base_fee or 0

    base_subtotal = base * item_count

    addons_subtotal = 0
    for itm in items:
        add_ons = itm.get("add_ons") or []
        # TODO: compute add-on pricing from Service Master when add-on model is ready

    subtotal_before_discount = base_subtotal + addons_subtotal

    bulk_discount_amount = 0
    if is_bulk and item_count >= 5:
        bulk_discount_amount = round(subtotal_before_discount * 0.10, 2)

    subtotal = subtotal_before_discount - bulk_discount_amount

    vat_rate = frappe.db.get_single_value("IGA Grading Settings", "vat_rate") or 14
    vat = round(subtotal * (vat_rate / 100), 2)
    total = round(subtotal + vat, 2)

    return {
        "base_subtotal": round(base_subtotal, 2),
        "addons_subtotal": round(addons_subtotal, 2),
        "subtotal_before_discount": round(subtotal_before_discount, 2),
        "bulk_discount": bulk_discount_amount,
        "subtotal": round(subtotal, 2),
        "vat": vat,
        "total": total,
        "currency": "EGP"
    }


@frappe.whitelist()
def get_submission_activity(submission_no):
    """Standalone endpoint for submission activity."""
    submission = frappe.get_doc("Submission", {"submission_no": submission_no})
    return submission.get_activity()


@frappe.whitelist()
def cancel_submission(submission_no):
    """Cancel a submission (only allowed when status is Created)."""
    submission = frappe.get_doc("Submission", {"submission_no": submission_no})
    if submission.status != "Created":
        frappe.throw(_("Only submissions in 'Created' status can be cancelled."))
    submission.status = "Cancelled"
    submission.save(ignore_permissions=True)
    return {"status": "cancelled"}


@frappe.whitelist()
def get_verify_result(cert_no):
    """Return verify result for a certificate."""
    item = frappe.get_value("Submission Item", {"certificate_number": cert_no}, "*")
    if not item:
        frappe.throw(_("Certificate not found"), frappe.DoesNotExistError)

    submission_status = frappe.db.get_value("Submission", item.parent_submission, "status")
    if submission_status not in ("Shipped", "Ready for Pickup", "Completed"):
        frappe.throw(_("Verification not yet available — submission still in progress"), frappe.PermissionError)

    ref = None
    description = None
    description_ar = None
    mintmark = None
    ref_code = None
    if item.item_reference:
        ref = frappe.get_doc("Item Reference Catalog", item.item_reference)
        ref_code = ref.ref_code
        description = ref.description_en
        description_ar = ref.description_ar
        mintmark = ref.mintmark

    final_grade_str = ""
    if item.final_grade:
        grade_doc = frappe.get_doc("Grade Scale Master", item.final_grade)
        final_grade_str = grade_doc.grade_name or grade_doc.grade_code

    # Population context
    population_context = None
    if ref_code and final_grade_str:
        all_certs = frappe.get_all("Submission Item",
            filters={
                "item_reference": item.item_reference,
                "result_type": ("in", ("Encapsulated", "Details")),
                "current_stage": "Completed"
            },
            fields=["final_grade"]
        )
        at_grade = sum(1 for c in all_certs if c.final_grade == item.final_grade)
        higher = sum(1 for c in all_certs if c.final_grade != item.final_grade and _grade_numeric(c.final_grade) > _grade_numeric(item.final_grade))
        lower = sum(1 for c in all_certs if c.final_grade != item.final_grade and _grade_numeric(c.final_grade) < _grade_numeric(item.final_grade))
        population_context = {
            "at_grade": at_grade,
            "higher": higher,
            "lower": lower,
            "is_top_grade": higher == 0
        }

    return {
        "certificate_number": item.certificate_number,
        "ref_code": ref_code,
        "result_type": item.result_type or "Encapsulated",
        "label_country_denom": item.label_country_denom or "",
        "label_year_line": item.label_year_line or "",
        "mintmark": mintmark,
        "label_series_line": item.label_series_line,
        "final_grade": final_grade_str,
        "designations": [],
        "holder_type": item.holder_type or "",
        "images": {
            "obverse": item.images_obverse,
            "reverse": item.images_reverse
        },
        "graded_on": cstr(item.graded_on) if item.graded_on else "",
        "description": description,
        "description_ar": description_ar,
        "population_context": population_context
    }


def _grade_numeric(grade_name):
    """Extract numeric portion from a grade name e.g. 'MS 65' -> 65."""
    if not grade_name:
        return 0
    import re
    nums = re.findall(r'\d+', grade_name)
    return int(nums[0]) if nums else 0
