frappe.ui.form.on('Member Registry Sets', {
	refresh: function(frm) {
		// Status-based buttons
		if (frm.doc.status === 'Draft') {
			frm.add_custom_button(__('Activate Set'), function() {
				frm.set_value('status', 'Active');
				frm.save();
			}).addClass('btn-primary');
		}
		
		if (frm.doc.status === 'Active') {
			frm.add_custom_button(__('Retire Set'), function() {
				frappe.confirm(
					__('Retire this registry set? It will no longer appear on leaderboards.'),
					function() {
						frm.set_value('status', 'Retired');
						frm.save();
					}
				);
			});
		}
		
		// Recalculate score button
		if (!frm.is_new()) {
			frm.add_custom_button(__('Recalculate Score'), function() {
				frappe.call({
					method: 'recalculate_score',
					doc: frm.doc,
					callback: function(r) {
						if (!r.exc) {
							frm.reload_doc();
							frappe.show_alert({message: __('Score recalculated'), indicator: 'green'});
						}
					}
				});
			});
		}
		
		// Display score/rank prominently
		if (frm.doc.score > 0) {
			frm.dashboard.add_indicator(__('Score: {0}', [frm.doc.score.toFixed(2)]), 'blue');
		}
		if (frm.doc.rank) {
			frm.dashboard.add_indicator(__('Rank: #{0}', [frm.doc.rank]), 'orange');
		}
		if (frm.doc.completion_pct) {
			frm.dashboard.add_indicator(__('Completion: {0}%', [frm.doc.completion_pct]), 'green');
		}
		
		// Public visibility indicator
		if (frm.doc.is_public) {
			frm.dashboard.add_indicator(__('Public on Leaderboard'), 'green');
		} else {
			frm.dashboard.add_indicator(__('Private'), 'grey');
		}
	},
	
	set_definition: function(frm) {
		// Auto-populate slots from set definition
		if (frm.doc.set_definition && frm.is_new()) {
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Registry Set Definitions',
					name: frm.doc.set_definition
				},
				callback: function(r) {
					if (r.message && r.message.slots) {
						frm.clear_table('slots');
						r.message.slots.forEach(function(slot) {
							let row = frm.add_child('slots');
							row.slot_no = slot.slot_no;
							row.slot_label = slot.slot_label;
							row.reference_item = slot.reference_item;
							row.weight = slot.weight;
						});
						frm.refresh_field('slots');
					}
				}
			});
		}
	}
});

frappe.ui.form.on('Member Registry Set Slot', {
	graded_item: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// Fetch grade and designation from graded item
		if (row.graded_item) {
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Submission Item',
					name: row.graded_item
				},
				callback: function(r) {
					if (r.message) {
						frappe.model.set_value(cdt, cdn, 'grade', r.message.grade);
						frappe.model.set_value(cdt, cdn, 'designation', r.message.designation);
						frappe.model.set_value(cdt, cdn, 'slot_score', calculate_slot_score(r.message.grade, row.weight));
					}
				}
			});
		}
	}
});

function calculate_slot_score(grade, weight) {
	// Simple scoring: numeric_grade * weight
	// Backend should implement full scoring logic from Registry Set Definition
	if (!grade || !weight) return 0;
	
	return frappe.call({
		method: 'frappe.client.get_value',
		args: {
			doctype: 'Grade Scale Master',
			filters: {scale_name: grade},
			fieldname: 'numeric_grade'
		},
		async: false
	}).responseJSON.message.numeric_grade * weight;
}
