frappe.ui.form.on('Reference Code Generator', {
	refresh: function(frm) {
		// Display current sequence
		if (frm.doc.last_sequence !== undefined) {
			frm.dashboard.add_indicator(__('Last Sequence: {0}', [frm.doc.last_sequence]), 'blue');
		}
		
		// Display generator key
		if (frm.doc.generator_key) {
			frm.dashboard.add_indicator(__('Key: {0}', [frm.doc.generator_key]), 'green');
		}
		
		// Preview next code
		if (!frm.is_new()) {
			frm.add_custom_button(__('Preview Next Code'), function() {
				preview_next_code(frm);
			});
		}
		
		// Reset sequence button (with confirmation)
		if (!frm.is_new()) {
			frm.add_custom_button(__('Reset Sequence'), function() {
				reset_sequence(frm);
			});
		}
		
		// View generated codes
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Generated Codes'), function() {
				frappe.route_options = {
					'ref_code': ['like', frm.doc.generator_key + '%']
				};
				frappe.set_route('List', 'Item Reference Catalog');
			});
		}
		
		// Read-only enforcement for system-managed fields
		frm.set_df_property('generator_key', 'read_only', 1);
		frm.set_df_property('last_sequence', 'read_only', 1);
	},
	
	collectible_type: function(frm) {
		// Auto-generate generator key when all fields are filled
		if (frm.doc.collectible_type && frm.doc.country_code && frm.doc.year) {
			generate_generator_key(frm);
		}
	},
	
	country_code: function(frm) {
		// Auto-uppercase country codes
		if (frm.doc.country_code) {
			frm.set_value('country_code', frm.doc.country_code.toUpperCase());
		}
		
		// Auto-generate generator key
		if (frm.doc.collectible_type && frm.doc.country_code && frm.doc.year) {
			generate_generator_key(frm);
		}
	},
	
	year: function(frm) {
		// Validate year range
		let current_year = new Date().getFullYear();
		if (frm.doc.year < 1 || frm.doc.year > current_year + 10) {
			frappe.msgprint(__('Year should be between 1 and {0}', [current_year + 10]));
		}
		
		// Auto-generate generator key
		if (frm.doc.collectible_type && frm.doc.country_code && frm.doc.year) {
			generate_generator_key(frm);
		}
	}
});

function generate_generator_key(frm) {
	if (frm.is_new()) {
		// Generate key format: TYPE-CTY-YYYY
		let type_code = get_type_code(frm.doc.collectible_type);
		let key = type_code + '-' + frm.doc.country_code + '-' + frm.doc.year;
		frm.set_value('generator_key', key);
	}
}

function get_type_code(collectible_type) {
	// Map collectible types to short codes
	const type_map = {
		'Coin': 'CN',
		'Medal': 'MD',
		'Token': 'TK',
		'Banknote': 'BN',
		'Postcard': 'PC',
		'Collectible Card': 'CC'
	};
	return type_map[collectible_type] || 'XX';
}

function preview_next_code(frm) {
	frappe.call({
		method: 'iga.international_grading_agency.doctype.reference_code_generator.reference_code_generator.preview_next_code',
		args: {
			generator_key: frm.doc.generator_key
		},
		callback: function(r) {
			if (r.message) {
				frappe.msgprint({
					title: __('Next Reference Code'),
					message: `
						<div style="text-align: center; padding: 20px;">
							<p style="font-size: 24px; font-family: monospace; font-weight: bold; color: #2490ef;">
								${r.message}
							</p>
							<hr>
							<small>Current Sequence: ${frm.doc.last_sequence}</small><br>
							<small>Next Sequence: ${frm.doc.last_sequence + 1}</small>
						</div>
					`,
					indicator: 'blue'
				});
			}
		}
	});
}

function reset_sequence(frm) {
	frappe.prompt({
		label: __('Reset Sequence To'),
		fieldname: 'new_sequence',
		fieldtype: 'Int',
		reqd: 1,
		default: 0,
		description: __('Warning: This will reset the sequence counter. Use with caution.')
	}, function(values) {
		frappe.confirm(
			__('Are you sure you want to reset the sequence from {0} to {1}? This action cannot be undone.', 
				[frm.doc.last_sequence, values.new_sequence]),
			function() {
				frm.set_value('last_sequence', values.new_sequence);
				frm.save();
				frappe.show_alert({
					message: __('Sequence reset to {0}', [values.new_sequence]),
					indicator: 'orange'
				});
			}
		);
	}, __('Reset Sequence'));
}
