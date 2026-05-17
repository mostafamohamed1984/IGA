frappe.ui.form.on('Problem Definitions', {
	refresh: function(frm) {
		// Status indicator
		if (frm.doc.status === 'Retired') {
			frm.dashboard.add_indicator(__('Retired - Not available for new submissions'), 'red');
		}
		
		// Severity indicator
		if (frm.doc.severity) {
			let color = {
				'Minor': 'green',
				'Moderate': 'orange',
				'Major': 'red',
				'Disqualifying': 'darkred'
			}[frm.doc.severity] || 'grey';
			frm.dashboard.add_indicator(__('Severity: {0}', [frm.doc.severity]), color);
		}
		
		// No-grade indicator
		if (frm.doc.results_in_no_grade) {
			frm.dashboard.add_indicator(__('Results in No Numeric Grade'), 'red');
		}
		
		// Add button to view usage
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Usage'), function() {
				frappe.route_options = {
					'problem': frm.doc.name
				};
				frappe.set_route('List', 'Submission Item');
			});
		}
	},
	
	problem_code: function(frm) {
		// Auto-uppercase problem codes
		if (frm.doc.problem_code) {
			frm.set_value('problem_code', frm.doc.problem_code.toUpperCase());
		}
	},
	
	results_in_no_grade: function(frm) {
		// Warn if enabling no-grade flag
		if (frm.doc.results_in_no_grade) {
			frappe.msgprint({
				title: __('Note'),
				message: __('Items with this problem will receive Result Type = "Details" and no numeric grade will be assigned.'),
				indicator: 'orange'
			});
		}
	}
});
