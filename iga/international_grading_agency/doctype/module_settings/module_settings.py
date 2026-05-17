import frappe
from frappe import _
from frappe.model.document import Document


class ModuleSettings(Document):
    
    def validate(self):
        self._validate_code_template()
        self._validate_registry_weights()
    
    def _validate_code_template(self):
        """Validate reference code template."""
        if not self.code_format_template:
            return
        
        valid_tokens = ["{TYPE}", "{CTY}", "{YYYY}", "{YY}", "{SEQ3}", "{SEQ4}", "{SEQ5}"]
        has_valid_token = any(token in self.code_format_template for token in valid_tokens)
        
        if not has_valid_token:
            frappe.throw(_("Code format template must include at least one valid token: {0}").format(
                ", ".join(valid_tokens)
            ))
    
    def _validate_registry_weights(self):
        """Validate registry formula weights."""
        total = (self.grade_weight or 0) + (self.population_weight or 0) + (self.value_weight or 0)
        
        if total == 0:
            frappe.msgprint(_("Warning: All registry weights are zero. Registry points will not be calculated."))


@frappe.whitelist()
def generate_reference_code(collectible_type, country_code, year):
    """Generate a reference code for testing."""
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
    type_code = type_map.get(collectible_type, "XX")
    
    # Get or create generator
    generator_key = f"{type_code}-{country_code}-{year}"
    
    generator = frappe.db.get_value(
        "Reference Code Generator",
        {"generator_key": generator_key},
        ["name", "last_sequence"],
        as_dict=True
    )
    
    sequence = (generator.last_sequence + 1) if generator else 1
    
    # Generate code from template
    code = template
    code = code.replace("{TYPE}", type_code)
    code = code.replace("{CTY}", country_code)
    code = code.replace("{YYYY}", str(year))
    code = code.replace("{YY}", str(year)[-2:])
    code = code.replace("{SEQ3}", f"{sequence:03d}")
    code = code.replace("{SEQ4}", f"{sequence:04d}")
    code = code.replace("{SEQ5}", f"{sequence:05d}")
    
    return code


@frappe.whitelist()
def migrate_countries_to_master():
    """Migrate countries from Country Configuration to Country Master."""
    settings = frappe.get_single("Module Settings")
    
    if not settings.country_configuration:
        return {"count": 0, "message": "No countries to migrate"}
    
    migrated = 0
    
    for country in settings.country_configuration:
        # Check if already exists
        exists = frappe.db.exists("Country Master", country.country_code)
        
        if not exists:
            # Create Country Master record
            country_doc = frappe.get_doc({
                "doctype": "Country Master",
                "iso_code": country.country_code,
                "country_name": country.country_name,
                "status": "Active"
            })
            country_doc.insert(ignore_permissions=True)
            migrated += 1
    
    return {
        "count": migrated,
        "message": f"Migrated {migrated} countries to Country Master"
    }
