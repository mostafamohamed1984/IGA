import frappe
from frappe.model.document import Document

class PostageMatrix(Document):
    def validate(self):
        if not self.rates:
            frappe.throw("At least one rate row is required")

    @frappe.whitelist()
    def get_rates(self):
        """Return structured rates for the API"""
        return self.rates
