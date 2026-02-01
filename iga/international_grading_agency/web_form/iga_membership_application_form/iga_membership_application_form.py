# Copyright (c) 2026, Mustafa Nazier and contributors
# For license information, please see license.txt

import frappe

def get_context(context):
	"""Add custom context for web form"""
	context.no_cache = 1
