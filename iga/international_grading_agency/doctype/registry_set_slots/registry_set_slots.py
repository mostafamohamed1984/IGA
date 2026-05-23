import frappe
from frappe.model.document import Document


class RegistrySetSlots(Document):

    def validate(self):
        if self.year and self.year < 0:
            frappe.throw("Year cannot be negative.")
