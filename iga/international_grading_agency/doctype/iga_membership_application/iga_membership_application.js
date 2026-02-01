// Copyright (c) 2026, Mustafa Nazier and contributors
// For license information, please see license.txt

frappe.ui.form.on('IGA Membership Application', {
	refresh: function(frm) {
		// Add custom button to create customer
		if (!frm.is_new() && frm.doc.email) {
			frm.add_custom_button(__('Create/Update Customer'), function() {
				frappe.call({
					method: 'iga.international_grading_agency.doctype.iga_membership_application.iga_membership_application.create_customer_from_membership',
					args: {
						membership_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message && r.message.success) {
							frappe.msgprint({
								title: __('Success'),
								message: r.message.message,
								indicator: 'green'
							});
						}
					}
				});
			});
		}
	},
	
	top_3_priorities: function(frm) {
		// Validate max 3 selections for top_3_priorities
		if (frm.doc.top_3_priorities) {
			let selections = frm.doc.top_3_priorities.split(',').filter(s => s.trim());
			if (selections.length > 3) {
				frappe.msgprint({
					title: __('Validation Error'),
					message: __('You can select a maximum of 3 priorities. Please remove {0} selection(s).', [selections.length - 3]),
					indicator: 'red'
				});
				
				// Keep only first 3 selections
				frm.set_value('top_3_priorities', selections.slice(0, 3).join(', '));
			}
		}
	},
	
	email: function(frm) {
		// Validate email format
		if (frm.doc.email && !frappe.utils.validate_type(frm.doc.email, 'email')) {
			frappe.msgprint({
				title: __('Invalid Email'),
				message: __('Please enter a valid email address'),
				indicator: 'red'
			});
			frm.set_value('email', '');
		}
	},
	
	date_of_birth: function(frm) {
		// Validate date of birth is not in future
		if (frm.doc.date_of_birth) {
			let dob = frappe.datetime.str_to_obj(frm.doc.date_of_birth);
			let today = frappe.datetime.now_date(true);
			
			if (dob > today) {
				frappe.msgprint({
					title: __('Invalid Date'),
					message: __('Date of birth cannot be in the future'),
					indicator: 'red'
				});
				frm.set_value('date_of_birth', '');
			}
		}
	}
});
