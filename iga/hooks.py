app_name = "iga"
app_title = "International Grading Agency"
app_publisher = "Mustafa Nazier"
app_description = "a frappe application that outlines the complete development plan for Phase 1 of the International Grading Agency (IGA) grading and certification system. The project will deliver a production-ready, audit-compliant platform built on ERPNext as the operational backbone, with a secure API integration layer connecting to a public-facing website."
app_email = "mustafanazieer@gmail.com"
app_license = "mit"

# Apps
# ------------------

# required_apps = []

# Each item in the list will be shown as an app in the apps page
# add_to_apps_screen = [
# 	{
# 		"name": "iga",
# 		"logo": "/assets/iga/logo.png",
# 		"title": "International Grading Agency",
# 		"route": "/iga",
# 		"has_permission": "iga.api.permission.has_app_permission"
# 	}
# ]

# Includes in <head>
# ------------------

# include js, css files in header of desk.html
# app_include_css = "/assets/iga/css/iga.css"
# app_include_js = "/assets/iga/js/iga.js"

# include js, css files in header of web template
# web_include_css = "/assets/iga/css/iga.css"
# web_include_js = "/assets/iga/js/iga.js"

# include custom scss in every website theme (without file extension ".scss")
# website_theme_scss = "iga/public/scss/website"

# include js, css files in header of web form
webform_include_js = {
	"iga-membership-application-form": "iga/public/js/iga_membership_webform.js",
	"IGA Membership Application": "iga/public/js/iga_membership_webform.js"
}
webform_include_css = {
	"iga-membership-application-form": "iga/public/css/webform_rtl.css",
	"IGA Membership Application": "iga/public/css/webform_rtl.css"
}

# include js in page
# page_js = {"page" : "public/js/file.js"}

# include js in doctype views
# doctype_js = {"doctype" : "public/js/doctype.js"}
# doctype_list_js = {"doctype" : "public/js/doctype_list.js"}
# doctype_tree_js = {"doctype" : "public/js/doctype_tree.js"}
# doctype_calendar_js = {"doctype" : "public/js/doctype_calendar.js"}

# Svg Icons
# ------------------
# include app icons in desk
# app_include_icons = "iga/public/icons.svg"

# Home Pages
# ----------

# application home page (will override Website Settings)
# home_page = "login"

# website user home page (by Role)
# role_home_page = {
# 	"Role": "home_page"
# }

# Generators
# ----------

# automatically create page for each record of this doctype
# website_generators = ["Web Page"]

# Jinja
# ----------

# add methods and filters to jinja environment
# jinja = {
# 	"methods": "iga.utils.jinja_methods",
# 	"filters": "iga.utils.jinja_filters"
# }

# Installation
# ------------

# before_install = "iga.install.before_install"
# after_install = "iga.install.after_install"

# Uninstallation
# ------------

# before_uninstall = "iga.uninstall.before_uninstall"
# after_uninstall = "iga.uninstall.after_uninstall"

# Integration Setup
# ------------------
# To set up dependencies/integrations with other apps
# Name of the app being installed is passed as an argument

# before_app_install = "iga.utils.before_app_install"
# after_app_install = "iga.utils.after_app_install"

# Integration Cleanup
# -------------------
# To clean up dependencies/integrations with other apps
# Name of the app being uninstalled is passed as an argument

# before_app_uninstall = "iga.utils.before_app_uninstall"
# after_app_uninstall = "iga.utils.after_app_uninstall"

# Desk Notifications
# ------------------
# See frappe.core.notifications.get_notification_config

# notification_config = "iga.notifications.get_notification_config"

# Permissions
# -----------
# Permissions evaluated in scripted ways

# permission_query_conditions = {
# 	"Event": "frappe.desk.doctype.event.event.get_permission_query_conditions",
# }
#
# has_permission = {
# 	"Event": "frappe.desk.doctype.event.event.has_permission",
# }

# DocType Class
# ---------------
# Override standard doctype classes

# override_doctype_class = {
# 	"ToDo": "custom_app.overrides.CustomToDo"
# }

# Document Events
# ---------------
# Hook on document methods and events

# doc_events = {
# 	"*": {
# 		"on_update": "method",
# 		"on_cancel": "method",
# 		"on_trash": "method"
# 	}
# }

# Scheduled Tasks
# ---------------

# scheduler_events = {
# 	"all": [
# 		"iga.tasks.all"
# 	],
# 	"daily": [
# 		"iga.tasks.daily"
# 	],
# 	"hourly": [
# 		"iga.tasks.hourly"
# 	],
# 	"weekly": [
# 		"iga.tasks.weekly"
# 	],
# 	"monthly": [
# 		"iga.tasks.monthly"
# 	],
# }

# Testing
# -------

# before_tests = "iga.install.before_tests"

# Overriding Methods
# ------------------------------
#
# override_whitelisted_methods = {
# 	"frappe.desk.doctype.event.event.get_events": "iga.event.get_events"
# }
#
# each overriding function accepts a `data` argument;
# generated from the base implementation of the doctype dashboard,
# along with any modifications made in other Frappe apps
# override_doctype_dashboards = {
# 	"Task": "iga.task.get_dashboard_data"
# }

# exempt linked doctypes from being automatically cancelled
#
# auto_cancel_exempted_doctypes = ["Auto Repeat"]

# Ignore links to specified DocTypes when deleting documents
# -----------------------------------------------------------

# ignore_links_on_delete = ["Communication", "ToDo"]

# Website Route Rules
# -------------------
website_route_rules = [
    {"from_route": "/api/v1/<path:remaining>", "to_route": "api_v1_handler"},
]

# Request Events
# ----------------
# before_request = ["iga.utils.before_request"]
# after_request = ["iga.utils.after_request"]

# Job Events
# ----------
# before_job = ["iga.utils.before_job"]
# after_job = ["iga.utils.after_job"]

# User Data Protection
# --------------------

# user_data_fields = [
# 	{
# 		"doctype": "{doctype_1}",
# 		"filter_by": "{filter_by}",
# 		"redact_fields": ["{field_1}", "{field_2}"],
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_2}",
# 		"filter_by": "{filter_by}",
# 		"partial": 1,
# 	},
# 	{
# 		"doctype": "{doctype_3}",
# 		"strict": False,
# 	},
# 	{
# 		"doctype": "{doctype_4}"
# 	}
# ]

# Authentication and authorization
# --------------------------------

# auth_hooks = [
# 	"iga.auth.validate"
# ]

# Custom Fields for native ERPNext DocTypes
custom_fields = {
	"Customer": [
		{
			"fieldname": "iga_username",
			"fieldtype": "Data",
			"label": "Username (IGA)",
			"unique": 1,
			"description": "URL-safe username for registry profile URLs"
		},
		{
			"fieldname": "iga_display_name",
			"fieldtype": "Data",
			"label": "Display Name (EN)"
		},
		{
			"fieldname": "iga_display_name_ar",
			"fieldtype": "Data",
			"label": "Display Name (AR)"
		},
		{
			"fieldname": "iga_is_dealer",
			"fieldtype": "Check",
			"label": "Is Dealer",
			"description": "Independent from membership plan — some manual dealers"
		},
		{
			"fieldname": "iga_avatar_url",
			"fieldtype": "Data",
			"label": "Avatar URL"
		},
		{
			"fieldname": "iga_rewards_balance",
			"fieldtype": "Float",
			"label": "Rewards Balance",
			"default": 0,
			"description": "Denormalized for fast reads"
		},
		{
			"fieldname": "iga_plan_code",
			"fieldtype": "Select",
			"label": "Plan Code",
			"options": "\nSILVER\nGOLD\nDIAMOND\nDEALER",
			"description": "Denormalized from active Subscription"
		},
		{
			"fieldname": "iga_plan_status",
			"fieldtype": "Select",
			"label": "Plan Status",
			"options": "\nActive\nInactive\nPending\nExpired\nGrace\nCancelled",
			"description": "Denormalized from active Subscription"
		}
	],
	"Issue": [
		{
			"fieldname": "iga_ticket_type",
			"fieldtype": "Select",
			"label": "Ticket Type (IGA)",
			"options": "\nGeneral\nOffer\nReport Certificate\nGuarantee Claim"
		},
		{
			"fieldname": "iga_guest_name",
			"fieldtype": "Data",
			"label": "Guest Name",
			"description": "For unauthenticated contact-form submissions"
		},
		{
			"fieldname": "iga_guest_email",
			"fieldtype": "Data",
			"label": "Guest Email",
			"options": "Email"
		},
		{
			"fieldname": "iga_guest_phone",
			"fieldtype": "Data",
			"label": "Guest Phone"
		},
		{
			"fieldname": "iga_related_certificate",
			"fieldtype": "Data",
			"label": "Related Certificate"
		},
		{
			"fieldname": "iga_related_submission",
			"fieldtype": "Link",
			"label": "Related Submission",
			"options": "Submission"
		}
	],
	"Sales Invoice": [
		{
			"fieldname": "iga_submission",
			"fieldtype": "Link",
			"label": "IGA Submission",
			"options": "Submission"
		},
		{
			"fieldname": "iga_tracking_id",
			"fieldtype": "Data",
			"label": "Tracking ID"
		},
		{
			"fieldname": "iga_invoice_type",
			"fieldtype": "Select",
			"label": "IGA Invoice Type",
			"options": "\nProforma Invoice\nSales Invoice\nMembership Sales Invoice"
		}
	]
}

# Automatically update python controller files with type annotations for this app.
# export_python_type_annotations = True

# default_log_clearing_doctypes = {
# 	"Logging DocType Name": 30  # days to retain logs
# }

# Translation
# ------------
# List of apps whose translatable strings should be excluded from this app's translations.
# ignore_translatable_strings_from = []

