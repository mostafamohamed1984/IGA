frappe.ui.form.on('Holder Types Master', {
	refresh: function(frm) {
		// Status indicator
		if (frm.doc.status === 'Retired') {
			frm.dashboard.add_indicator(__('Retired - Not available for new submissions'), 'red');
		}
		
		// NFC support indicator
		if (frm.doc.supports_nfc) {
			frm.dashboard.add_indicator(__('NFC Enabled'), 'green');
		} else {
			frm.dashboard.add_indicator(__('No NFC'), 'grey');
		}
		
		// Size range display
		if (frm.doc.min_mm && frm.doc.max_mm) {
			frm.dashboard.add_indicator(__('Size: {0}-{1}mm', [frm.doc.min_mm, frm.doc.max_mm]), 'blue');
		}
		
		// Add button to view usage
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Usage'), function() {
				frappe.route_options = {
					'holder_type': frm.doc.name
				};
				frappe.set_route('List', 'Submission Item');
			});
		}
	},
	
	holder_code: function(frm) {
		// Auto-uppercase holder codes
		if (frm.doc.holder_code) {
			frm.set_value('holder_code', frm.doc.holder_code.toUpperCase());
		}
	},
	
	min_mm: function(frm) {
		// Validate min < max
		if (frm.doc.min_mm && frm.doc.max_mm && frm.doc.min_mm > frm.doc.max_mm) {
			frappe.msgprint(__('Minimum diameter cannot exceed maximum diameter'));
			frm.set_value('min_mm', null);
		}
	},
	
	max_mm: function(frm) {
		// Validate max > min
		if (frm.doc.min_mm && frm.doc.max_mm && frm.doc.max_mm < frm.doc.min_mm) {
			frappe.msgprint(__('Maximum diameter cannot be less than minimum diameter'));
			frm.set_value('max_mm', null);
		}
	}
});
