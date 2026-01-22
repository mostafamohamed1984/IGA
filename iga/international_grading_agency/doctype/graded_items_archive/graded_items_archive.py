# Copyright (c) 2026, IGA and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document
import re


class GradedItemsArchive(Document):
	def validate(self):
		"""Validate grade and extract numeric value"""
		
		# Extract numeric from grade_full
		if self.grade_full:
			match = re.search(r'\d+', self.grade_full)
			if match:
				self.grade_numeric = int(match.group())
		
		# Validate grade exists in Module Settings
		if self.grade_full:
			grade_exists = frappe.db.exists(
				"Grade Scoring Configuration",
				{"parent": "Module Settings", "grade_full": self.grade_full}
			)
			if not grade_exists:
				frappe.throw(f"Grade '{self.grade_full}' not found in Module Settings. Please add it first.")
