import frappe
from frappe.model.document import Document


class ServiceMaster(Document):
    def validate(self):
        if self.turnaround_days_min and self.turnaround_days_max:
            if self.turnaround_days_min > self.turnaround_days_max:
                frappe.throw("Turnaround Days Min cannot be greater than Max.")
        if self.base_fee and self.base_fee < 0:
            frappe.throw("Base Fee cannot be negative.")
