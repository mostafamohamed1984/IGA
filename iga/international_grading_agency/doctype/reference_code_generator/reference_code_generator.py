# Copyright (c) 2026, IGA and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class ReferenceCodeGenerator(Document):
	def before_save(self):
		# Auto-generate generator_key from type-country-year
		if not self.generator_key:
			type_code = self.collectible_type[:2].upper() if self.collectible_type else "XX"
			self.generator_key = f"{type_code}-{self.country_code}-{self.year}"


@frappe.whitelist()
def generate_next_code(collectible_type, country_code, year, variant=None):
	"""
	Generate next reference code with sequence locking
	
	Args:
		collectible_type: Type of collectible (Coin, Medal, etc.)
		country_code: 3-letter ISO country code
		year: Year (AD)
		variant: Optional variant suffix (.1, .2, etc.)
	
	Returns:
		str: Generated reference code (e.g., CO-EGY-1952-047 or CO-EGY-1952-047.1)
	"""
	# Create generator key
	type_code = collectible_type[:2].upper() if collectible_type else "XX"
	gen_key = f"{type_code}-{country_code}-{year}"
	
	# Get or create generator record
	if not frappe.db.exists("Reference Code Generator", gen_key):
		gen = frappe.get_doc({
			"doctype": "Reference Code Generator",
			"generator_key": gen_key,
			"collectible_type": collectible_type,
			"country_code": country_code,
			"year": year,
			"last_sequence": 0
		})
		gen.insert(ignore_permissions=True)
		frappe.db.commit()
	
	# Increment sequence with database lock to prevent duplicates
	frappe.db.sql("""
		UPDATE `tabReference Code Generator`
		SET last_sequence = last_sequence + 1
		WHERE name = %s
	""", gen_key)
	frappe.db.commit()
	
	# Get new sequence number
	new_seq = frappe.db.get_value("Reference Code Generator", gen_key, "last_sequence")
	
	# Format code: TYPE-CTY-YYYY-SEQ3
	code = f"{type_code}-{country_code}-{year}-{str(new_seq).zfill(3)}"
	
	# Add variant suffix if provided
	if variant:
		code += f".{variant}"
	
	return code
