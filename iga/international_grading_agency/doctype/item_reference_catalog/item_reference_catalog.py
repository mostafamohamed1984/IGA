import frappe
from frappe import _
from frappe.model.document import Document


class ItemReferenceCatalog(Document):
    
    def autoname(self):
        """Use title as name."""
        if not self.title:
            frappe.throw(_("Title is required"))
        self.name = self.title
    
    def validate(self):
        self._validate_year()
        self._generate_ref_code_if_needed()
    
    def _validate_year(self):
        """Validate year fields."""
        import datetime
        current_year = datetime.datetime.now().year
        
        if self.year_ad and (self.year_ad < 1 or self.year_ad > current_year + 10):
            frappe.throw(_("Year AD should be between 1 and {0}").format(current_year + 10))
        
        if self.year_ah and (self.year_ah < 1 or self.year_ah > 1500):
            frappe.throw(_("Year AH should be between 1 and 1500"))
    
    def _generate_ref_code_if_needed(self):
        """Auto-generate reference code if not set."""
        if not self.ref_code and self.status == "Active":
            self.ref_code = self.generate_reference_code()
    
    @frappe.whitelist()
    def generate_reference_code(self):
        """Generate reference code based on Module Settings template."""
        if self.ref_code:
            return self.ref_code
        
        # Get settings
        settings = frappe.get_single("Module Settings")
        
        if not settings.auto_generate_on_active:
            return None
        
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
        type_code = type_map.get(self.collectible_type, "XX")
        
        # Get country code
        country_code = self.country[:3] if self.country else "XXX"
        
        # Get year
        year = self.year_ad or self.year_ah or 0
        
        # Get or create generator
        generator_key = f"{type_code}-{country_code}-{year}"
        
        generator = frappe.db.get_value(
            "Reference Code Generator",
            {"generator_key": generator_key},
            ["name", "last_sequence"],
            as_dict=True
        )
        
        if not generator:
            # Create new generator
            gen_doc = frappe.get_doc({
                "doctype": "Reference Code Generator",
                "generator_key": generator_key,
                "collectible_type": self.collectible_type,
                "country_code": country_code,
                "year": year,
                "last_sequence": 0
            })
            gen_doc.insert(ignore_permissions=True)
            sequence = 1
        else:
            sequence = generator.last_sequence + 1
        
        # Update sequence
        frappe.db.set_value(
            "Reference Code Generator",
            generator_key if not generator else generator.name,
            "last_sequence",
            sequence
        )
        
        # Generate code from template
        code = template
        code = code.replace("{TYPE}", type_code)
        code = code.replace("{CTY}", country_code)
        code = code.replace("{YYYY}", str(year))
        code = code.replace("{YY}", str(year)[-2:] if year else "00")
        code = code.replace("{SEQ3}", f"{sequence:03d}")
        code = code.replace("{SEQ4}", f"{sequence:04d}")
        code = code.replace("{SEQ5}", f"{sequence:05d}")
        
        return code
