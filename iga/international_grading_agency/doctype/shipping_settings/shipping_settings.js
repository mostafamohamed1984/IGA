frappe.ui.form.on('Shipping Settings', {
	refresh: function(frm) {
		// Single DocType indicator
		frm.dashboard.add_indicator(__('Shipping & Logistics Configuration'), 'blue');
		
		// Display carrier info
		if (frm.doc.default_carrier) {
			frm.dashboard.add_indicator(__('Carrier: {0}', [frm.doc.default_carrier]), 'green');
		}
		
		// Display shipping zones count
		if (frm.doc.shipping_zones && frm.doc.shipping_zones.length > 0) {
			frm.dashboard.add_indicator(__('Zones: {0}', [frm.doc.shipping_zones.length]), 'orange');
		}
		
		// Test carrier API button
		if (frm.doc.carrier_api_endpoint) {
			frm.add_custom_button(__('Test Carrier API'), function() {
				test_carrier_api(frm);
			});
		}
		
		// Calculate shipping button
		frm.add_custom_button(__('Calculate Shipping Cost'), function() {
			calculate_shipping_cost(frm);
		});
		
		// Track shipment button
		frm.add_custom_button(__('Track Shipment'), function() {
			track_shipment(frm);
		});
	},
	
	default_carrier: function(frm) {
		// Show carrier-specific fields
		if (frm.doc.default_carrier) {
			frappe.msgprint({
				title: __('Carrier Selected'),
				message: __('Ensure API credentials are configured for {0}', [frm.doc.default_carrier]),
				indicator: 'blue'
			});
		}
	}
});

frappe.ui.form.on('Shipping Zone', {
	zone_name: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// Auto-generate zone code
		if (row.zone_name && !row.zone_code) {
			let code = row.zone_name.toUpperCase().replace(/\s+/g, '_');
			frappe.model.set_value(cdt, cdn, 'zone_code', code);
		}
	},
	
	base_rate: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// Validate rate
		if (row.base_rate < 0) {
			frappe.msgprint(__('Base rate cannot be negative'));
			frappe.model.set_value(cdt, cdn, 'base_rate', 0);
		}
	}
});

function test_carrier_api(frm) {
	frappe.call({
		method: 'test_carrier_connection',
		doc: frm.doc,
		callback: function(r) {
			if (r.message && r.message.success) {
				frappe.show_alert({
					message: __('Carrier API connection successful'),
					indicator: 'green'
				});
			} else {
				frappe.msgprint({
					title: __('Connection Failed'),
					message: r.message ? r.message.error : __('Unable to connect to carrier API'),
					indicator: 'red'
				});
			}
		}
	});
}

function calculate_shipping_cost(frm) {
	let d = new frappe.ui.Dialog({
		title: __('Calculate Shipping Cost'),
		fields: [
			{
				fieldtype: 'Link',
				fieldname: 'submission',
				label: 'Submission',
				options: 'Submission',
				reqd: 1
			},
			{
				fieldtype: 'Select',
				fieldname: 'shipping_zone',
				label: 'Shipping Zone',
				options: get_zone_options(frm),
				reqd: 1
			},
			{
				fieldtype: 'Select',
				fieldname: 'service_level',
				label: 'Service Level',
				options: 'Standard\nExpress\nOvernight',
				reqd: 1,
				default: 'Standard'
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
				method: 'calculate_shipping',
				doc: frm.doc,
				args: {
					submission: d.get_value('submission'),
					zone: d.get_value('shipping_zone'),
					service_level: d.get_value('service_level')
				},
				callback: function(r) {
					if (r.message) {
						let html = `
							<table class="table table-bordered">
								<tr><th>Base Rate</th><td>${r.message.base_rate} EGP</td></tr>
								<tr><th>Weight Surcharge</th><td>${r.message.weight_surcharge || 0} EGP</td></tr>
								<tr><th>Service Level Fee</th><td>${r.message.service_fee || 0} EGP</td></tr>
								<tr><th>Insurance</th><td>${r.message.insurance || 0} EGP</td></tr>
								<tr><th><strong>Total</strong></th><td><strong>${r.message.total} EGP</strong></td></tr>
							</table>
						`;
						d.fields_dict.result_html.$wrapper.html(html);
					}
				}
			});
		}
	});
	d.show();
}

function track_shipment(frm) {
	let d = new frappe.ui.Dialog({
		title: __('Track Shipment'),
		fields: [
			{
				fieldtype: 'Data',
				fieldname: 'tracking_number',
				label: 'Tracking Number',
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
		primary_action_label: __('Track'),
		primary_action: function() {
			frappe.call({
				method: 'track_shipment',
				doc: frm.doc,
				args: {
					tracking_number: d.get_value('tracking_number')
				},
				callback: function(r) {
					if (r.message) {
						let events = r.message.events || [];
						let html = '<div class="tracking-timeline">';
						
						events.forEach(function(event) {
							html += `
								<div class="alert alert-info" style="margin-bottom: 10px;">
									<strong>${event.status}</strong><br>
									<small>${event.location} - ${event.timestamp}</small><br>
									${event.description || ''}
								</div>
							`;
						});
						
						html += '</div>';
						d.fields_dict.result_html.$wrapper.html(html);
					}
				}
			});
		}
	});
	d.show();
}

function get_zone_options(frm) {
	if (!frm.doc.shipping_zones) return '';
	return frm.doc.shipping_zones.map(z => z.zone_name).join('\n');
}
