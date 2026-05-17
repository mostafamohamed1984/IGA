import frappe
from frappe.model.document import Document


class CountryMaster(Document):
    def validate(self):
        if self.iso_code:
            self.iso_code = self.iso_code.upper().strip()
        if len(self.iso_code) != 2:
            frappe.throw("ISO Code must be exactly 2 characters.")
