// Copyright (c) 2026, Mustafa Nazier and contributors
// For license information, please see license.txt

frappe.ui.form.on('IGA Membership Application', {
	onload: function (frm) {
		set_nationality_options(frm);
	},
	refresh: function (frm) {
		set_nationality_options(frm);
		// Add custom button to create customer
		if (!frm.is_new() && frm.doc.email) {
			frm.add_custom_button(__('Create/Update Customer'), function () {
				frappe.call({
					method: 'iga.international_grading_agency.doctype.iga_membership_application.iga_membership_application.create_customer_from_membership',
					args: {
						membership_name: frm.doc.name
					},
					callback: function (r) {
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

		// Add validation for top 3 priorities checkboxes
		validate_top_3_priorities(frm);
	},


	email: function (frm) {
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

	date_of_birth: function (frm) {
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

function set_nationality_options(frm) {
	frappe.db.get_doc('Module Settings', 'Module Settings').then(settings => {
		if (settings && settings.country_configuration) {
			let countries = settings.country_configuration
				.filter(c => c.enabled)
				.map(c => c.country_name);

			// Add an empty option at the beginning
			countries.unshift("");

			frm.set_df_property('nationality', 'options', countries);
			frm.refresh_field('nationality');
		}
	});
}

// Validation helper for top 3 priorities
function validate_top_3_priorities(frm) {
	const priority_fields = [
		'priority_price', 'priority_speed', 'priority_accuracy',
		'priority_holder_quality', 'priority_professional_photos',
		'priority_easy_delivery', 'priority_customer_service',
		'priority_market_acceptance', 'priority_online_verification', 'priority_warranty'
	];

	let count = 0;
	priority_fields.forEach(field => {
		if (frm.doc[field]) count++;
	});

	if (count > 3) {
		frappe.msgprint({
			title: __('Validation Error'),
			message: __('You can select a maximum of 3 priorities. Please uncheck {0} option(s).', [count - 3]),
			indicator: 'red'
		});
	}
}

// Add change handlers for all priority checkboxes
[
	'priority_price', 'priority_speed', 'priority_accuracy',
	'priority_holder_quality', 'priority_professional_photos',
	'priority_easy_delivery', 'priority_customer_service',
	'priority_market_acceptance', 'priority_online_verification', 'priority_warranty'
].forEach(field => {
	frappe.ui.form.on('IGA Membership Application', field, function (frm) {
		validate_top_3_priorities(frm);
	});
});
