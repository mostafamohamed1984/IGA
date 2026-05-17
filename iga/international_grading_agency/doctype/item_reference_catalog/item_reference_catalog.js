frappe.ui.form.on('Item Reference Catalog', {
	refresh: function(frm) {
		// Status indicator
		if (frm.doc.status === 'Draft') {
			frm.dashboard.add_indicator(__('Draft - Not available for submissions'), 'orange');
		} else if (frm.doc.status === 'Deprecated') {
			frm.dashboard.add_indicator(__('Deprecated'), 'red');
		}
		
		// Collectible type indicator
		if (frm.doc.collectible_type) {
			frm.dashboard.add_indicator(__('Type: {0}', [frm.doc.collectible_type]), 'blue');
		}
		
		// Reference code display
		if (frm.doc.ref_code) {
			frm.dashboard.add_indicator(__('Ref: {0}', [frm.doc.ref_code]), 'green');
		}
		
		// Activate button
		if (frm.doc.status === 'Draft') {
			frm.add_custom_button(__('Activate'), function() {
				frm.set_value('status', 'Active');
				frm.set_value('last_verified', frappe.datetime.nowdate());
				frm.save();
			}).addClass('btn-primary');
		}
		
		// Deprecate button
		if (frm.doc.status === 'Active') {
			frm.add_custom_button(__('Deprecate'), function() {
				frappe.prompt({
					label: __('Deprecation Reason'),
					fieldname: 'reason',
					fieldtype: 'Small Text',
					reqd: 1
				}, function(values) {
					frm.set_value('status', 'Deprecated');
					frm.set_value('deprecated_reason', values.reason);
					frm.save();
				}, __('Deprecate Reference Item'));
			});
		}
		
		// View submissions button
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Submissions'), function() {
				frappe.route_options = {
					'reference_item': frm.doc.name
				};
				frappe.set_route('List', 'Submission Item');
			});
		}
		
		// Generate reference code button
		if (frm.is_new() || !frm.doc.ref_code) {
			frm.add_custom_button(__('Generate Reference Code'), function() {
				generate_reference_code(frm);
			});
		}
		
		// Image preview
		if (frm.doc.front_image) {
			frm.fields_dict.front_image_preview.$wrapper.html(
				`<img src="${frm.doc.front_image}" style="max-width: 200px; border: 1px solid #ddd; border-radius: 4px;">`
			);
		}
		if (frm.doc.back_image) {
			frm.fields_dict.back_image_preview.$wrapper.html(
				`<img src="${frm.doc.back_image}" style="max-width: 200px; border: 1px solid #ddd; border-radius: 4px;">`
			);
		}
	},
	
	collectible_type: function(frm) {
		// Show/hide relevant sections based on type
		toggle_type_sections(frm);
	},
	
	country: function(frm) {
		// Auto-populate issuer authority for certain countries
		if (frm.doc.country && !frm.doc.issuer_authority) {
			suggest_issuer_authority(frm);
		}
	},
	
	year_ad: function(frm) {
		// Auto-populate title if fields are available
		if (frm.doc.year_ad && frm.doc.country && frm.doc.denomination_value) {
			auto_generate_title(frm);
		}
	},
	
	denomination_value: function(frm) {
		// Auto-populate title
		if (frm.doc.year_ad && frm.doc.country && frm.doc.denomination_value) {
			auto_generate_title(frm);
		}
	}
});

function toggle_type_sections(frm) {
	// This is handled by depends_on in JSON, but we can add additional logic here
	if (frm.doc.collectible_type) {
		frappe.show_alert({
			message: __('Showing fields for {0}', [frm.doc.collectible_type]),
			indicator: 'blue'
		});
	}
}

function suggest_issuer_authority(frm) {
	const issuer_map = {
		'EG': 'Central Bank of Egypt',
		'SA': 'Saudi Arabian Monetary Authority',
		'AE': 'Central Bank of UAE',
		'US': 'United States Mint',
		'GB': 'Royal Mint',
		'FR': 'Monnaie de Paris',
		'DE': 'Staatliche Münze Berlin'
	};
	
	let suggested = issuer_map[frm.doc.country];
	if (suggested) {
		frm.set_value('issuer_authority', suggested);
	}
}

function auto_generate_title(frm) {
	if (frm.doc.title) return; // Don't overwrite existing title
	
	let parts = [];
	
	if (frm.doc.year_ad) parts.push(frm.doc.year_ad);
	if (frm.doc.country) parts.push(frm.doc.country);
	if (frm.doc.denomination_value && frm.doc.denomination_unit) {
		parts.push(frm.doc.denomination_value + ' ' + frm.doc.denomination_unit);
	} else if (frm.doc.denomination_value) {
		parts.push(frm.doc.denomination_value);
	}
	
	if (frm.doc.issue_type && frm.doc.issue_type !== 'Circulation') {
		parts.push('(' + frm.doc.issue_type + ')');
	}
	
	if (parts.length > 0) {
		frm.set_value('title', parts.join(' '));
	}
}

function generate_reference_code(frm) {
	frappe.call({
		method: 'generate_reference_code',
		doc: frm.doc,
		callback: function(r) {
			if (r.message) {
				frm.set_value('ref_code', r.message);
				frappe.show_alert({
					message: __('Reference code generated: {0}', [r.message]),
					indicator: 'green'
				});
			}
		}
	});
}
