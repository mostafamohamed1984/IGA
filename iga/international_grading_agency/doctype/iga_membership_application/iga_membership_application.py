# Copyright (c) 2026, Mustafa Nazier and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
from frappe.utils import today, getdate, add_months, add_days
import re


class IGAMembershipApplication(Document):
	def before_insert(self):
		"""Set valid_from on first creation"""
		if not self.valid_from:
			self.valid_from = today()
	
	def after_insert(self):
		"""Copy doc.name to membership_id after document is created"""
		if not self.membership_id:
			self.membership_id = self.name
			self.db_set("membership_id", self.membership_id, update_modified=False)
	
	def validate(self):
		"""Validate all fields according to Field_Spec requirements"""
		
		# Validate full_name: min length 3, trim spaces
		if self.full_name:
			self.full_name = self.full_name.strip()
			if len(self.full_name) < 3:
				frappe.throw("Full name must be at least 3 characters long")
		
		# Validate date_of_birth: must be <= today
		if self.date_of_birth:
			if getdate(self.date_of_birth) > getdate(today()):
				frappe.throw("Date of birth cannot be in the future")
		
		# Validate phone formats (basic validation)
		if self.mobile_primary:
			self._validate_phone(self.mobile_primary, "Primary Mobile")
		
		if self.mobile_secondary:
			self._validate_phone(self.mobile_secondary, "Secondary Mobile")
		
		# Validate email uniqueness (ERPNext handles this via unique=1, but double-check)
		if self.email and not self.is_new():
			existing = frappe.db.exists(
				"IGA Membership Application",
				{"email": self.email, "name": ["!=", self.name]}
			)
			if existing:
				frappe.throw(f"Email {self.email} is already registered")
		
		# Validate accept_terms must be checked
		if not self.accept_terms:
			frappe.throw("You must accept the Terms and Conditions to proceed")
		
		# Validate collectibles_interest: at least 1 selection required
		interest_fields = ['interest_coins', 'interest_medals_tokens', 'interest_banknotes', 
		                   'interest_postcards', 'interest_other']
		if not any(getattr(self, field, 0) for field in interest_fields):
			frappe.throw("Please select at least one collectible interest")
		
		# Validate choose_iga_reasons: at least 1 selection required
		reason_fields = ['reason_save_time', 'reason_lower_cost', 'reason_arabic_support',
		                 'reason_local_delivery', 'reason_reduce_shipping_risk', 
		                 'reason_fast_certification', 'reason_local_market_acceptance', 'reason_other']
		if not any(getattr(self, field, 0) for field in reason_fields):
			frappe.throw("Please select at least one reason for choosing IGA")
		
		# Validate iga_barriers: at least 1 selection required
		barrier_fields = ['barrier_trust_credibility', 'barrier_market_recognition', 'barrier_accuracy',
		                  'barrier_tamper_protection', 'barrier_price', 'barrier_turnaround_time',
		                  'barrier_warranty_policy', 'barrier_other']
		if not any(getattr(self, field, 0) for field in barrier_fields):
			frappe.throw("Please select at least one potential barrier")
		
		# Validate top_3_priorities: exactly 3 selections required
		priority_fields = ['priority_price', 'priority_speed', 'priority_accuracy', 
		                   'priority_holder_quality', 'priority_professional_photos',
		                   'priority_easy_delivery', 'priority_customer_service',
		                   'priority_market_acceptance', 'priority_online_verification', 'priority_warranty']
		priority_count = sum(1 for field in priority_fields if getattr(self, field, 0))
		if priority_count != 3:
			frappe.throw(f"Please select exactly 3 priorities (currently selected: {priority_count})")

		
		# Lock valid_from after first save (prevent changes)
		if not self.is_new():
			old_doc = self.get_doc_before_save()
			if old_doc and old_doc.valid_from and self.valid_from != old_doc.valid_from:
				self.valid_from = old_doc.valid_from
		
		# Auto-calculate valid_thru: valid_from + 12 months - 1 day
		if self.valid_from:
			self.valid_thru = add_days(add_months(getdate(self.valid_from), 12), -1)
	
	def _validate_phone(self, phone, field_label):
		"""Basic phone validation - remove spaces and check if it contains digits"""
		cleaned = re.sub(r'[\s\-\(\)]', '', phone)
		if not re.match(r'^\+?\d{10,15}$', cleaned):
			frappe.throw(f"{field_label} must be a valid phone number (10-15 digits)")


@frappe.whitelist()
def create_customer_from_membership(membership_name):
	"""
	Create or update Customer, Contact, and Address from membership application
	
	Args:
		membership_name: Name of the IGA Membership Application document
	
	Returns:
		dict: Success message and created customer name
	"""
	# Get membership application
	membership = frappe.get_doc("IGA Membership Application", membership_name)
	
	# Check if customer already exists by email
	existing_customer = frappe.db.get_value(
		"Contact",
		{"email_id": membership.email},
		"name"
	)
	
	if existing_customer:
		# Get linked customer
		contact_doc = frappe.get_doc("Contact", existing_customer)
		if contact_doc.links:
			customer_name = contact_doc.links[0].link_name
			customer = frappe.get_doc("Customer", customer_name)
			
			# Update existing customer
			customer.customer_name = membership.full_name
			customer.mobile_no = membership.mobile_primary
			customer.save(ignore_permissions=True)
			
			return {
				"success": True,
				"message": f"Customer {customer_name} updated successfully",
				"customer_name": customer_name,
				"is_new": False
			}
	
	# Create new customer
	customer = frappe.get_doc({
		"doctype": "Customer",
		"customer_name": membership.full_name,
		"customer_type": "Individual",
		"customer_group": "Individual",
		"territory": "All Territories"
	})
	customer.insert(ignore_permissions=True)
	
	# Create contact
	contact = frappe.get_doc({
		"doctype": "Contact",
		"first_name": membership.full_name,
		"email_id": membership.email,
		"mobile_no": membership.mobile_primary,
		"phone": membership.mobile_secondary if hasattr(membership, 'mobile_secondary') else None,
		"links": [{
			"link_doctype": "Customer",
			"link_name": customer.name
		}]
	})
	contact.insert(ignore_permissions=True)
	
	# Create address if provided
	if membership.address_text:
		address = frappe.get_doc({
			"doctype": "Address",
			"address_title": membership.full_name,
			"address_line1": membership.address_text[:140],  # Limit to field size
			"address_type": "Billing",
			"country": "Egypt",  # Default
			"links": [{
				"link_doctype": "Customer",
				"link_name": customer.name
			}]
		})
		address.insert(ignore_permissions=True)
	
	frappe.db.commit()
	
	return {
		"success": True,
		"message": f"Customer {customer.name} created successfully",
		"customer_name": customer.name,
		"is_new": True
	}
