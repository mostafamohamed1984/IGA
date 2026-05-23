import frappe
from frappe.model.document import Document


class MembershipSettings(Document):

    def validate(self):
        if self.max_redeem_pct < 0 or self.max_redeem_pct > 100:
            frappe.throw("Max Redeem % must be between 0 and 100.")
        if self.renewal_reminder_days < 0:
            frappe.throw("Renewal Reminder days cannot be negative.")
        if self.expiry_reminder_days < 0:
            frappe.throw("Expiry Reminder days cannot be negative.")

    @staticmethod
    def get_earn_rate():
        return frappe.db.get_single_value("Membership Settings", "earn_rate") or 0.01

    @staticmethod
    def get_point_value():
        return frappe.db.get_single_value("Membership Settings", "point_value") or 0.10

    @staticmethod
    def get_min_redeem():
        return frappe.db.get_single_value("Membership Settings", "min_redeem_points") or 100
