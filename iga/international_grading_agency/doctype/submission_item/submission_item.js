// Copyright (c) 2026, IGA and contributors
// For license information, please see license.txt

frappe.ui.form.on('Submission Item', {
	refresh: function(frm) {
		// Add custom buttons for workflow actions
		if (frm.doc.current_stage === 'Grading' && !frm.doc.__islocal) {
			frm.add_custom_button(__('Complete Grading'), function() {
				show_grading_dialog(frm);
			});
		}

		if (frm.doc.current_stage === 'QC' && !frm.doc.__islocal) {
			frm.add_custom_button(__('Approve QC'), function() {
				frm.set_value('current_stage', 'Imaging');
				frm.set_value('graded_on', frappe.datetime.now_datetime());
				frm.save();
			});

			frm.add_custom_button(__('Return to Grading'), function() {
				frappe.confirm(
					__('Return this item to grading?'),
					function() {
						frm.set_value('current_stage', 'Grading');
						frm.set_value('final_grade', '');
						frm.save();
					}
				);
			});
		}

		// Show certificate number prominently
		if (frm.doc.certificate_number) {
			frm.dashboard.add_comment(__('Certificate Number: <b>{0}</b>', [frm.doc.certificate_number]), 'blue', true);
		}

		// Show NFC chip status
		if (frm.doc.nfc_uid) {
			frm.dashboard.add_comment(__('NFC Chip ID: {0}', [frm.doc.nfc_uid]), 'green', true);
		}

		// Color code result type
		if (frm.doc.result_type) {
			const color_map = {
				'Encapsulated': 'green',
				'Details': 'orange',
				'Not Encapsulated': 'red',
				'Rejected': 'red'
			};
			frm.set_df_property('result_type', 'description', 
				`<span style="color: ${color_map[frm.doc.result_type] || 'black'}; font-weight: bold;">${frm.doc.result_type}</span>`
			);
		}

		// Add button to view on public verify page
		if (frm.doc.certificate_number && frm.doc.current_stage === 'Completed') {
			frm.add_custom_button(__('View Public Certificate'), function() {
				window.open(`/verify/${frm.doc.certificate_number}`, '_blank');
			});
		}
	},

	onload: function(frm) {
		// Set filters
		frm.set_query('item_reference', function() {
			return {
				filters: {
					'status': 'Active'
				}
			};
		});

		frm.set_query('final_grade', function() {
			return {
				filters: {
					'status': 'Active'
				}
			};
		});

		frm.set_query('holder_type', function() {
			return {
				filters: {
					'status': 'Active'
				}
			};
		});

		frm.set_query('label_template', function() {
			return {
				filters: {
					'status': 'Active'
				}
			};
		});
	},

	item_reference: function(frm) {
		// Auto-fetch reference details for label
		if (frm.doc.item_reference) {
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Item Reference Catalog',
					name: frm.doc.item_reference
				},
				callback: function(r) {
					if (r.message) {
						const ref = r.message;
						
						// Auto-populate label fields
						let country_denom = '';
						if (ref.country) country_denom += ref.country;
						if (ref.denomination_value) country_denom += ` - ${ref.denomination_value}`;
						if (ref.denomination_unit) country_denom += ` ${ref.denomination_unit}`;
						frm.set_value('label_country_denom', country_denom);

						// Year line
						let year_line = '';
						if (ref.year_ad) year_line += `${ref.year_ad} AD`;
						if (ref.year_ah) year_line += ` / ${ref.year_ah} AH`;
						frm.set_value('label_year_line', year_line);

						// Series line
						if (ref.series_set_issue) {
							frm.set_value('label_series_line', ref.series_set_issue);
						}

						// Suggest holder type based on diameter
						if (ref.diameter_mm) {
							suggest_holder_type(frm, ref.diameter_mm);
						}
					}
				}
			});
		}
	},

	final_grade: function(frm) {
		// Validate grade exists in Grade Scale Master
		if (frm.doc.final_grade) {
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Grade Scale Master',
					name: frm.doc.final_grade
				},
				callback: function(r) {
					if (!r.message) {
						frappe.msgprint(__('Grade {0} not found in Grade Scale Master', [frm.doc.final_grade]));
						frm.set_value('final_grade', '');
					}
				}
			});
		}
	},

	result_type: function(frm) {
		// Show/hide fields based on result type
		const is_encapsulated = frm.doc.result_type === 'Encapsulated';
		const is_details = frm.doc.result_type === 'Details';
		
		frm.toggle_reqd('final_grade', is_encapsulated || is_details);
		frm.toggle_reqd('holder_type', is_encapsulated || is_details);
		frm.toggle_display('designations', is_encapsulated);
		frm.toggle_display('problems', is_details);
	},

	declared_value: function(frm) {
		// Validate against service tier max value
		if (frm.doc.declared_value && frm.doc.parent) {
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Submission',
					filters: { name: frm.doc.parent },
					fieldname: 'service_tier'
				},
				callback: function(r) {
					if (r.message && r.message.service_tier) {
						frappe.call({
							method: 'frappe.client.get_value',
							args: {
								doctype: 'Service Master',
								filters: { name: r.message.service_tier },
								fieldname: 'max_declared_value'
							},
							callback: function(service_r) {
								if (service_r.message && service_r.message.max_declared_value) {
									const max_value = service_r.message.max_declared_value;
									if (max_value > 0 && frm.doc.declared_value > max_value) {
										frappe.msgprint(__('Declared value exceeds maximum for this service tier (EGP {0})', [max_value]));
									}
								}
							}
						});
					}
				}
			});
		}
	},

	images_obverse: function(frm) {
		// Show image preview
		if (frm.doc.images_obverse) {
			frm.set_df_property('images_obverse', 'description', 
				`<img src="${frm.doc.images_obverse}" style="max-width: 200px; border: 1px solid #ddd; padding: 5px;">`
			);
		}
	},

	images_reverse: function(frm) {
		// Show image preview
		if (frm.doc.images_reverse) {
			frm.set_df_property('images_reverse', 'description', 
				`<img src="${frm.doc.images_reverse}" style="max-width: 200px; border: 1px solid #ddd; padding: 5px;">`
			);
		}
	}
});

// Helper Functions
function show_grading_dialog(frm) {
	const dialog = new frappe.ui.Dialog({
		title: __('Complete Grading'),
		fields: [
			{
				fieldtype: 'Link',
				fieldname: 'final_grade',
				label: __('Final Grade'),
				options: 'Grade Scale Master',
				reqd: 1
			},
			{
				fieldtype: 'Select',
				fieldname: 'result_type',
				label: __('Result Type'),
				options: '\nEncapsulated\nDetails\nNot Encapsulated\nRejected',
				reqd: 1
			},
			{
				fieldtype: 'Section Break'
			},
			{
				fieldtype: 'Table MultiSelect',
				fieldname: 'designations',
				label: __('Designations'),
				options: 'Designation Master',
				depends_on: 'eval:doc.result_type=="Encapsulated"'
			},
			{
				fieldtype: 'Table MultiSelect',
				fieldname: 'problems',
				label: __('Problems'),
				options: 'Problem Definitions',
				depends_on: 'eval:doc.result_type=="Details"'
			},
			{
				fieldtype: 'Section Break'
			},
			{
				fieldtype: 'Small Text',
				fieldname: 'internal_notes',
				label: __('Internal Notes')
			}
		],
		primary_action_label: __('Save & Move to QC'),
		primary_action: function(values) {
			frm.set_value('final_grade', values.final_grade);
			frm.set_value('result_type', values.result_type);
			frm.set_value('current_stage', 'QC');
			if (values.internal_notes) {
				frm.set_value('internal_notes', values.internal_notes);
			}
			frm.save();
			dialog.hide();
		}
	});
	dialog.show();
}

function suggest_holder_type(frm, diameter_mm) {
	frappe.call({
		method: 'frappe.client.get_list',
		args: {
			doctype: 'Holder Types Master',
			filters: {
				'status': 'Active',
				'min_mm': ['<=', diameter_mm],
				'max_mm': ['>=', diameter_mm]
			},
			fields: ['name', 'holder_name'],
			limit: 1
		},
		callback: function(r) {
			if (r.message && r.message.length > 0) {
				frm.set_value('holder_type', r.message[0].name);
				frappe.show_alert({
					message: __('Suggested holder type: {0}', [r.message[0].holder_name]),
					indicator: 'green'
				});
			}
		}
	});
}
