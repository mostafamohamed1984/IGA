import frappe
from frappe import _
from frappe.model.document import Document


class ReferenceCodeGenerator(Document):
    
    def autoname(self):
        """Use generator_key as name."""
        if not self.generator_key:
            self._generate_key()
        self.name = self.generator_key
    
    def _generate_key(self):
        """Generate generator key from type, country, year."""
        type_map = {
            "Coin": "CN",
            "Medal": "MD",
            "Token": "TK",
            "Banknote": "BN",
            "Postcard": "PC",
            "Collectible Card": "CC"
        }
        type_code = type_map.get(self.collectible_type, "XX")
        
        self.generator_key = f"{type_code}-{self.country_code}-{self.year}"
    
    def validate(self):
        if not self.generator_key:
            self._generate_key()
        
        # Validate country code length
        if self.country_code and len(self.country_code) > 3:
            frappe.throw(_("Country code must be 3 characters or less"))
        
        # Validate year
        import datetime
        current_year = datetime.datetime.now().year
        if self.year < 1 or self.year > current_year + 10:
            frappe.throw(_("Year must be between 1 and {0}").format(current_year + 10))


@frappe.whitelist()
def preview_next_code(generator_key):
    """Preview the next reference code that would be generated."""
    generator = frappe.get_doc("Reference Code Generator", generator_key)
    
    # Get template from Module Settings
    settings = frappe.get_single("Module Settings")
    template = settings.code_format_template or "{TYPE}-{CTY}-{YYYY}-{SEQ3}"
    
    # Get type code
    type_map = {
        "Coin": "CN",
        "Medal": "MD",
        "Token": "TK",
        "Banknote": "BN",
        "Postcard": "PC",
        "Collectible Card": "CC"
    }
    type_code = type_map.get(generator.collectible_type, "XX")
    
    # Next sequence
    next_seq = generator.last_sequence + 1
    
    # Generate code
    code = template
    code = code.replace("{TYPE}", type_code)
    code = code.replace("{CTY}", generator.country_code)
    code = code.replace("{YYYY}", str(generator.year))
    code = code.replace("{YY}", str(generator.year)[-2:])
    code = code.replace("{SEQ3}", f"{next_seq:03d}")
    code = code.replace("{SEQ4}", f"{next_seq:04d}")
    code = code.replace("{SEQ5}", f"{next_seq:05d}")
    
    return code
