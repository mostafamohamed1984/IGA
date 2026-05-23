import frappe
from frappe import _
from frappe.model.document import Document
import requests


class ShippingSettings(Document):
    
    def validate(self):
        self._validate_zones()
        self._validate_default_carrier()
        self._validate_insurance()
        self._validate_packaging()

    def _validate_default_carrier(self):
        if not self.default_carrier:
            frappe.throw(_("Default Carrier is required"))

    def _validate_insurance(self):
        if not self.insurance_tiers:
            frappe.throw(_("At least one Insurance Tier is required"))

    def _validate_packaging(self):
        if not self.packaging_rules:
            frappe.throw(_("At least one Packaging Rule is required"))
    
    def _validate_zones(self):
        """Validate shipping zones."""
        if not self.shipping_zones:
            return
        
        # Check for duplicate zone codes
        codes = [z.zone_code for z in self.shipping_zones if z.zone_code]
        if len(codes) != len(set(codes)):
            frappe.throw(_("Duplicate zone codes found"))
    
    @frappe.whitelist()
    def test_carrier_connection(self):
        """Test connection to carrier API."""
        if not self.carrier_api_endpoint:
            return {"success": False, "error": "Carrier API endpoint not configured"}
        
        try:
            response = requests.get(
                f"{self.carrier_api_endpoint}/ping",
                headers={"Authorization": f"Bearer {self.carrier_api_key}"},
                timeout=5
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "Carrier API connection successful"
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @frappe.whitelist()
    def calculate_shipping(self, submission, zone, service_level="Standard"):
        """Calculate shipping cost for a submission."""
        if not submission or not zone:
            return {"error": "Submission and zone are required"}
        
        # Get submission data
        sub_doc = frappe.get_doc("Submission", submission)
        
        # Get zone data
        zone_data = None
        for z in self.shipping_zones or []:
            if z.zone_name == zone:
                zone_data = z
                break
        
        if not zone_data:
            return {"error": f"Zone {zone} not found"}
        
        # Calculate base rate
        base_rate = zone_data.base_rate or 0
        
        # Weight surcharge (assume 50g per item)
        weight_kg = (sub_doc.item_count * 50) / 1000
        weight_surcharge = weight_kg * (zone_data.per_kg_rate or 0) if weight_kg > 1 else 0
        
        # Service level fee
        service_fees = {
            "Standard": 0,
            "Express": base_rate * 0.5,
            "Overnight": base_rate * 1.0
        }
        service_fee = service_fees.get(service_level, 0)
        
        # Insurance (1% of declared value)
        insurance = (sub_doc.declared_value_total or 0) * 0.01
        
        # Total
        total = base_rate + weight_surcharge + service_fee + insurance
        
        return {
            "base_rate": base_rate,
            "weight_surcharge": weight_surcharge,
            "service_fee": service_fee,
            "insurance": insurance,
            "total": round(total, 2),
            "currency": "EGP"
        }
    
    @frappe.whitelist()
    def track_shipment(self, tracking_number):
        """Track shipment via carrier API."""
        if not tracking_number:
            return {"error": "Tracking number is required"}
        
        if not self.carrier_api_endpoint:
            return {"error": "Carrier API endpoint not configured"}
        
        try:
            response = requests.get(
                f"{self.carrier_api_endpoint}/track/{tracking_number}",
                headers={"Authorization": f"Bearer {self.carrier_api_key}"},
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Tracking failed: {response.text}"}
        
        except Exception as e:
            return {"error": str(e)}
