import frappe
from frappe import _
from frappe.model.document import Document
import requests


class LabelPrintSettings(Document):
    
    def validate(self):
        self._validate_dimensions()
        self._validate_dpi()
    
    def _validate_dimensions(self):
        """Validate label dimensions."""
        if self.label_width and (self.label_width < 10 or self.label_width > 500):
            frappe.throw(_("Label width should be between 10 and 500mm"))
        
        if self.label_height and (self.label_height < 10 or self.label_height > 500):
            frappe.throw(_("Label height should be between 10 and 500mm"))
    
    def _validate_dpi(self):
        """Validate print DPI."""
        if self.print_dpi and (self.print_dpi < 150 or self.print_dpi > 1200):
            frappe.throw(_("Print DPI should be between 150 and 1200"))
    
    @frappe.whitelist()
    def print_test_label(self, submission_item, preview_only=True):
        """Print or preview a test label."""
        if not submission_item:
            return {"error": "Submission Item is required"}
        
        # Get submission item data
        item = frappe.get_doc("Submission Item", submission_item)
        
        # Generate label HTML
        label_html = self._generate_label_html(item)
        
        if preview_only:
            return label_html
        
        # Send to printer
        if not self.printer_api_endpoint:
            return {"error": "Printer API endpoint not configured"}
        
        try:
            response = requests.post(
                f"{self.printer_api_endpoint}/print",
                json={
                    "printer": self.default_printer,
                    "content": label_html,
                    "dpi": self.print_dpi
                },
                timeout=10
            )
            
            if response.status_code == 200:
                return {"success": True, "message": "Label sent to printer"}
            else:
                return {"error": f"Print failed: {response.text}"}
        
        except Exception as e:
            return {"error": str(e)}
    
    def _generate_label_html(self, item):
        """Generate label HTML from submission item."""
        html = f"""
        <div style="width: {self.label_width}mm; height: {self.label_height}mm; 
                    border: 1px solid #000; padding: 5mm; font-family: Arial;">
            <div style="text-align: center; font-weight: bold; font-size: 14pt;">
                IGA CERTIFICATION
            </div>
            <hr>
            <div style="margin-top: 5mm;">
                <strong>Certificate:</strong> {item.certificate_number}<br>
                <strong>Grade:</strong> {item.final_grade or 'Pending'}<br>
                <strong>Item:</strong> {item.item_reference}<br>
                <strong>Result:</strong> {item.result_type or 'Pending'}
            </div>
        </div>
        """
        return html
    
    @frappe.whitelist()
    def preview_template(self, template):
        """Preview a label template."""
        if not template:
            return {"error": "Template is required"}
        
        template_doc = frappe.get_doc("Label Template Master", template)
        
        # Generate preview HTML
        preview_html = f"""
        <div style="border: 2px solid #2490ef; padding: 20px; background: #f5f5f5;">
            <h4>{template_doc.template_code}</h4>
            <p><strong>Holder Type:</strong> {template_doc.holder_type or 'N/A'}</p>
            <p><strong>Label Variant:</strong> {template_doc.label_variant}</p>
            <p><strong>Logo Variant:</strong> {template_doc.logo_variant}</p>
            <hr>
            <div style="background: white; padding: 10px; min-height: 100px;">
                <em>Template preview would render here based on layout_json</em>
            </div>
        </div>
        """
        
        return preview_html
    
    @frappe.whitelist()
    def check_printer_status(self):
        """Check printer status via API."""
        if not self.printer_api_endpoint:
            return {"error": "Printer API endpoint not configured"}
        
        try:
            response = requests.get(
                f"{self.printer_api_endpoint}/status",
                params={"printer": self.default_printer},
                timeout=5
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                return {"error": f"Status check failed: {response.text}"}
        
        except Exception as e:
            return {
                "online": False,
                "error": str(e)
            }
