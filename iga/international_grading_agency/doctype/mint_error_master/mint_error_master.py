import frappe
from frappe.model.document import Document


class MintErrorMaster(Document):
    def validate(self):
        if not self.get("error_code"):
            frappe.throw("Error Code is required.")
