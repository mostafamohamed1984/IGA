# Copyright (c) 2026, IGA and contributors
# For license information, please see license.txt

import frappe


def execute(filters=None):
	"""
	Population Report - Aggregates graded items by reference and grade
	Only counts items with status = 'Shipped'
	"""
	columns = get_columns()
	data = get_data(filters)
	
	return columns, data


def get_columns():
	"""Define report columns"""
	return [
		{
			"label": "Reference Code",
			"fieldname": "ref_code",
			"fieldtype": "Link",
			"options": "Item Reference Catalog",
			"width": 150
		},
		{
			"label": "Title",
			"fieldname": "title",
			"fieldtype": "Data",
			"width": 250
		},
		{
			"label": "Type",
			"fieldname": "collectible_type",
			"fieldtype": "Data",
			"width": 120
		},
		{
			"label": "Country",
			"fieldname": "country",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": "Year",
			"fieldname": "year_ad",
			"fieldtype": "Int",
			"width": 80
		},
		{
			"label": "Grade",
			"fieldname": "grade_full",
			"fieldtype": "Data",
			"width": 100
		},
		{
			"label": "Population",
			"fieldname": "population",
			"fieldtype": "Int",
			"width": 100
		},
		{
			"label": "First Graded",
			"fieldname": "first_graded",
			"fieldtype": "Date",
			"width": 100
		},
		{
			"label": "Last Graded",
			"fieldname": "last_graded",
			"fieldtype": "Date",
			"width": 100
		}
	]


def get_data(filters):
	"""Get population data from Graded Items Archive"""
	
	conditions = "WHERE gia.status = 'Shipped'"
	
	# Add filters
	if filters.get("reference_item"):
		conditions += f" AND gia.reference_item = '{filters.get('reference_item')}'"
	
	if filters.get("collectible_type"):
		conditions += f" AND irc.collectible_type = '{filters.get('collectible_type')}'"
	
	if filters.get("country"):
		conditions += f" AND irc.country LIKE '%{filters.get('country')}%'"
	
	if filters.get("from_date"):
		conditions += f" AND gia.shipped_date >= '{filters.get('from_date')}'"
	
	if filters.get("to_date"):
		conditions += f" AND gia.shipped_date <= '{filters.get('to_date')}'"
	
	# Query to aggregate population
	data = frappe.db.sql(f"""
		SELECT 
			irc.ref_code,
			irc.title,
			irc.collectible_type,
			irc.country,
			irc.year_ad,
			gia.grade_full,
			COUNT(*) as population,
			MIN(gia.shipped_date) as first_graded,
			MAX(gia.shipped_date) as last_graded
		FROM `tabGraded Items Archive` gia
		INNER JOIN `tabItem Reference Catalog` irc 
			ON gia.reference_item = irc.name
		{conditions}
		GROUP BY gia.reference_item, gia.grade_full
		ORDER BY irc.ref_code, gia.grade_numeric DESC
	""", as_dict=1)
	
	return data
