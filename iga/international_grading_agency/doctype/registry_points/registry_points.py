# Copyright (c) 2026, IGA and contributors
# For license information, please see license.txt

import frappe
from frappe.model.document import Document


class RegistryPoints(Document):
	def before_save(self):
		"""Calculate registry points before saving"""
		self.calculate_points()
	
	def calculate_points(self):
		"""
		Calculate registry points using formula:
		registry_points = (score * grade_weight) + (1/population * population_weight) + (value * value_weight)
		"""
		
		# Get Module Settings
		settings = frappe.get_single("Module Settings")
		
		# Get grade score from Module Settings
		grade_config = frappe.db.get_value(
			"Grade Scoring Configuration",
			{"parent": "Module Settings", "grade_full": self.grade_full},
			"score"
		)
		self.score = grade_config or 0
		
		# Get population from Graded Items Archive (count of Shipped items)
		self.population = frappe.db.count(
			"Graded Items Archive",
			{
				"reference_item": self.reference_item,
				"grade_full": self.grade_full,
				"status": "Shipped"
			}
		)
		
		# Avoid division by zero
		if self.population == 0:
			self.population = 1
		
		# Calculate registry points using formula
		self.registry_points = (
			(self.score * settings.grade_weight) +
			((1 / self.population) * settings.population_weight) +
			((self.value or 0) * settings.value_weight)
		)
		
		# Update last calculated timestamp
		self.last_calculated = frappe.utils.now()
