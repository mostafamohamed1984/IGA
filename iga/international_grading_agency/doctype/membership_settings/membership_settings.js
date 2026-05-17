frappe.ui.form.on('Membership Settings', {
	refresh: function(frm) {
		// Single DocType indicator
		frm.dashboard.add_indicator(__('System-wide Membership Configuration'), 'blue');
		
		// Display key settings
		if (frm.doc.earn_rate) {
			frm.dashboard.add_indicator(__('Earn Rate: {0} pts/EGP', [frm.doc.earn_rate]), 'green');
		}
		if (frm.doc.point_value) {
			frm.dashboard.add_indicator(__('Point Value: {0} EGP/pt', [frm.doc.point_value]), 'orange');
		}
		if (frm.doc.point_expiry_months) {
			frm.dashboard.add_indicator(__('Points Expire: {0} months', [frm.doc.point_expiry_months]), 'red');
		}
		
		// Rewards calculator
		frm.add_custom_button(__('Calculate Rewards Example'), function() {
			show_rewards_calculator(frm);
		});
		
		// Validation warnings
		if (frm.doc.earn_rate && frm.doc.point_value) {
			let effective_discount = (frm.doc.earn_rate * frm.doc.point_value) * 100;
			if (effective_discount > 10) {
				frappe.msgprint({
					title: __('Warning'),
					message: __('Current settings result in {0}% effective discount. Consider adjusting rates.', 
						[effective_discount.toFixed(2)]),
					indicator: 'orange'
				});
			}
		}
	},
	
	earn_rate: function(frm) {
		// Validate earn rate
		if (frm.doc.earn_rate < 0 || frm.doc.earn_rate > 1) {
			frappe.msgprint(__('Earn rate should typically be between 0 and 1'));
		}
		
		// Show effective discount
		if (frm.doc.point_value) {
			let effective_discount = (frm.doc.earn_rate * frm.doc.point_value) * 100;
			frappe.show_alert({
				message: __('Effective discount: {0}%', [effective_discount.toFixed(2)]),
				indicator: effective_discount > 10 ? 'orange' : 'green'
			});
		}
	},
	
	point_value: function(frm) {
		// Validate point value
		if (frm.doc.point_value < 0 || frm.doc.point_value > 10) {
			frappe.msgprint(__('Point value should typically be between 0 and 10 EGP'));
		}
		
		// Show effective discount
		if (frm.doc.earn_rate) {
			let effective_discount = (frm.doc.earn_rate * frm.doc.point_value) * 100;
			frappe.show_alert({
				message: __('Effective discount: {0}%', [effective_discount.toFixed(2)]),
				indicator: effective_discount > 10 ? 'orange' : 'green'
			});
		}
	},
	
	point_expiry_months: function(frm) {
		// Validate expiry period
		if (frm.doc.point_expiry_months < 1 || frm.doc.point_expiry_months > 60) {
			frappe.msgprint(__('Point expiry should typically be between 1 and 60 months'));
		}
	},
	
	downgrade_grace_days: function(frm) {
		// Validate grace period
		if (frm.doc.downgrade_grace_days < 0 || frm.doc.downgrade_grace_days > 365) {
			frappe.msgprint(__('Grace period should typically be between 0 and 365 days'));
		}
	},
	
	min_redeem_points: function(frm) {
		// Validate minimum redeem
		if (frm.doc.min_redeem_points < 0) {
			frappe.msgprint(__('Minimum redeem points cannot be negative'));
			frm.set_value('min_redeem_points', 100);
		}
	}
});

function show_rewards_calculator(frm) {
	let d = new frappe.ui.Dialog({
		title: __('Rewards Calculator'),
		fields: [
			{
				fieldtype: 'Currency',
				fieldname: 'invoice_amount',
				label: 'Invoice Amount (EGP)',
				reqd: 1,
				default: 1000
			},
			{
				fieldtype: 'Float',
				fieldname: 'plan_multiplier',
				label: 'Plan Multiplier',
				reqd: 1,
				default: 1.0,
				description: 'From Membership Plan'
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
			let invoice_amount = d.get_value('invoice_amount');
			let plan_multiplier = d.get_value('plan_multiplier');
			
			let base_points = invoice_amount * frm.doc.earn_rate;
			let total_points = base_points * plan_multiplier;
			let redemption_value = total_points * frm.doc.point_value;
			let effective_discount = (redemption_value / invoice_amount) * 100;
			
			let html = `
				<table class="table table-bordered">
					<tr><th>Invoice Amount</th><td>${invoice_amount.toFixed(2)} EGP</td></tr>
					<tr><th>Base Points Earned</th><td>${base_points.toFixed(2)}</td></tr>
					<tr><th>Plan Multiplier</th><td>${plan_multiplier}x</td></tr>
					<tr><th>Total Points Earned</th><td><strong>${total_points.toFixed(2)}</strong></td></tr>
					<tr><th>Redemption Value</th><td>${redemption_value.toFixed(2)} EGP</td></tr>
					<tr><th>Effective Discount</th><td><strong>${effective_discount.toFixed(2)}%</strong></td></tr>
				</table>
			`;
			
			d.fields_dict.result_html.$wrapper.html(html);
		}
	});
	d.show();
}
