frappe.ui.form.on('Designation Master', {
	refresh: function(frm) {
		// Status indicator
		if (frm.doc.status === 'Retired') {
			frm.dashboard.add_indicator(__('Retired - Not available for new submissions'), 'red');
		}
		
		// Crosswalk indicators
		if (frm.doc.ngc_equivalent) {
			frm.dashboard.add_indicator(__('NGC: {0}', [frm.doc.ngc_equivalent]), 'blue');
		}
		if (frm.doc.pcgs_equivalent) {
			frm.dashboard.add_indicator(__('PCGS: {0}', [frm.doc.pcgs_equivalent]), 'orange');
		}
		
		// Add button to view usage
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Usage'), function() {
				frappe.route_options = {
					'designation': frm.doc.name
				};
				frappe.set_route('List', 'Submission Item');
			});
		}
	},
	
	designation_code: function(frm) {
		// Auto-uppercase designation codes
		if (frm.doc.designation_code) {
			frm.set_value('designation_code', frm.doc.designation_code.toUpperCase());
		}
	}
});
