import frappe
from frappe.model.document import Document


class MembershipSettings(Document):

    @staticmethod
    def get_earn_rate():
        return frappe.db.get_single_value("Membership Settings", "earn_rate") or 0.01

    @staticmethod
    def get_point_value():
        return frappe.db.get_single_value("Membership Settings", "point_value") or 0.10

    @staticmethod
    def get_min_redeem():
        return frappe.db.get_single_value("Membership Settings", "min_redeem_points") or 100
