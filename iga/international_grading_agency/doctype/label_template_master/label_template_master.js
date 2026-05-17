frappe.ui.form.on('Label Template Master', {
	refresh: function(frm) {
		// Status indicator
		if (frm.doc.status === 'Draft') {
			frm.dashboard.add_indicator(__('Draft - Not available for production'), 'orange');
		}
		
		// Template info display
		if (frm.doc.holder_type) {
			frm.dashboard.add_indicator(__('Holder: {0}', [frm.doc.holder_type]), 'blue');
		}
		if (frm.doc.label_variant) {
			frm.dashboard.add_indicator(__('Variant: {0}', [frm.doc.label_variant]), 'green');
		}
		
		// JSON validation button
		if (frm.doc.layout_json) {
			frm.add_custom_button(__('Validate JSON'), function() {
				try {
					JSON.parse(frm.doc.layout_json);
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
		
		// Preview button (if backend supports it)
		if (!frm.is_new() && frm.doc.status === 'Active') {
			frm.add_custom_button(__('Preview Template'), function() {
				frappe.call({
					method: 'preview_template',
					doc: frm.doc,
					callback: function(r) {
						if (r.message) {
							// Open preview in new window or dialog
							let d = new frappe.ui.Dialog({
								title: __('Template Preview'),
								fields: [{
									fieldtype: 'HTML',
									fieldname: 'preview_html'
								}]
							});
							d.fields_dict.preview_html.$wrapper.html(r.message);
							d.show();
						}
					}
				});
			});
		}
		
		// Add button to view usage
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Usage'), function() {
				frappe.route_options = {
					'label_template': frm.doc.name
				};
				frappe.set_route('List', 'Submission Item');
			});
		}
	},
	
	template_code: function(frm) {
		// Auto-uppercase template codes
		if (frm.doc.template_code) {
			frm.set_value('template_code', frm.doc.template_code.toUpperCase());
		}
	},
	
	layout_json: function(frm) {
		// Auto-validate JSON on change
		if (frm.doc.layout_json) {
			try {
				JSON.parse(frm.doc.layout_json);
				frm.set_df_property('layout_json', 'description', __('Valid JSON'));
			} catch (e) {
				frm.set_df_property('layout_json', 'description', __('Invalid JSON: {0}', [e.message]));
			}
		}
	}
});
