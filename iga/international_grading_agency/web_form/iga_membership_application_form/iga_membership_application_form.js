// Copyright (c) 2026, Mustafa Nazier and contributors
// For license information, please see license.txt

frappe.ready(function() {
	// Validate top_3_priorities on change
	frappe.web_form.on('top_3_priorities', function(field, value) {
		if (value) {
			let selections = value.split(',').filter(s => s.trim());
			if (selections.length > 3) {
				frappe.msgprint({
					title: __('تحذير'),
					message: __('يمكنك اختيار 3 أولويات كحد أقصى'),
					indicator: 'red'
				});
				// Keep only first 3
				frappe.web_form.set_value('top_3_priorities', selections.slice(0, 3).join(', '));
			}
		}
	});
});
