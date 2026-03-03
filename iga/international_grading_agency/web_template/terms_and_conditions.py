# Copyright (c) 2026, IGA and contributors
# For license information, please see license.txt

import frappe

def get_context(context):
	"""Context for Terms and Conditions page"""
	context.no_cache = 0
	context.show_sidebar = False
	
	# Set page metadata
	context.title = "الشروط والأحكام الخاصة بالعضويات"
	context.description = "شروط وأحكام عضويات شركة أي جي أيه لخدمات التقييم الفني"
	
	return context
