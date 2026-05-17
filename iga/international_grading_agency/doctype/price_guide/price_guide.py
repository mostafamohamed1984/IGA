import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class PriceGuide(Document):
    
    def autoname(self):
        """Use reference_item as name."""
        if not self.reference_item:
            frappe.throw(_("Reference Item is required"))
        self.name = self.reference_item
    
    def validate(self):
        self._populate_from_reference()
        self._validate_grade_values()
    
    def _populate_from_reference(self):
        """Auto-populate fields from Item Reference Catalog."""
        if not self.reference_item:
            return
        
        ref = frappe.get_doc("Item Reference Catalog", self.reference_item)
        
        # Auto-populate if empty
        if not self.category and ref.collectible_type:
            # Map collectible type to category
            type_to_category = {
                "Coin": "Modern" if ref.year_ad and ref.year_ad >= 1951 else "Early Modern",
                "Medal": "Medals & Tokens",
                "Token": "Medals & Tokens"
            }
            self.category = type_to_category.get(ref.collectible_type)
        
        if not self.country:
            self.country = ref.country
        
        if not self.year:
            self.year = ref.year_ad or ref.year_ah
        
        if not self.mint:
            self.mint = ref.mint
    
    def _validate_grade_values(self):
        """Validate grade values table."""
        if not self.grade_values:
            frappe.throw(_("At least one grade value is required"))
        
        # Check for duplicate grade/designation combinations
        seen = set()
        for entry in self.grade_values:
            key = (entry.grade, entry.designation or "")
            if key in seen:
                frappe.throw(_("Duplicate grade/designation combination: {0} {1}").format(
                    entry.grade, entry.designation or ""
                ))
            seen.add(key)
    
    def before_save(self):
        """Update metadata."""
        self.last_updated = now_datetime()
        self.updated_by = frappe.session.user
    
    def on_update(self):
        """Clear cache when price guide is updated."""
        frappe.cache().delete_value(f"price_guide:{self.name}")
