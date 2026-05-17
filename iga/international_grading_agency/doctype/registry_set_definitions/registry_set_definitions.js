frappe.ui.form.on('Registry Set Definitions', {
	refresh: function(frm) {
		// Status indicator
		if (frm.doc.status === 'Draft') {
			frm.dashboard.add_indicator(__('Draft - Not available for members'), 'orange');
		} else if (frm.doc.status === 'Retired') {
			frm.dashboard.add_indicator(__('Retired'), 'red');
		}
		
		// Set type indicator
		if (frm.doc.is_proof_set) {
			frm.dashboard.add_indicator(__('Proof Set'), 'blue');
		}
		
		// Set statistics
		if (frm.doc.slot_count) {
			frm.dashboard.add_indicator(__('Slots: {0}', [frm.doc.slot_count]), 'green');
		}
		if (frm.doc.max_score) {
			frm.dashboard.add_indicator(__('Max Score: {0}', [frm.doc.max_score.toFixed(2)]), 'purple');
		}
		
		// Activate button
		if (frm.doc.status === 'Draft' && frm.doc.slots && frm.doc.slots.length > 0) {
			frm.add_custom_button(__('Activate Set'), function() {
				frm.set_value('status', 'Active');
				frm.save();
			}).addClass('btn-primary');
		}
		
		// JSON validation button
		if (frm.doc.scoring_rules) {
			frm.add_custom_button(__('Validate Scoring Rules'), function() {
				try {
					JSON.parse(frm.doc.scoring_rules);
					frappe.show_alert({message: __('Valid JSON'), indicator: 'green'});
				} catch (e) {
					frappe.msgprint({
						title: __('Invalid JSON'),
						message: __('Error: {0}', [e.message]),
						indicator: 'red'
					});
				}
			});
		}
		
		// View member sets button
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Member Sets'), function() {
				frappe.route_options = {
					'set_definition': frm.doc.name
				};
				frappe.set_route('List', 'Member Registry Sets');
			});
		}
		
		// Recalculate statistics button
		if (frm.doc.slots && frm.doc.slots.length > 0) {
			frm.add_custom_button(__('Recalculate Stats'), function() {
				calculate_set_statistics(frm);
			});
		}
	},
	
	slots: function(frm) {
		// Auto-recalculate statistics when slots change
		calculate_set_statistics(frm);
	},
	
	scoring_rules: function(frm) {
		// Auto-validate JSON on change
		if (frm.doc.scoring_rules) {
			try {
				JSON.parse(frm.doc.scoring_rules);
				frm.set_df_property('scoring_rules', 'description', __('Valid JSON'));
			} catch (e) {
				frm.set_df_property('scoring_rules', 'description', __('Invalid JSON: {0}', [e.message]));
			}
		}
	}
});

frappe.ui.form.on('Registry Set Slots', {
	slots_add: function(frm, cdt, cdn) {
		// Auto-number new slots
		let row = locals[cdt][cdn];
		if (!row.slot_no) {
			let max_slot = 0;
			frm.doc.slots.forEach(function(slot) {
				if (slot.slot_no > max_slot) max_slot = slot.slot_no;
			});
			frappe.model.set_value(cdt, cdn, 'slot_no', max_slot + 1);
		}
		
		// Default weight
		if (!row.weight) {
			frappe.model.set_value(cdt, cdn, 'weight', 1.0);
		}
	},
	
	reference_item: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// Auto-populate slot label from reference item
		if (row.reference_item) {
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Item Reference Catalog',
					name: row.reference_item
				},
				callback: function(r) {
					if (r.message) {
						let label = r.message.year + ' ' + r.message.denomination;
						if (r.message.variety) label += ' (' + r.message.variety + ')';
						frappe.model.set_value(cdt, cdn, 'slot_label', label);
					}
				}
			});
		}
	}
});

function calculate_set_statistics(frm) {
	// Calculate slot count
	let slot_count = frm.doc.slots ? frm.doc.slots.length : 0;
	frm.set_value('slot_count', slot_count);
	
	// Calculate max score (sum of all weights * 70, assuming max grade is 70)
	let max_score = 0;
	if (frm.doc.slots) {
		frm.doc.slots.forEach(function(slot) {
			max_score += (slot.weight || 1.0) * 70;
		});
	}
	frm.set_value('max_score', max_score);
	
	frappe.show_alert({message: __('Statistics updated'), indicator: 'green'});
}
