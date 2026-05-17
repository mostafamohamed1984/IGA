frappe.ui.form.on('Label Print Settings', {
	refresh: function(frm) {
		// Single DocType indicator
		frm.dashboard.add_indicator(__('Label Printing Configuration'), 'blue');
		
		// Display printer info
		if (frm.doc.default_printer) {
			frm.dashboard.add_indicator(__('Printer: {0}', [frm.doc.default_printer]), 'green');
		}
		
		// Display label dimensions
		if (frm.doc.label_width && frm.doc.label_height) {
			frm.dashboard.add_indicator(__('Size: {0}x{1}mm', 
				[frm.doc.label_width, frm.doc.label_height]), 'blue');
		}
		
		// Test print button
		if (frm.doc.default_printer) {
			frm.add_custom_button(__('Test Print'), function() {
				test_print_label(frm);
			});
		}
		
		// Preview label button
		frm.add_custom_button(__('Preview Label'), function() {
			preview_label_template(frm);
		});
		
		// Printer status button
		if (frm.doc.printer_api_endpoint) {
			frm.add_custom_button(__('Check Printer Status'), function() {
				check_printer_status(frm);
			});
		}
	},
	
	label_width: function(frm) {
		// Validate dimensions
		if (frm.doc.label_width < 10 || frm.doc.label_width > 500) {
			frappe.msgprint(__('Label width should typically be between 10 and 500mm'));
		}
	},
	
	label_height: function(frm) {
		// Validate dimensions
		if (frm.doc.label_height < 10 || frm.doc.label_height > 500) {
			frappe.msgprint(__('Label height should typically be between 10 and 500mm'));
		}
	},
	
	print_dpi: function(frm) {
		// Validate DPI
		if (frm.doc.print_dpi < 150 || frm.doc.print_dpi > 1200) {
			frappe.msgprint(__('Print DPI should typically be between 150 and 1200'));
		}
	}
});

function test_print_label(frm) {
	let d = new frappe.ui.Dialog({
		title: __('Test Print Label'),
		fields: [
			{
				fieldtype: 'Link',
				fieldname: 'submission_item',
				label: 'Submission Item',
				options: 'Submission Item',
				reqd: 1,
				description: 'Select a graded item to print test label'
			},
			{
				fieldtype: 'Check',
				fieldname: 'preview_only',
				label: 'Preview Only (Do Not Print)',
				default: 1
			},
			{
				fieldtype: 'Section Break'
			},
			{
				fieldtype: 'HTML',
				fieldname: 'result_html'
			}
		],
		primary_action_label: __('Print'),
		primary_action: function() {
			frappe.call({
				method: 'print_test_label',
				doc: frm.doc,
				args: {
					submission_item: d.get_value('submission_item'),
					preview_only: d.get_value('preview_only')
				},
				callback: function(r) {
					if (r.message) {
						if (d.get_value('preview_only')) {
							d.fields_dict.result_html.$wrapper.html(
								'<div class="alert alert-info"><h5>Label Preview</h5>' + 
								r.message + '</div>'
							);
						} else {
							frappe.show_alert({
								message: __('Test label sent to printer'),
								indicator: 'green'
							});
							d.hide();
						}
					}
				}
			});
		}
	});
	d.show();
}

function preview_label_template(frm) {
	let d = new frappe.ui.Dialog({
		title: __('Preview Label Template'),
		fields: [
			{
				fieldtype: 'Link',
				fieldname: 'template',
				label: 'Label Template',
				options: 'Label Template Master',
				reqd: 1
			},
			{
				fieldtype: 'Section Break'
			},
			{
				fieldtype: 'HTML',
				fieldname: 'preview_html'
			}
		],
		size: 'large',
		primary_action_label: __('Load Preview'),
		primary_action: function() {
			frappe.call({
				method: 'preview_template',
				doc: frm.doc,
				args: {
					template: d.get_value('template')
				},
				callback: function(r) {
					if (r.message) {
						d.fields_dict.preview_html.$wrapper.html(r.message);
					}
				}
			});
		}
	});
	d.show();
}

function check_printer_status(frm) {
	frappe.call({
		method: 'check_printer_status',
		doc: frm.doc,
		callback: function(r) {
			if (r.message) {
				let status = r.message;
				let indicator = status.online ? 'green' : 'red';
				let html = `
					<table class="table table-bordered">
						<tr><th>Status</th><td><span class="indicator ${indicator}">${status.online ? 'Online' : 'Offline'}</span></td></tr>
						<tr><th>Printer Name</th><td>${status.name || 'N/A'}</td></tr>
						<tr><th>Paper Status</th><td>${status.paper_status || 'Unknown'}</td></tr>
						<tr><th>Ink Level</th><td>${status.ink_level || 'Unknown'}</td></tr>
						<tr><th>Queue Length</th><td>${status.queue_length || 0}</td></tr>
					</table>
				`;
				
				frappe.msgprint({
					title: __('Printer Status'),
					message: html,
					indicator: indicator
				});
			}
		}
	});
}
