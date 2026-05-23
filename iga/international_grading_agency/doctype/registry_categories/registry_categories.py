import frappe
from frappe.model.document import Document


class RegistryCategories(Document):

    def validate(self):
        if self.parent_category and self.parent_category == self.name:
            frappe.throw("A category cannot be its own parent.")
