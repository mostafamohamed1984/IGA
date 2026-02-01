# Copyright (c) 2026, Mustafa Nazier and Contributors
# See license.txt

import frappe
from frappe.tests.utils import FrappeTestCase
from frappe.utils import today, getdate, add_months, add_days


class TestIGAMembershipApplication(FrappeTestCase):
	def setUp(self):
		"""Set up test data"""
		# Clean up any existing test data
		frappe.db.delete("IGA Membership Application", {"email": "test@example.com"})
		frappe.db.commit()
	
	def test_membership_creation(self):
		"""Test basic membership application creation"""
		membership = frappe.get_doc({
			"doctype": "IGA Membership Application",
			"membership_tier": "Silver",
			"full_name": "Test User",
			"mobile_primary": "+201234567890",
			"email": "test@example.com",
			"preferred_contact_method": "واتساب",
			"accept_terms": 1,
			"user_profile_type": "هاوي مبتدئ",
			"collectibles_interest": "عملات",
			"expected_items_first_3_months": "1–5",
			"acceptable_grading_price_range": "أقل من 399",
			"used_foreign_graders_before": "لا",
			"choose_iga_reasons": "تكلفة أقل",
			"iga_barriers": "السعر",
			"top_3_priorities": "السعر, السرعة, الدقة"
		})
		membership.insert()
		
		# Verify naming series
		self.assertTrue(membership.name.startswith("26-"))
		
		# Verify membership_id is set
		self.assertEqual(membership.membership_id, membership.name)
		
		# Verify valid_from is today
		self.assertEqual(membership.valid_from, today())
		
		# Verify valid_thru is 12 months - 1 day
		expected_thru = add_days(add_months(getdate(membership.valid_from), 12), -1)
		self.assertEqual(membership.valid_thru, expected_thru)
	
	def test_full_name_validation(self):
		"""Test full name must be at least 3 characters"""
		membership = frappe.get_doc({
			"doctype": "IGA Membership Application",
			"membership_tier": "Silver",
			"full_name": "AB",  # Too short
			"mobile_primary": "+201234567890",
			"email": "test2@example.com",
			"preferred_contact_method": "واتساب",
			"accept_terms": 1,
			"user_profile_type": "هاوي مبتدئ",
			"collectibles_interest": "عملات",
			"expected_items_first_3_months": "1–5",
			"acceptable_grading_price_range": "أقل من 399",
			"used_foreign_graders_before": "لا",
			"choose_iga_reasons": "تكلفة أقل",
			"iga_barriers": "السعر",
			"top_3_priorities": "السعر"
		})
		
		with self.assertRaises(frappe.ValidationError):
			membership.insert()
	
	def test_date_of_birth_validation(self):
		"""Test date of birth cannot be in future"""
		membership = frappe.get_doc({
			"doctype": "IGA Membership Application",
			"membership_tier": "Silver",
			"full_name": "Test User",
			"date_of_birth": add_days(today(), 1),  # Future date
			"mobile_primary": "+201234567890",
			"email": "test3@example.com",
			"preferred_contact_method": "واتساب",
			"accept_terms": 1,
			"user_profile_type": "هاوي مبتدئ",
			"collectibles_interest": "عملات",
			"expected_items_first_3_months": "1–5",
			"acceptable_grading_price_range": "أقل من 399",
			"used_foreign_graders_before": "لا",
			"choose_iga_reasons": "تكلفة أقل",
			"iga_barriers": "السعر",
			"top_3_priorities": "السعر"
		})
		
		with self.assertRaises(frappe.ValidationError):
			membership.insert()
	
	def test_email_uniqueness(self):
		"""Test email must be unique"""
		# Create first membership
		membership1 = frappe.get_doc({
			"doctype": "IGA Membership Application",
			"membership_tier": "Silver",
			"full_name": "Test User 1",
			"mobile_primary": "+201234567890",
			"email": "unique@example.com",
			"preferred_contact_method": "واتساب",
			"accept_terms": 1,
			"user_profile_type": "هاوي مبتدئ",
			"collectibles_interest": "عملات",
			"expected_items_first_3_months": "1–5",
			"acceptable_grading_price_range": "أقل من 399",
			"used_foreign_graders_before": "لا",
			"choose_iga_reasons": "تكلفة أقل",
			"iga_barriers": "السعر",
			"top_3_priorities": "السعر"
		})
		membership1.insert()
		
		# Try to create second with same email
		membership2 = frappe.get_doc({
			"doctype": "IGA Membership Application",
			"membership_tier": "Gold",
			"full_name": "Test User 2",
			"mobile_primary": "+201234567891",
			"email": "unique@example.com",  # Duplicate
			"preferred_contact_method": "واتساب",
			"accept_terms": 1,
			"user_profile_type": "هاوي مبتدئ",
			"collectibles_interest": "عملات",
			"expected_items_first_3_months": "1–5",
			"acceptable_grading_price_range": "أقل من 399",
			"used_foreign_graders_before": "لا",
			"choose_iga_reasons": "تكلفة أقل",
			"iga_barriers": "السعر",
			"top_3_priorities": "السعر"
		})
		
		with self.assertRaises(frappe.DuplicateEntryError):
			membership2.insert()
	
	def test_accept_terms_required(self):
		"""Test accept_terms must be checked"""
		membership = frappe.get_doc({
			"doctype": "IGA Membership Application",
			"membership_tier": "Silver",
			"full_name": "Test User",
			"mobile_primary": "+201234567890",
			"email": "test4@example.com",
			"preferred_contact_method": "واتساب",
			"accept_terms": 0,  # Not accepted
			"user_profile_type": "هاوي مبتدئ",
			"collectibles_interest": "عملات",
			"expected_items_first_3_months": "1–5",
			"acceptable_grading_price_range": "أقل من 399",
			"used_foreign_graders_before": "لا",
			"choose_iga_reasons": "تكلفة أقل",
			"iga_barriers": "السعر",
			"top_3_priorities": "السعر"
		})
		
		with self.assertRaises(frappe.ValidationError):
			membership.insert()
	
	def test_top_3_priorities_max_3(self):
		"""Test top_3_priorities allows max 3 selections"""
		membership = frappe.get_doc({
			"doctype": "IGA Membership Application",
			"membership_tier": "Silver",
			"full_name": "Test User",
			"mobile_primary": "+201234567890",
			"email": "test5@example.com",
			"preferred_contact_method": "واتساب",
			"accept_terms": 1,
			"user_profile_type": "هاوي مبتدئ",
			"collectibles_interest": "عملات",
			"expected_items_first_3_months": "1–5",
			"acceptable_grading_price_range": "أقل من 399",
			"used_foreign_graders_before": "لا",
			"choose_iga_reasons": "تكلفة أقل",
			"iga_barriers": "السعر",
			"top_3_priorities": "السعر, السرعة, الدقة, جودة خامات الحفظات"  # 4 selections
		})
		
		with self.assertRaises(frappe.ValidationError):
			membership.insert()
	
	def test_valid_from_lock(self):
		"""Test valid_from cannot be changed after creation"""
		membership = frappe.get_doc({
			"doctype": "IGA Membership Application",
			"membership_tier": "Silver",
			"full_name": "Test User",
			"mobile_primary": "+201234567890",
			"email": "test6@example.com",
			"preferred_contact_method": "واتساب",
			"accept_terms": 1,
			"user_profile_type": "هاوي مبتدئ",
			"collectibles_interest": "عملات",
			"expected_items_first_3_months": "1–5",
			"acceptable_grading_price_range": "أقل من 399",
			"used_foreign_graders_before": "لا",
			"choose_iga_reasons": "تكلفة أقل",
			"iga_barriers": "السعر",
			"top_3_priorities": "السعر"
		})
		membership.insert()
		
		original_valid_from = membership.valid_from
		
		# Try to change valid_from
		membership.valid_from = add_days(today(), -10)
		membership.save()
		
		# Should be reverted to original
		self.assertEqual(membership.valid_from, original_valid_from)
	
	def tearDown(self):
		"""Clean up test data"""
		frappe.db.delete("IGA Membership Application", {"email": ["like", "test%@example.com"]})
		frappe.db.delete("IGA Membership Application", {"email": "unique@example.com"})
		frappe.db.commit()
