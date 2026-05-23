import frappe
from frappe import _
from frappe.model.document import Document
import requests
import json
import hmac
import hashlib


class NFCSettings(Document):
    
    def validate(self):
        if self.nfc_enabled:
            if not self.api_endpoint:
                frappe.throw(_("API Endpoint is required when NFC is enabled"))
            if not self.api_key:
                frappe.throw(_("API Key is required when NFC is enabled"))
        if not self.payload_template:
            frappe.throw(_("Payload Template is required"))
        if not self.active_signing_profile:
            frappe.throw(_("Active Signing Profile is required"))
        if not self.verify_url_base:
            frappe.throw(_("Verify URL Base is required"))
    
    @frappe.whitelist()
    def test_nfc_connection(self):
        """Test connection to NFC service."""
        if not self.nfc_enabled:
            return {"success": False, "error": "NFC is not enabled"}
        
        if not self.api_endpoint:
            return {"success": False, "error": "API Endpoint not configured"}
        
        try:
            # Test ping endpoint
            response = requests.get(
                f"{self.api_endpoint}/ping",
                headers={"Authorization": f"Bearer {self.api_key}"},
                timeout=5
            )
            
            if response.status_code == 200:
                return {
                    "success": True,
                    "message": "NFC service connection successful",
                    "response": response.json() if response.content else {}
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}: {response.text}"
                }
        
        except requests.exceptions.Timeout:
            return {"success": False, "error": "Connection timeout"}
        except requests.exceptions.ConnectionError:
            return {"success": False, "error": "Could not connect to NFC service"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    @frappe.whitelist()
    def generate_nfc_data(self, certificate_no, grade):
        """Generate test NFC chip data."""
        if not certificate_no or not grade:
            return {"error": "Certificate number and grade are required"}
        
        # Generate payload
        payload = {
            "certificate_number": certificate_no,
            "grade": grade,
            "timestamp": frappe.utils.now(),
            "issuer": "IGA"
        }
        
        # Generate signature
        signature = self._generate_signature(payload)
        
        return {
            "payload": payload,
            "signature": signature,
            "encoded": self._encode_payload(payload, signature)
        }
    
    def _generate_signature(self, payload):
        """Generate HMAC signature for payload."""
        if not self.api_key:
            return "NO_KEY"
        
        payload_str = json.dumps(payload, sort_keys=True)
        signature = hmac.new(
            self.api_key.encode(),
            payload_str.encode(),
            hashlib.sha256
        ).hexdigest()
        
        return signature
    
    def _encode_payload(self, payload, signature):
        """Encode payload and signature for NFC chip."""
        import base64

        data = {
            "payload": payload,
            "signature": signature
        }

        json_str = json.dumps(data)
        encoded = base64.b64encode(json_str.encode()).decode()

        return encoded

    @staticmethod
    def verify_nfc_payload(encoded_payload):
        """Verify an NFC payload and return (cert_no, valid)."""
        import base64
        import hmac
        import hashlib

        nfc_settings = frappe.get_single("NFC Settings")
        if not nfc_settings.nfc_enabled:
            return None, False

        try:
            decoded = base64.b64decode(encoded_payload).decode()
            data = json.loads(decoded)
        except Exception:
            return None, False

        payload = data.get("payload")
        signature = data.get("signature")
        if not payload or not signature:
            return None, False

        cert_no = payload.get("certificate_number") if isinstance(payload, dict) else payload
        if not cert_no:
            return None, False

        api_key = nfc_settings.get_password("api_key") if nfc_settings.api_key else ""
        if not api_key:
            return cert_no, False

        payload_str = json.dumps(payload, sort_keys=True)
        expected = hmac.new(api_key.encode(), payload_str.encode(), hashlib.sha256).hexdigest()
        valid = hmac.compare_digest(expected, signature)

        return cert_no, valid
