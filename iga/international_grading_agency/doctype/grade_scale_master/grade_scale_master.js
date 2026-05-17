frappe.ui.form.on('Grade Scale Master', {
	refresh: function(frm) {
		// Validation indicator
		if (frm.doc.numeric_grade < 1 || frm.doc.numeric_grade > 70) {
			frm.dashboard.add_indicator(__('Invalid: Numeric grade must be 1-70'), 'red');
		}
		
		// Display grade type indicators
		if (frm.doc.is_proof) {
			frm.dashboard.add_indicator(__('Proof Grade'), 'blue');
		}
		if (frm.doc.is_circulated) {
			frm.dashboard.add_indicator(__('Circulated Grade'), 'orange');
		}
		
		// Status indicator
		if (frm.doc.status === 'Inactive') {
			frm.dashboard.add_indicator(__('Inactive - Not available for grading'), 'red');
		}
	},
	
	numeric_grade: function(frm) {
		// Validate range
		if (frm.doc.numeric_grade < 1 || frm.doc.numeric_grade > 70) {
			frappe.msgprint(__('Numeric grade must be between 1 and 70'));
			frm.set_value('numeric_grade', null);
		}
		
		// Auto-suggest label based on numeric grade
		if (frm.doc.numeric_grade && !frm.doc.label) {
			let suggested_label = get_grade_label_suggestion(frm.doc.numeric_grade);
			if (suggested_label) {
				frm.set_value('label', suggested_label);
			}
		}
	},
	
	is_proof: function(frm) {
		// Proof grades typically start at 60
		if (frm.doc.is_proof && frm.doc.numeric_grade && frm.doc.numeric_grade < 60) {
			frappe.msgprint({
				title: __('Note'),
				message: __('Proof grades typically use numeric values 60-70'),
				indicator: 'yellow'
			});
		}
	},
	
	is_circulated: function(frm) {
		// Circulated grades typically 1-59
		if (frm.doc.is_circulated && frm.doc.numeric_grade && frm.doc.numeric_grade >= 60) {
			frappe.msgprint({
				title: __('Note'),
				message: __('Circulated grades typically use numeric values 1-59'),
				indicator: 'yellow'
			});
		}
	}
});

function get_grade_label_suggestion(numeric_grade) {
	// Standard Sheldon scale labels
	const grade_map = {
		70: 'Perfect Uncirculated',
		69: 'Superb Gem Uncirculated',
		68: 'Superb Gem Uncirculated',
		67: 'Superb Gem Uncirculated',
		66: 'Gem Uncirculated',
		65: 'Gem Uncirculated',
		64: 'Choice Uncirculated',
		63: 'Choice Uncirculated',
		62: 'Uncirculated',
		61: 'Uncirculated',
		60: 'Uncirculated',
		58: 'Choice About Uncirculated',
		55: 'About Uncirculated',
		53: 'About Uncirculated',
		50: 'About Uncirculated',
		45: 'Choice Extremely Fine',
		40: 'Extremely Fine',
		35: 'Choice Very Fine',
		30: 'Very Fine',
		25: 'Very Fine',
		20: 'Very Fine',
		15: 'Fine',
		12: 'Fine',
		10: 'Very Good',
		8: 'Very Good',
		6: 'Good',
		4: 'Good',
		3: 'About Good',
		2: 'Fair',
		1: 'Poor'
	};
	
	return grade_map[numeric_grade] || null;
}
