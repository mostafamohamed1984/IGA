import frappe
from frappe.model.document import Document

VALID_PLAN_CODES = {"SILVER", "GOLD", "DIAMOND", "DEALER"}


class MembershipPlans(Document):
    def validate(self):
        if self.plan_code and self.plan_code.upper() not in VALID_PLAN_CODES:
            frappe.msgprint(
                f"Non-standard plan code '{self.plan_code}'. Standard codes: SILVER, GOLD, DIAMOND, DEALER.",
                alert=True
            )
        if self.annual_fee < 0:
            frappe.throw("Annual Fee cannot be negative.")
        if self.monthly_fee and self.monthly_fee < 0:
            frappe.throw("Monthly Fee cannot be negative.")
        if self.tier_order < 0:
            frappe.throw("Tier Order cannot be negative.")
