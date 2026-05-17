frappe.ui.form.on('Membership Plans', {
	refresh: function(frm) {
		// Status indicator
		if (frm.doc.status === 'Retired') {
			frm.dashboard.add_indicator(__('Retired - Not available for new subscriptions'), 'red');
		}
		
		// Plan type indicator
		if (frm.doc.is_dealer_plan) {
			frm.dashboard.add_indicator(__('Dealer Program Plan'), 'purple');
		}
		
		// Benefits summary
		if (frm.doc.included_credits > 0) {
			frm.dashboard.add_indicator(__('Credits: {0}', [frm.doc.included_credits]), 'green');
		}
		if (frm.doc.reward_multiplier) {
			frm.dashboard.add_indicator(__('Rewards: {0}x', [frm.doc.reward_multiplier]), 'blue');
		}
		if (frm.doc.registry_access_level) {
			frm.dashboard.add_indicator(__('Registry: {0}', [frm.doc.registry_access_level]), 'orange');
		}
		
		// Pricing calculator
		frm.add_custom_button(__('Calculate Annual Value'), function() {
			let annual_fee = frm.doc.annual_fee || 0;
			let credits_value = (frm.doc.included_credits || 0) * 50; // Assume 50 EGP per credit
			let total_value = annual_fee + credits_value;
			
			frappe.msgprint({
				title: __('Annual Value Breakdown'),
				message: __('Annual Fee: {0} EGP<br>Included Credits Value: {1} EGP<br>Total Value: {2} EGP', 
					[annual_fee, credits_value, total_value]),
				indicator: 'blue'
			});
		});
		
		// Add button to view active subscriptions
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Subscriptions'), function() {
				frappe.route_options = {
					'plan': frm.doc.name
				};
				frappe.set_route('List', 'Membership Subscriptions');
			});
		}
	},
	
	plan_code: function(frm) {
		// Auto-uppercase plan codes
		if (frm.doc.plan_code) {
			frm.set_value('plan_code', frm.doc.plan_code.toUpperCase());
		}
	},
	
	annual_fee: function(frm) {
		// Suggest monthly fee (annual / 12 * 1.1 for monthly premium)
		if (frm.doc.annual_fee && !frm.doc.monthly_fee) {
			let suggested_monthly = (frm.doc.annual_fee / 12) * 1.1;
			frm.set_value('monthly_fee', Math.round(suggested_monthly));
		}
	},
	
	reward_multiplier: function(frm) {
		// Validate multiplier range
		if (frm.doc.reward_multiplier < 0 || frm.doc.reward_multiplier > 10) {
			frappe.msgprint(__('Reward multiplier should typically be between 0 and 10'));
		}
	},
	
	max_redeem_pct: function(frm) {
		// Validate percentage
		if (frm.doc.max_redeem_pct < 0 || frm.doc.max_redeem_pct > 100) {
			frappe.msgprint(__('Max redeem percentage must be between 0 and 100'));
			frm.set_value('max_redeem_pct', 25);
		}
	}
});
