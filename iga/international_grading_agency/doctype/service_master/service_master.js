// Copyright (c) 2026, IGA and contributors
// For license information, please see license.txt

frappe.ui.form.on('Service Master', {
	refresh: function(frm) {
		// Add custom button to preview pricing
		if (!frm.doc.__islocal) {
			frm.add_custom_button(__('Preview Pricing'), function() {
				show_pricing_preview(frm);
			});
		}

		// Show calculated effective price with discounts
		if (frm.doc.base_fee) {
			update_pricing_display(frm);
		}

		// Color code status
		if (frm.doc.status) {
			const color = frm.doc.status === 'Active' ? 'green' : 'red';
			frm.set_df_property('status', 'description',
				`<span style="color: ${color}; font-weight: bold;">${frm.doc.status}</span>`
			);
		}

		// Show service tier badge
		if (frm.doc.service_tier) {
			const tier_colors = {
				'Value': 'blue',
				'Standard': 'green',
				'Express': 'orange',
				'Priority': 'red'
			};
			frm.dashboard.add_comment(
				__('Tier: <b>{0}</b>', [frm.doc.service_tier]),
				tier_colors[frm.doc.service_tier] || 'blue',
				true
			);
		}

		// Show turnaround time
		if (frm.doc.turnaround_days_min && frm.doc.turnaround_days_max) {
			frm.dashboard.add_comment(
				__('Turnaround: {0}-{1} days', [frm.doc.turnaround_days_min, frm.doc.turnaround_days_max]),
				'blue',
				true
			);
		}
	},

	onload: function(frm) {
		// Set default values for new records
		if (frm.doc.__islocal) {
			if (!frm.doc.status) {
				frm.set_value('status', 'Active');
			}
			if (!frm.doc.is_add_on) {
				frm.set_value('is_add_on', 0);
			}
		}
	},

	category: function(frm) {
		// Update service code suggestion
		if (frm.doc.category && frm.doc.service_tier && frm.doc.__islocal) {
			suggest_service_code(frm);
		}
	},

	service_tier: function(frm) {
		// Update service code suggestion
		if (frm.doc.category && frm.doc.service_tier && frm.doc.__islocal) {
			suggest_service_code(frm);
		}

		// Show/hide add-on fields
		frm.toggle_display('add_on_surcharge_pct', frm.doc.is_add_on);
	},

	is_add_on: function(frm) {
		// Show/hide add-on specific fields
		frm.toggle_display('add_on_surcharge_pct', frm.doc.is_add_on);
		frm.toggle_reqd('add_on_surcharge_pct', frm.doc.is_add_on);

		if (frm.doc.is_add_on) {
			frappe.msgprint({
				title: __('Add-On Service'),
				message: __('Add-on services apply a surcharge percentage on top of the base service fee'),
				indicator: 'blue'
			});
		}
	},

	base_fee: function(frm) {
		// Update pricing display
		update_pricing_display(frm);
	},

	member_discount_pct: function(frm) {
		// Validate discount percentage
		if (frm.doc.member_discount_pct < 0 || frm.doc.member_discount_pct > 100) {
			frappe.msgprint(__('Discount percentage must be between 0 and 100'));
			frm.set_value('member_discount_pct', 0);
		}
		update_pricing_display(frm);
	},

	bulk_discount_pct: function(frm) {
		// Validate discount percentage
		if (frm.doc.bulk_discount_pct < 0 || frm.doc.bulk_discount_pct > 100) {
			frappe.msgprint(__('Discount percentage must be between 0 and 100'));
			frm.set_value('bulk_discount_pct', 0);
		}
		update_pricing_display(frm);
	},

	bulk_min_items: function(frm) {
		// Validate minimum items
		if (frm.doc.bulk_min_items < 1) {
			frappe.msgprint(__('Minimum items must be at least 1'));
			frm.set_value('bulk_min_items', 1);
		}
	},

	add_on_surcharge_pct: function(frm) {
		// Validate surcharge percentage
		if (frm.doc.add_on_surcharge_pct < 0) {
			frappe.msgprint(__('Surcharge percentage cannot be negative'));
			frm.set_value('add_on_surcharge_pct', 0);
		}
		update_pricing_display(frm);
	},

	max_declared_value: function(frm) {
		// Show warning if unlimited
		if (frm.doc.max_declared_value === 0) {
			frappe.show_alert({
				message: __('Unlimited declared value - ensure proper insurance coverage'),
				indicator: 'orange'
			});
		}
	},

	turnaround_days_min: function(frm) {
		// Validate turnaround range
		if (frm.doc.turnaround_days_max && frm.doc.turnaround_days_min > frm.doc.turnaround_days_max) {
			frappe.msgprint(__('Minimum days cannot exceed maximum days'));
			frm.set_value('turnaround_days_min', frm.doc.turnaround_days_max);
		}
	},

	turnaround_days_max: function(frm) {
		// Validate turnaround range
		if (frm.doc.turnaround_days_min && frm.doc.turnaround_days_max < frm.doc.turnaround_days_min) {
			frappe.msgprint(__('Maximum days cannot be less than minimum days'));
			frm.set_value('turnaround_days_max', frm.doc.turnaround_days_min);
		}
	},

	before_save: function(frm) {
		// Auto-generate service name if empty
		if (!frm.doc.service_name && frm.doc.category && frm.doc.service_tier) {
			const name = `${frm.doc.category} - ${frm.doc.service_tier}`;
			frm.set_value('service_name', name);
		}
	}
});

// Helper Functions
function suggest_service_code(frm) {
	// Generate suggested service code
	const category_codes = {
		'Modern Coins': 'MC',
		'Early Modern': 'EM',
		'Medieval': 'MD',
		'Medals & Tokens': 'MT',
		'High Value': 'HV',
		'Unlimited': 'UL'
	};

	const tier_codes = {
		'Value': 'V',
		'Standard': 'S',
		'Express': 'E',
		'Priority': 'P'
	};

	const cat_code = category_codes[frm.doc.category] || 'XX';
	const tier_code = tier_codes[frm.doc.service_tier] || 'X';
	const suggested_code = `${cat_code}-${tier_code}`;

	if (!frm.doc.service_code) {
		frm.set_value('service_code', suggested_code);
	}
}

function update_pricing_display(frm) {
	if (!frm.doc.base_fee) return;

	let html = '<div class="alert alert-info" style="margin-top: 10px;">';
	html += '<h5>Pricing Breakdown</h5>';
	html += `<p><b>Base Fee:</b> EGP ${frm.doc.base_fee.toFixed(2)}</p>`;

	// Member discount
	if (frm.doc.member_discount_pct) {
		const member_price = frm.doc.base_fee * (1 - frm.doc.member_discount_pct / 100);
		html += `<p><b>Member Price (${frm.doc.member_discount_pct}% off):</b> EGP ${member_price.toFixed(2)}</p>`;
	}

	// Bulk discount
	if (frm.doc.bulk_discount_pct && frm.doc.bulk_min_items) {
		const bulk_price = frm.doc.base_fee * (1 - frm.doc.bulk_discount_pct / 100);
		html += `<p><b>Bulk Price (${frm.doc.bulk_discount_pct}% off, min ${frm.doc.bulk_min_items} items):</b> EGP ${bulk_price.toFixed(2)}</p>`;
	}

	// Add-on surcharge
	if (frm.doc.is_add_on && frm.doc.add_on_surcharge_pct) {
		const addon_price = frm.doc.base_fee * (1 + frm.doc.add_on_surcharge_pct / 100);
		html += `<p><b>Add-On Price (+${frm.doc.add_on_surcharge_pct}%):</b> EGP ${addon_price.toFixed(2)}</p>`;
	}

	// VAT
	frappe.call({
		method: 'frappe.client.get_value',
		args: {
			doctype: 'IGA Grading Settings',
			filters: { name: 'IGA Grading Settings' },
			fieldname: 'vat_rate'
		},
		callback: function(r) {
			const vat_rate = r.message ? r.message.vat_rate : 14;
			const price_with_vat = frm.doc.base_fee * (1 + vat_rate / 100);
			html += `<p><b>Price with VAT (${vat_rate}%):</b> EGP ${price_with_vat.toFixed(2)}</p>`;
			html += '</div>';
			frm.set_df_property('base_fee', 'description', html);
		}
	});
}

function show_pricing_preview(frm) {
	const dialog = new frappe.ui.Dialog({
		title: __('Pricing Preview'),
		fields: [
			{
				fieldtype: 'Int',
				fieldname: 'item_count',
				label: __('Number of Items'),
				default: 1,
				reqd: 1
			},
			{
				fieldtype: 'Check',
				fieldname: 'is_member',
				label: __('Member Discount'),
				default: 0
			},
			{
				fieldtype: 'Check',
				fieldname: 'is_bulk',
				label: __('Bulk Discount'),
				default: 0
			},
			{
				fieldtype: 'Section Break'
			},
			{
				fieldtype: 'HTML',
				fieldname: 'preview_html'
			}
		],
		primary_action_label: __('Calculate'),
		primary_action: function(values) {
			let subtotal = frm.doc.base_fee * values.item_count;
			let discount_applied = 0;

			// Apply member discount
			if (values.is_member && frm.doc.member_discount_pct) {
				discount_applied += subtotal * (frm.doc.member_discount_pct / 100);
			}

			// Apply bulk discount
			if (values.is_bulk && frm.doc.bulk_discount_pct && values.item_count >= frm.doc.bulk_min_items) {
				discount_applied += subtotal * (frm.doc.bulk_discount_pct / 100);
			}

			subtotal -= discount_applied;

			// Get VAT rate
			frappe.call({
				method: 'frappe.client.get_value',
				args: {
					doctype: 'IGA Grading Settings',
					filters: { name: 'IGA Grading Settings' },
					fieldname: 'vat_rate'
				},
				callback: function(r) {
					const vat_rate = r.message ? r.message.vat_rate : 14;
					const vat_amount = subtotal * (vat_rate / 100);
					const grand_total = subtotal + vat_amount;

					let html = '<div class="alert alert-success">';
					html += '<h4>Pricing Calculation</h4>';
					html += `<p><b>Items:</b> ${values.item_count}</p>`;
					html += `<p><b>Base Fee per Item:</b> EGP ${frm.doc.base_fee.toFixed(2)}</p>`;
					html += `<p><b>Subtotal:</b> EGP ${(frm.doc.base_fee * values.item_count).toFixed(2)}</p>`;
					if (discount_applied > 0) {
						html += `<p><b>Discount:</b> -EGP ${discount_applied.toFixed(2)}</p>`;
						html += `<p><b>After Discount:</b> EGP ${subtotal.toFixed(2)}</p>`;
					}
					html += `<p><b>VAT (${vat_rate}%):</b> EGP ${vat_amount.toFixed(2)}</p>`;
					html += `<p style="font-size: 18px;"><b>Grand Total:</b> EGP ${grand_total.toFixed(2)}</p>`;
					html += '</div>';

					dialog.fields_dict.preview_html.$wrapper.html(html);
				}
			});
		}
	});

	dialog.show();
	dialog.get_primary_btn().click();
}
