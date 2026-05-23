import frappe
from frappe.model.document import Document
from frappe.utils import today

class ItemReferencePricing(Document):
    def before_save(self):
        self.last_updated = today()
