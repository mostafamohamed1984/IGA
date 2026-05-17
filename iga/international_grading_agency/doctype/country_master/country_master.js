frappe.ui.form.on('Country Master', {
	refresh: function(frm) {
		// Status indicator
		if (frm.doc.status === 'Inactive') {
			frm.dashboard.add_indicator(__('Inactive'), 'red');
		}
		
		// Region display
		if (frm.doc.region) {
			frm.dashboard.add_indicator(__('Region: {0}', [frm.doc.region]), 'blue');
		}
		
		// Mint indicator
		if (frm.doc.has_mint) {
			frm.dashboard.add_indicator(__('Has Mint'), 'green');
		}
		
		// Currency display
		if (frm.doc.currency) {
			frm.dashboard.add_indicator(__('Currency: {0}', [frm.doc.currency]), 'orange');
		}
		
		// Add button to view items from this country
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Reference Items'), function() {
				frappe.route_options = {
					'country': frm.doc.name
				};
				frappe.set_route('List', 'Item Reference Catalog');
			});
		}
	},
	
	iso_code: function(frm) {
		// Auto-uppercase ISO codes
		if (frm.doc.iso_code) {
			let code = frm.doc.iso_code.toUpperCase();
			frm.set_value('iso_code', code);
			
			// Validate 2-letter format
			if (code.length !== 2) {
				frappe.msgprint(__('ISO code must be exactly 2 letters'));
			}
		}
	},
	
	country_name: function(frm) {
		// Auto-suggest currency based on country name
		if (frm.doc.country_name && !frm.doc.currency) {
			suggest_currency(frm);
		}
	}
});

function suggest_currency(frm) {
	// Common country-currency mappings
	const currency_map = {
		'Egypt': 'EGP',
		'United States': 'USD',
		'United Kingdom': 'GBP',
		'Saudi Arabia': 'SAR',
		'United Arab Emirates': 'AED',
		'Kuwait': 'KWD',
		'Jordan': 'JOD',
		'Lebanon': 'LBP',
		'Syria': 'SYP',
		'Iraq': 'IQD',
		'Palestine': 'ILS',
		'Morocco': 'MAD',
		'Tunisia': 'TND',
		'Algeria': 'DZD',
		'Libya': 'LYD',
		'Sudan': 'SDG',
		'France': 'EUR',
		'Germany': 'EUR',
		'Italy': 'EUR',
		'Spain': 'EUR',
		'Greece': 'EUR',
		'Turkey': 'TRY',
		'Iran': 'IRR',
		'China': 'CNY',
		'Japan': 'JPY',
		'India': 'INR',
		'Russia': 'RUB',
		'Canada': 'CAD',
		'Australia': 'AUD',
		'Brazil': 'BRL',
		'Mexico': 'MXN',
		'South Africa': 'ZAR'
	};
	
	let suggested = currency_map[frm.doc.country_name];
	if (suggested) {
		frm.set_value('currency', suggested);
	}
}
