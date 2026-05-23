frappe.ui.form.on('NFC Settings', {
	refresh: function(frm) {
		// Single DocType indicator
		frm.dashboard.add_indicator(__('NFC Chip Configuration'), 'blue');
		
		// Display key settings
		if (frm.doc.nfc_enabled) {
			frm.dashboard.add_indicator(__('NFC Enabled'), 'green');
		} else {
			frm.dashboard.add_indicator(__('NFC Disabled'), 'red');
		}
		
		// API endpoint display
		if (frm.doc.api_endpoint) {
			frm.dashboard.add_indicator(__('API: {0}', [frm.doc.api_endpoint]), 'blue');
		}
		
		// Signing profile indicator
		if (frm.doc.active_signing_profile) {
			frm.dashboard.add_indicator(__('Signing Profile: {0}', [frm.doc.active_signing_profile]), 'orange');
		}
		
		// Verify URL indicator
		if (frm.doc.verify_url_base) {
			frm.dashboard.add_indicator(__('Verify URL configured'), 'purple');
		}
		
		// Test connection button
		if (frm.doc.nfc_enabled && frm.doc.api_endpoint) {
			frm.add_custom_button(__('Test NFC Connection'), function() {
				test_nfc_connection(frm);
			});
		}
		
		// Generate test chip button
		frm.add_custom_button(__('Generate Test Chip Data'), function() {
			generate_test_chip_data(frm);
		});
		
		// Security warning
		if (frm.doc.api_key) {
			frappe.msgprint({
				title: __('Security Notice'),
				message: __('API key is stored. Ensure proper access controls are in place.'),
				indicator: 'orange'
			});
		}
	},
	
	nfc_enabled: function(frm) {
		// Show/hide relevant fields
		if (frm.doc.nfc_enabled) {
			frm.set_df_property('api_endpoint', 'reqd', 1);
			frm.set_df_property('api_key', 'reqd', 1);
		} else {
			frm.set_df_property('api_endpoint', 'reqd', 0);
			frm.set_df_property('api_key', 'reqd', 0);
		}
	},
	
	api_endpoint: function(frm) {
		// Validate URL format
		if (frm.doc.api_endpoint && !frm.doc.api_endpoint.startsWith('http')) {
			frappe.msgprint(__('API endpoint should start with http:// or https://'));
		}
	}
});

function test_nfc_connection(frm) {
	frappe.call({
		method: 'test_nfc_connection',
		doc: frm.doc,
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({
					message: __('NFC connection successful'),
					indicator: 'green'
				});
			} else {
				frappe.msgprint({
					title: __('Connection Failed'),
					message: r.message ? r.message.error : __('Unable to connect to NFC service'),
					indicator: 'red'
				});
			}
		}
	});
}

function generate_test_chip_data(frm) {
	let d = new frappe.ui.Dialog({
		title: __('Generate Test Chip Data'),
		fields: [
			{
				fieldtype: 'Data',
				fieldname: 'certificate_no',
				label: 'Certificate Number',
				reqd: 1,
				default: 'IGA-TEST-12345'
			},
			{
				fieldtype: 'Data',
				fieldname: 'grade',
				label: 'Grade',
				reqd: 1,
				default: 'MS-65'
			},
			{
				fieldtype: 'Section Break'
			},
			{
				fieldtype: 'HTML',
				fieldname: 'result_html'
			}
		],
		primary_action_label: __('Generate'),
		primary_action: function() {
			frappe.call({
				method: 'generate_nfc_data',
				doc: frm.doc,
				args: {
					certificate_no: d.get_value('certificate_no'),
					grade: d.get_value('grade')
				},
				callback: function(r) {
					if (r.message) {
						let html = `
							<div class="alert alert-success">
								<h5>Test Chip Data Generated</h5>
								<pre>${JSON.stringify(r.message, null, 2)}</pre>
							</div>
						`;
						d.fields_dict.result_html.$wrapper.html(html);
					}
				}
			});
		}
	});
	d.show();
}
