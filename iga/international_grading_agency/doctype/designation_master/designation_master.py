import frappe
from frappe.model.document import Document


class DesignationMaster(Document):
    def validate(self):
        if not self.label_print_order:
            self.label_print_order = 0
