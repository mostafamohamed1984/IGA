frappe.ui.form.on('Mint Error Master', {
	refresh: function(frm) {
		// Status indicator
		if (frm.doc.status === 'Retired') {
			frm.dashboard.add_indicator(__('Retired - Not available for new submissions'), 'red');
		}
		
		// Severity indicator
		if (frm.doc.severity_typical) {
			let color = {
				'Minor': 'green',
				'Moderate': 'orange',
				'Major': 'red'
			}[frm.doc.severity_typical] || 'grey';
			frm.dashboard.add_indicator(__('Severity: {0}', [frm.doc.severity_typical]), color);
		}
		
		// Image preview
		if (frm.doc.image) {
			frm.set_df_property('image', 'description', __('Reference image for graders'));
		}
		
		// Add button to view usage
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Usage'), function() {
				frappe.route_options = {
					'mint_error': frm.doc.name
				};
				frappe.set_route('List', 'Submission Item');
			});
		}
	},
	
	error_code: function(frm) {
		// Auto-uppercase error codes
		if (frm.doc.error_code) {
			frm.set_value('error_code', frm.doc.error_code.toUpperCase());
		}
	}
});
