# Copyright (c) 2026, IGA and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from iga.international_grading_agency.doctype.reference_code_generator.reference_code_generator import generate_next_code


class ItemReferenceCatalog(Document):
	def before_insert(self):
		"""Set default status to Draft on new document creation"""
		if not self.status:
			self.status = "Draft"
		
		# Set last_verified to current date on creation
		self.last_verified = frappe.utils.today()
	
	def validate(self):
		"""Validate mandatory fields and auto-update status based on completeness"""
		
		# Update last_verified on every save
		self.last_verified = frappe.utils.today()
		
		# Auto-update status based on mandatory field completeness
		if self.status != "Deprecated":  # Don't auto-change if already deprecated
			if self._are_mandatory_fields_complete():
				self.status = "Active"
			else:
				self.status = "Draft"
		
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
		
		# Prevent ref_code changes when status is Active (check before save)
		if not self.is_new() and self.status == "Active":
			old_doc = self.get_doc_before_save()
			if old_doc and old_doc.ref_code and self.ref_code != old_doc.ref_code:
				frappe.throw("Reference Code cannot be changed once the status is Active")
		
		# Generate reference code when status changes to Active
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
			if not self.bn_denomination_value:
				frappe.throw("Denomination Value is mandatory for Banknotes")
			if not self.bn_denomination_unit:
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
			if not self.cc_year:
				frappe.throw("Year is mandatory for Collectible Cards")
	
	def _are_mandatory_fields_complete(self):
		"""Check if all mandatory fields are filled based on collectible type"""
		
		# Check MASTER section mandatory fields
		if not all([self.title, self.collectible_type, self.country, self.calendar_type]):
			return False
		
		# Check calendar type mandatory fields
		if self.calendar_type in ["AD", "Both"] and not self.year_ad:
			return False
		
		if self.calendar_type in ["AH", "Both"] and not self.year_ah:
			return False
		
		# Check collectible type specific mandatory fields
		if self.collectible_type == "Coin":
			if not all([self.denomination_value, self.denomination_unit, self.metal]):
				return False
		
		elif self.collectible_type in ["Token", "Medal"]:
			if not self.metal:
				return False
		
		elif self.collectible_type == "Banknote":
			if not all([self.bn_denomination_value, self.bn_denomination_unit]):
				return False
		
		elif self.collectible_type == "Postcard":
			if not all([self.publisher, self.location, self.used_unused]):
				return False
		
		elif self.collectible_type == "Collectible Card":
			if not all([self.card_brand, self.set_name, self.card_number, self.cc_year]):
				return False
		
		return True


@frappe.whitelist()
def archive_reference_item(docname, deprecated_reason):
	"""
	Archive an Item Reference Catalog by:
	1. Setting status to Deprecated
	2. Creating a Graded Items Archive record with the same data
	
	Args:
		docname: Name of the Item Reference Catalog document
		deprecated_reason: Reason for deprecation
	
	Returns:
		dict: Success message and created archive document name
	"""
	# Get the reference item
	ref_item = frappe.get_doc("Item Reference Catalog", docname)
	
	# Check if already deprecated
	if ref_item.status == "Deprecated":
		frappe.throw("This item is already deprecated")
	
	# Check if status is Active
	if ref_item.status != "Active":
		frappe.throw("Only Active items can be archived")
	
	# Validate deprecated reason
	if not deprecated_reason or not deprecated_reason.strip():
		frappe.throw("Deprecation reason is required")
	
	# Create Graded Items Archive record
	archive_doc = frappe.get_doc({
		"doctype": "Graded Items Archive",
		"reference_item": ref_item.name,
		"grade_full": "UNC Details",  # Default grade for archived reference items
		"grading_date": frappe.utils.today(),
		"status": "Graded",
		"notes": f"Archived from Item Reference Catalog. Reason: {deprecated_reason}",
		"item_images": ref_item.front_image or ref_item.back_image
	})
	archive_doc.insert(ignore_permissions=True)
	
	# Update reference item status to Deprecated
	ref_item.status = "Deprecated"
	ref_item.deprecated_reason = deprecated_reason
	ref_item.flags.ignore_validate = True  # Skip validation to allow manual status change
	ref_item.save(ignore_permissions=True)
	
	frappe.db.commit()
	
	return {
		"success": True,
		"message": f"Item archived successfully. Archive ID: {archive_doc.name}",
		"archive_name": archive_doc.name
	}
