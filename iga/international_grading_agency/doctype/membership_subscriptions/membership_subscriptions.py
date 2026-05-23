import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import today, getdate


class MembershipSubscriptions(Document):

    def autoname(self):
        self.subscription_no = frappe.model.naming.make_autoname("IGA-SUB-.YYYY.-.#####")
        self.name = self.subscription_no

    def validate(self):
        if self.start_date and self.end_date:
            if getdate(self.start_date) > getdate(self.end_date):
                frappe.throw(_("Start Date cannot be after End Date."))
        if not self.member_no:
            self.member_no = self.customer
        self._enforce_one_active_per_customer()

    def _enforce_one_active_per_customer(self):
        if self.status == "Active":
            existing = frappe.db.get_value(
                "Membership Subscriptions",
                {
                    "customer": self.customer,
                    "status": "Active",
                    "name": ("!=", self.name)
                },
                "name"
            )
            if existing:
                frappe.throw(_(
                    "Customer {0} already has an active subscription: {1}. "
                    "Cancel the existing subscription before activating a new one."
                ).format(self.customer, existing))

    def on_submit(self):
        """Activate and set credits from plan on submission."""
        if self.status == "Pending":
            plan = frappe.get_doc("Membership Plans", self.plan)
            self.credits_remaining = plan.included_credits
            self.status = "Active"
            self.db_update()

    @frappe.whitelist()
    def deduct_credit(self):
        """Decrement one credit. Call on submission approval."""
        if self.credits_remaining > 0:
            self.credits_remaining -= 1
            self.db_update()
        else:
            frappe.throw(_("No credits remaining on subscription {0}.").format(self.name))

    def is_active(self):
        return self.status == "Active" and getdate(self.end_date) >= getdate(today())

    @frappe.whitelist()
    def renew_subscription(self):
        """Renew subscription for another period."""
        from dateutil.relativedelta import relativedelta
        
        if self.status == "Cancelled":
            frappe.throw(_("Cannot renew a cancelled subscription. Create a new subscription instead."))
        
        plan = frappe.get_doc("Membership Plans", self.plan)
        
        # Calculate new end date
        if self.billing_period == "Monthly":
            new_end_date = getdate(self.end_date) + relativedelta(months=1)
        else:  # Annual
            new_end_date = getdate(self.end_date) + relativedelta(years=1)
        
        # Update subscription
        self.end_date = new_end_date
        self.status = "Active"
        self.credits_remaining += plan.included_credits
        
        # Create renewal invoice
        invoice = frappe.get_doc({
            "doctype": "Sales Invoice",
            "customer": self.customer,
            "posting_date": today(),
            "due_date": today(),
            "custom_subscription": self.name,
            "items": [{
                "item_code": "MEMBERSHIP",
                "item_name": f"Membership Renewal - {plan.plan_name}",
                "description": f"Subscription: {self.name}",
                "qty": 1,
                "rate": plan.monthly_fee if self.billing_period == "Monthly" else plan.annual_fee
            }]
        })
        invoice.insert(ignore_permissions=True)
        
        self.save(ignore_permissions=True)
        
        return {
            "subscription_no": self.name,
            "new_end_date": self.end_date,
            "credits_added": plan.included_credits,
            "invoice_no": invoice.name
        }
