// Copyright (c) 2026, Mustafa Nazier and contributors
// For license information, please see license.txt

frappe.ui.form.on('IGA Promo Code', {
	refresh: function(frm) {
		if (frm.doc.expires_at) {
			let expires = frappe.datetime.str_to_obj(frm.doc.expires_at);
			let today = new Date();
			today.setHours(0, 0, 0, 0);
			if (expires < today) {
				frm.dashboard.add_indicator(__('Expired'), 'red');
			}
		}
		
		if (!frm.doc.active) {
			frm.dashboard.add_indicator(__('Inactive'), 'red');
		} else if (frm.doc.usage_limit && frm.doc.usage_count >= frm.doc.usage_limit) {
			frm.dashboard.add_indicator(__('Limit Reached'), 'red');
		} else {
			frm.dashboard.add_indicator(__('Active'), 'green');
		}
	},
	
	value: function(frm) {
		if (frm.doc.type === 'percent' && frm.doc.value > 100) {
			frappe.msgprint(__('Percent discount cannot exceed 100%'));
			frm.set_value('value', 100);
		}
	}
});
