// Copyright (c) 2026, Mustafa Nazier and contributors
// For license information, please see license.txt

frappe.ui.form.on('IGA News Article', {
	refresh: function(frm) {
		if (frm.doc.published) {
			frm.dashboard.add_indicator(__('Published'), 'green');
		} else {
			frm.dashboard.add_indicator(__('Draft / Unpublished'), 'orange');
		}
	},
	
	title: function(frm) {
		if (frm.doc.title && !frm.doc.slug) {
			let slug = frm.doc.title
				.toLowerCase()
				.replace(/[^a-z0-9\s-]/g, '')
				.replace(/[\s-]+/g, '-');
			frm.set_value('slug', slug);
		}
	}
});
