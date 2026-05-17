// Copyright (c) 2026, IGA and contributors
// For license information, please see license.txt

frappe.ui.form.on('Membership Subscriptions', {
	refresh: function(frm) {
		// Add custom buttons based on status
		if (frm.doc.status === 'Active' && !frm.doc.__islocal) {
			frm.add_custom_button(__('Cancel Subscription'), function() {
				frappe.confirm(
					__('Are you sure you want to cancel this subscription?'),
					function() {
						show_cancellation_dialog(frm);
					}
				);
			});

			frm.add_custom_button(__('Renew Subscription'), function() {
				renew_subscription(frm);
			});

			frm.add_custom_button(__('Add Credits'), function() {
				show_add_credits_dialog(frm);
			});
		}

		if (frm.doc.status === 'Expired' && !frm.doc.__islocal) {
			frm.add_custom_button(__('Reactivate'), function() {
				renew_subscription(frm);
			});
		}

		// Show expiry warning
		if (frm.doc.status === 'Active' && frm.doc.end_date) {
			const days_remaining = frappe.datetime.get_day_diff(frm.doc.end_date, frappe.datetime.nowdate());
			if (days_remaining <= 30 && days_remaining > 0) {
				frm.dashboard.add_comment(
					__('Subscription expires in {0} days', [days_remaining]),
					'orange',
					true
				);
			} else if (days_remaining <= 0) {
				frm.dashboard.add_comment(
					__('Subscription has expired'),
					'red',
					true
				);
			}
		}

		// Show credits remaining
		if (frm.doc.credits_remaining !== undefined) {
			const color = frm.doc.credits_remaining > 0 ? 'green' : 'red';
			frm.dashboard.add_comment(
				__('Credits Remaining: <b>{0}</b>', [frm.doc.credits_remaining]),
				color,
				true
			);
		}

		// Color code status
		if (frm.doc.status) {
			const status_colors = {
				'Pending': 'orange',
				'Active': 'green',
				'Expired': 'red',
				'Cancelled': 'red'
			};
			frm.set_df_property('status', 'description',
				`<span style="color: ${status_colors[frm.doc.status] || 'black'}; font-weight: bold;">${frm.doc.status}</span>`
			);
		}

		// Show plan details
		if (frm.doc.plan) {
			show_plan_details(frm);
		}
	},

	onload: function(frm) {
		// Set filters
		frm.set_query('customer', function() {
			return {
				filters: {
					'disabled': 0
				}
			};
		});

		frm.set_query('plan', function() {
			return {
				filters: {
					'status': 'Active'
				}
			};
		});

		// Auto-set dates if new
		if (frm.doc.__islocal && !frm.doc.start_date) {
			frm.set_value('start_date', frappe.datetime.nowdate());
		}
	},

	plan: function(frm) {
		// Auto-fetch plan details
		if (frm.doc.plan) {
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Membership Plans',
					name: frm.doc.plan
				},
				callback: function(r) {
					if (r.message) {
						const plan = r.message;
						
						// Set credits
						if (frm.doc.__islocal) {
							frm.set_value('credits_remaining', plan.included_credits || 0);
						}

						// Show plan info
						frappe.show_alert({
							message: __('Plan: {0} - Credits: {1}', [plan.plan_name, plan.included_credits]),
							indicator: 'blue'
						});
					}
				}
			});
		}
	},

	billing_period: function(frm) {
		// Calculate end date based on billing period
		if (frm.doc.start_date && frm.doc.billing_period) {
			calculate_end_date(frm);
		}
	},

	start_date: function(frm) {
		// Calculate end date
		if (frm.doc.billing_period) {
			calculate_end_date(frm);
		}
	},

	customer: function(frm) {
		// Check for existing active subscriptions
		if (frm.doc.customer && frm.doc.__islocal) {
			frappe.call({
				method: 'frappe.client.get_list',
				args: {
					doctype: 'Membership Subscriptions',
					filters: {
						'customer': frm.doc.customer,
						'status': 'Active'
					},
					fields: ['name', 'plan', 'end_date']
				},
				callback: function(r) {
					if (r.message && r.message.length > 0) {
						frappe.msgprint({
							title: __('Existing Subscription Found'),
							message: __('Customer already has an active subscription: {0}', [r.message[0].name]),
							indicator: 'orange'
						});
					}
				}
			});
		}
	},

	before_save: function(frm) {
		// Auto-update status based on dates
		if (frm.doc.start_date && frm.doc.end_date) {
			const today = frappe.datetime.nowdate();
			if (frm.doc.status !== 'Cancelled') {
				if (today < frm.doc.start_date) {
					frm.set_value('status', 'Pending');
				} else if (today >= frm.doc.start_date && today <= frm.doc.end_date) {
					frm.set_value('status', 'Active');
				} else if (today > frm.doc.end_date) {
					frm.set_value('status', 'Expired');
				}
			}
		}
	}
});

// Helper Functions
function calculate_end_date(frm) {
	if (!frm.doc.start_date || !frm.doc.billing_period) return;

	let end_date;
	if (frm.doc.billing_period === 'Monthly') {
		end_date = frappe.datetime.add_months(frm.doc.start_date, 1);
	} else if (frm.doc.billing_period === 'Annual') {
		end_date = frappe.datetime.add_months(frm.doc.start_date, 12);
	}

	// Subtract 1 day for inclusive expiry
	end_date = frappe.datetime.add_days(end_date, -1);
	frm.set_value('end_date', end_date);
}

function show_plan_details(frm) {
	frappe.call({
		method: 'frappe.client.get',
		args: {
			doctype: 'Membership Plans',
			name: frm.doc.plan
		},
		callback: function(r) {
			if (r.message) {
				const plan = r.message;
				let html = '<div class="alert alert-info">';
				html += `<h5>${plan.plan_name}</h5>`;
				html += `<p><b>Plan Code:</b> ${plan.plan_code}</p>`;
				if (frm.doc.billing_period === 'Monthly') {
					html += `<p><b>Fee:</b> EGP ${plan.monthly_fee}</p>`;
				} else {
					html += `<p><b>Fee:</b> EGP ${plan.annual_fee}</p>`;
				}
				html += `<p><b>Included Credits:</b> ${plan.included_credits}</p>`;
				html += `<p><b>Reward Multiplier:</b> ${plan.reward_multiplier}x</p>`;
				html += `<p><b>Max Redeem:</b> ${plan.max_redeem_pct}%</p>`;
				if (plan.feature_bullets) {
					html += `<p><b>Features:</b><br>${plan.feature_bullets.replace(/\n/g, '<br>')}</p>`;
				}
				html += '</div>';
				frm.set_df_property('plan', 'description', html);
			}
		}
	});
}

function show_cancellation_dialog(frm) {
	const dialog = new frappe.ui.Dialog({
		title: __('Cancel Subscription'),
		fields: [
			{
				fieldtype: 'Small Text',
				fieldname: 'cancellation_reason',
				label: __('Reason for Cancellation'),
				reqd: 1
			},
			{
				fieldtype: 'Check',
				fieldname: 'refund_credits',
				label: __('Refund Remaining Credits'),
				default: 0
			}
		],
		primary_action_label: __('Cancel Subscription'),
		primary_action: function(values) {
			frm.set_value('status', 'Cancelled');
			frm.set_value('cancelled_on', frappe.datetime.nowdate());
			frm.set_value('cancellation_reason', values.cancellation_reason);
			
			if (values.refund_credits) {
				// TODO: Implement credit refund logic
				frappe.msgprint(__('Credit refund will be processed'));
			}
			
			frm.save();
			dialog.hide();
		}
	});
	dialog.show();
}

function renew_subscription(frm) {
	frappe.confirm(
		__('Renew subscription for another {0}?', [frm.doc.billing_period]),
		function() {
			frappe.call({
				method: 'iga.international_grading_agency.doctype.membership_subscriptions.membership_subscriptions.renew_subscription',
				args: {
					subscription_name: frm.doc.name
				},
				callback: function(r) {
					if (r.message) {
						frappe.msgprint(__('Subscription renewed: {0}', [r.message]));
						frm.reload_doc();
					}
				}
			});
		}
	);
}

function show_add_credits_dialog(frm) {
	const dialog = new frappe.ui.Dialog({
		title: __('Add Credits'),
		fields: [
			{
				fieldtype: 'Int',
				fieldname: 'credits_to_add',
				label: __('Credits to Add'),
				reqd: 1,
				default: 0
			},
			{
				fieldtype: 'Small Text',
				fieldname: 'reason',
				label: __('Reason'),
				reqd: 1
			}
		],
		primary_action_label: __('Add Credits'),
		primary_action: function(values) {
			if (values.credits_to_add <= 0) {
				frappe.msgprint(__('Please enter a positive number'));
				return;
			}

			const new_balance = (frm.doc.credits_remaining || 0) + values.credits_to_add;
			frm.set_value('credits_remaining', new_balance);
			frm.save();

			// TODO: Create Rewards Ledger entry
			frappe.show_alert({
				message: __('Added {0} credits. New balance: {1}', [values.credits_to_add, new_balance]),
				indicator: 'green'
			});

			dialog.hide();
		}
	});
	dialog.show();
}
