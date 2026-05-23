# Copyright (c) 2026, Mustafa Nazier and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import getdate

class IGAPromoCode(Document):
    def validate(self):
        # Enforce code casing
        if self.code:
            self.code = self.code.upper().strip()
        
        # Validate value
        if self.value <= 0:
            frappe.throw("Promo code value must be greater than zero")
            
        if self.type == "percent" and self.value > 100:
            frappe.throw("Percent discount cannot exceed 100%")

    @frappe.whitelist()
    def validate_code(self):
        """API/RPC validator for promo code"""
        current_date = getdate()
        
        if not self.active:
            return {"valid": False, "reason": "inactive"}
            
        if self.expires_at and getdate(self.expires_at) < current_date:
            return {"valid": False, "reason": "expired"}
            
        if self.usage_limit and self.usage_count >= self.usage_limit:
            return {"valid": False, "reason": "expired"}
            
        return {
            "valid": True,
            "code": {
                "code": self.code,
                "type": self.type,
                "value": self.value,
                "description": self.description,
                "expiresAt": self.expires_at,
                "active": self.active
            }
        }
