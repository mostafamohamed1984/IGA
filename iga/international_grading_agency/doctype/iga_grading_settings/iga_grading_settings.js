frappe.ui.form.on('IGA Grading Settings', {
	refresh: function(frm) {
		frm.dashboard.add_indicator(__('System-wide Grading Configuration'), 'blue');

		if (frm.doc.vat_rate) {
			frm.dashboard.add_indicator(__('VAT: {0}%', [frm.doc.vat_rate]), 'green');
		}

		if (frm.doc.scoring_components && frm.doc.scoring_components.length > 0) {
			let total_weight_unc = 0;
			let total_weight_circ = 0;
			frm.doc.scoring_components.forEach(function(comp) {
				total_weight_unc += comp.weight_uncirculated || 0;
				total_weight_circ += comp.weight_circulated || 0;
			});

			if (Math.abs(total_weight_unc - 100) > 0.01) {
				frm.dashboard.add_indicator(__('Warning: Uncirculated weights sum to {0}% (should be 100%)',
					[total_weight_unc.toFixed(2)]), 'red');
			}
			if (Math.abs(total_weight_circ - 100) > 0.01) {
				frm.dashboard.add_indicator(__('Warning: Circulated weights sum to {0}% (should be 100%)',
					[total_weight_circ.toFixed(2)]), 'red');
			}
		}

		frm.add_custom_button(__('Test Grading Calculator'), function() {
			show_grading_test_dialog(frm);
		});
	},

	vat_rate: function(frm) {
		if (frm.doc.vat_rate < 0 || frm.doc.vat_rate > 100) {
			frappe.msgprint(__('VAT rate must be between 0 and 100'));
			frm.set_value('vat_rate', 14);
		}
	}
});

frappe.ui.form.on('Grading Scoring Component', {
	weight_uncirculated: function(frm, cdt, cdn) {
		calculate_total_weights(frm);
	},

	weight_circulated: function(frm, cdt, cdn) {
		calculate_total_weights(frm);
	}
});

function calculate_total_weights(frm) {
	if (!frm.doc.scoring_components) return;

	let total_unc = 0;
	let total_circ = 0;

	frm.doc.scoring_components.forEach(function(comp) {
		total_unc += comp.weight_uncirculated || 0;
		total_circ += comp.weight_circulated || 0;
	});

	frappe.show_alert({
		message: __('Total Weights - Uncirculated: {0}%, Circulated: {1}%',
			[total_unc.toFixed(2), total_circ.toFixed(2)]),
		indicator: (Math.abs(total_unc - 100) < 0.01 && Math.abs(total_circ - 100) < 0.01) ? 'green' : 'orange'
	});
}

function show_grading_test_dialog(frm) {
	let d = new frappe.ui.Dialog({
		title: __('Test Grading Calculator'),
		fields: [
			{
				fieldtype: 'Select',
				fieldname: 'coin_type',
				label: 'Coin Type',
				options: 'Uncirculated\nCirculated',
				reqd: 1
			},
			{
				fieldtype: 'Section Break'
			},
			{
				fieldtype: 'HTML',
				fieldname: 'result_html'
			}
		],
		primary_action_label: __('Calculate'),
		primary_action: function() {
			frappe.call({
				method: 'test_grading_calculation',
				doc: frm.doc,
				args: {
					coin_type: d.get_value('coin_type')
				},
				callback: function(r) {
					if (r.message) {
						d.fields_dict.result_html.$wrapper.html(
							'<div class="alert alert-info">' + r.message + '</div>'
						);
					}
				}
			});
		}
	});
	d.show();
}
