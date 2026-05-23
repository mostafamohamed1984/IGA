import frappe
from frappe.model.document import Document


class HolderTypesMaster(Document):
    def validate(self):
        if self.outer_width_mm and self.outer_height_mm:
            if self.outer_width_mm <= 0 or self.outer_height_mm <= 0:
                frappe.throw("Dimensions must be positive values.")
        if self.max_coin_diameter_mm and self.min_coin_diameter_mm:
            if self.max_coin_diameter_mm < self.min_coin_diameter_mm:
                frappe.throw("Max coin diameter must be >= min coin diameter.")
