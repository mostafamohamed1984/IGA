// Copyright (c) 2026, IGA and contributors
// For license information, please see license.txt

frappe.ui.form.on('Submission', {
	refresh: function(frm) {
		// Add custom buttons based on status
		if (frm.doc.status === 'Created' && !frm.doc.__islocal) {
			frm.add_custom_button(__('Mark as Received'), function() {
				frm.set_value('status', 'Received');
				frm.set_value('received_on', frappe.datetime.now_datetime());
				frm.save();
			});
		}

		if (frm.doc.status === 'Shipped' || frm.doc.status === 'Ready for Pickup') {
			frm.add_custom_button(__('Mark as Completed'), function() {
				frm.set_value('status', 'Completed');
				frm.set_value('completed_on', frappe.datetime.now_datetime());
				frm.save();
			});
		}

		// Add button to view tracking page
		if (frm.doc.tracking_id) {
			frm.add_custom_button(__('View Tracking'), function() {
				frappe.msgprint(__('Tracking ID: {0}', [frm.doc.tracking_id]));
			});
		}

		// Add button to generate proforma invoice
		if (frm.doc.status === 'Created' && !frm.doc.proforma_invoice) {
			frm.add_custom_button(__('Generate Proforma Invoice'), function() {
				frappe.call({
					method: 'iga.international_grading_agency.doctype.submission.submission.generate_proforma_invoice',
					args: {
						submission_name: frm.doc.name
					},
					callback: function(r) {
						if (r.message) {
							frm.reload_doc();
							frappe.msgprint(__('Proforma Invoice {0} created', [r.message]));
						}
					}
				});
			});
		}

		// Color code status
		if (frm.doc.status) {
			frm.set_df_property('status', 'description', get_status_description(frm.doc.status));
		}

		// Show items breakdown
		if (frm.doc.items_breakdown) {
			try {
				const breakdown = JSON.parse(frm.doc.items_breakdown);
				let html = '<table class="table table-bordered table-sm"><thead><tr><th>Stage</th><th>Count</th></tr></thead><tbody>';
				for (const [stage, count] of Object.entries(breakdown)) {
					if (count > 0) {
						html += `<tr><td>${stage}</td><td>${count}</td></tr>`;
					}
				}
				html += '</tbody></table>';
				frm.set_df_property('items_breakdown', 'description', html);
			} catch (e) {
				console.error('Error parsing items_breakdown:', e);
			}
		}
	},

	onload: function(frm) {
		// Set filters for customer field
		frm.set_query('customer', function() {
			return {
				filters: {
					'customer_group': 'IGA Members'
				}
			};
		});

		// Set filters for subscription field
		frm.set_query('subscription', function() {
			if (frm.doc.customer) {
				return {
					filters: {
						'customer': frm.doc.customer,
						'status': 'Active'
					}
				};
			}
		});

		// Set filters for service_tier
		frm.set_query('service_tier', function() {
			return {
				filters: {
					'status': 'Active'
				}
			};
		});

		// Set filters for dealer
		frm.set_query('dealer', function() {
			return {
				filters: {
					'customer_group': 'IGA Dealers'
				}
			};
		});
	},

	customer: function(frm) {
		// Auto-fetch active subscription
		if (frm.doc.customer && !frm.doc.subscription) {
			frappe.call({
				method: 'iga.international_grading_agency.doctype.submission.submission.get_active_subscription',
				args: {
					customer: frm.doc.customer
				},
				callback: function(r) {
					if (r.message) {
						frm.set_value('subscription', r.message);
					} else {
						frappe.msgprint(__('No active subscription found for this customer'));
					}
				}
			});
		}
	},

	service_tier: function(frm) {
		// Calculate pricing when service tier changes
		calculate_totals(frm);
	},

	is_bulk: function(frm) {
		// Recalculate with bulk discount
		calculate_totals(frm);
	},

	uses_credit: function(frm) {
		// Show/hide credit fields
		frm.toggle_display('credits_used', frm.doc.uses_credit);
		if (frm.doc.uses_credit && frm.doc.subscription) {
			// Fetch available credits
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'Membership Subscriptions',
					filters: { name: frm.doc.subscription },
					fieldname: 'credits_remaining'
				},
				callback: function(r) {
					if (r.message) {
						frappe.msgprint(__('Available Credits: {0}', [r.message.credits_remaining]));
					}
				}
			});
		}
	},

	submission_source: function(frm) {
		// Show/hide dealer fields
		const is_dealer = frm.doc.submission_source === 'Dealer';
		frm.toggle_display('dealer', is_dealer);
		frm.toggle_display('submitted_on_behalf_of', is_dealer);
		frm.toggle_display('dealer_reference_no', is_dealer);
		frm.toggle_reqd('dealer', is_dealer);
	},

	before_save: function(frm) {
		// Calculate item count
		if (frm.doc.items) {
			frm.set_value('item_count', frm.doc.items.length);
		}

		// Calculate declared value total
		let total_value = 0;
		if (frm.doc.items) {
			frm.doc.items.forEach(function(item) {
				total_value += item.declared_value || 0;
			});
		}
		frm.set_value('declared_value_total', total_value);

		// Calculate totals
		calculate_totals(frm);
	}
});

// Child table: Submission Item
frappe.ui.form.on('Submission Item', {
	items_add: function(frm, cdt, cdn) {
		// Set default values for new item
		const row = locals[cdt][cdn];
		if (!row.declared_value) {
			frappe.model.set_value(cdt, cdn, 'declared_value', 0);
		}
	},

	item_reference: function(frm, cdt, cdn) {
		// Auto-fetch reference details
		const row = locals[cdt][cdn];
		if (row.item_reference) {
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Item Reference Catalog',
					name: row.item_reference
				},
				callback: function(r) {
					if (r.message) {
						// Could auto-fill some fields from reference
						frappe.model.set_value(cdt, cdn, 'reference_title', r.message.title);
					}
				}
			});
		}
	},

	declared_value: function(frm, cdt, cdn) {
		// Recalculate totals
		calculate_totals(frm);
	},

	items_remove: function(frm, cdt, cdn) {
		// Recalculate totals
		calculate_totals(frm);
	}
});

// Helper Functions
function calculate_totals(frm) {
	if (!frm.doc.service_tier || !frm.doc.items || frm.doc.items.length === 0) {
		return;
	}

	// Fetch service tier pricing
	frappe.call({
		method: 'frappe.client.get',
		args: {
			doctype: 'Service Master',
			name: frm.doc.service_tier
		},
		callback: function(r) {
			if (r.message) {
				const service = r.message;
				let subtotal = service.base_fee * frm.doc.items.length;

				// Apply bulk discount
				if (frm.doc.is_bulk && service.bulk_discount_pct) {
					const discount_amount = subtotal * (service.bulk_discount_pct / 100);
					subtotal -= discount_amount;
					frm.set_value('discount_pct', service.bulk_discount_pct);
				} else {
					frm.set_value('discount_pct', 0);
				}

				// Calculate VAT
				frappe.call({
					method: 'frappe.client.get_value',
					args: {
						doctype: 'IGA Grading Settings',
						filters: { name: 'IGA Grading Settings' },
						fieldname: 'vat_rate'
					},
					callback: function(vat_r) {
						const vat_rate = vat_r.message ? vat_r.message.vat_rate : 14;
						const vat_amount = subtotal * (vat_rate / 100);
						const grand_total = subtotal + vat_amount;

						frm.set_value('subtotal', subtotal);
						frm.set_value('vat_amount', vat_amount);
						frm.set_value('grand_total', grand_total);
					}
				});
			}
		}
	});
}

function get_status_description(status) {
	const descriptions = {
		'Created': 'Submission registered, awaiting physical receipt',
		'Received': 'Items received and logged into system',
		'Grading': 'Items being evaluated by graders',
		'Slabbing': 'Items being encapsulated',
		'QC': 'Quality control review in progress',
		'Imaging': 'Professional photography in progress',
		'Shipped': 'Items shipped to customer',
		'Ready for Pickup': 'Items ready for counter collection',
		'Completed': 'Submission completed and delivered',
		'On Hold': 'Submission temporarily paused'
	};
	return descriptions[status] || '';
}
