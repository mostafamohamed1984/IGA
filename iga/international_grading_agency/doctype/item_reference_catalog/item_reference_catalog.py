# Copyright (c) 2026, IGA and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from iga.international_grading_agency.doctype.reference_code_generator.reference_code_generator import generate_next_code


class ItemReferenceCatalog(Document):
	def validate(self):
		"""Validate mandatory fields based on collectible type and calendar type"""
		
		# Validate calendar type mandatory fields
		if self.calendar_type in ["AD", "Both"]:
			if not self.year_ad:
				frappe.throw("Year (AD) is mandatory when Calendar Type is AD or Both")
		
		if self.calendar_type in ["AH", "Both"]:
			if not self.year_ah:
				frappe.throw("Year (AH) is mandatory when Calendar Type is AH or Both")
		
		# Validate deprecated reason
		if self.status == "Deprecated" and not self.deprecated_reason:
			frappe.throw("Deprecated Reason is mandatory when status is Deprecated")
		
		# Validate collectible type specific mandatory fields
		if self.collectible_type == "Coin":
			if not self.denomination_value:
				frappe.throw("Denomination Value is mandatory for Coins")
			if not self.denomination_unit:
				frappe.throw("Denomination Unit is mandatory for Coins")
		
		if self.collectible_type in ["Coin", "Token", "Medal"]:
			if not self.metal:
				frappe.throw("Metal is mandatory for Coins, Tokens, and Medals")
		
		if self.collectible_type == "Banknote":
			if not self.denomination_value:
				frappe.throw("Denomination Value is mandatory for Banknotes")
			if not self.denomination_unit:
				frappe.throw("Denomination Unit is mandatory for Banknotes")
		
		if self.collectible_type == "Postcard":
			if not self.publisher:
				frappe.throw("Publisher is mandatory for Postcards")
			if not self.location:
				frappe.throw("Location is mandatory for Postcards")
			if not self.used_unused:
				frappe.throw("Used/Unused is mandatory for Postcards")
		
		if self.collectible_type == "Collectible Card":
			if not self.card_brand:
				frappe.throw("Card Brand is mandatory for Collectible Cards")
			if not self.set_name:
				frappe.throw("Set Name is mandatory for Collectible Cards")
			if not self.card_number:
				frappe.throw("Card Number is mandatory for Collectible Cards")
			if not self.year:
				frappe.throw("Year is mandatory for Collectible Cards")
	
	def before_save(self):
		"""Generate reference code when status changes to Active"""
		
		# Generate reference code when status becomes Active
		if self.status == "Active" and not self.ref_code:
			# Use year_ad if available, otherwise year_ah, otherwise current year
			year = self.year_ad or self.year_ah or frappe.utils.now_datetime().year
			
			# Extract ISO3 country code (first 3 chars)
			country_code = self.country[:3].upper() if self.country else "XXX"
			
			# Generate the code
			self.ref_code = generate_next_code(
				self.collectible_type,
				country_code,
				year
			)
	
	def on_update(self):
		"""Prevent reference code changes when Active"""
		
		# Lock ref_code when status is Active
		if self.status == "Active" and self.has_value_changed("ref_code"):
			frappe.throw("Reference Code cannot be changed once the status is Active")
