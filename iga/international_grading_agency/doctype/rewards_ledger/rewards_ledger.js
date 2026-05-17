frappe.ui.form.on('Rewards Ledger', {
	refresh: function(frm) {
		// Entry type indicator
		let color = {
			'Earn': 'green',
			'Redeem': 'orange',
			'Adjust': 'blue',
			'Expire': 'red'
		}[frm.doc.entry_type] || 'grey';
		frm.dashboard.add_indicator(__('Type: {0}', [frm.doc.entry_type]), color);
		
		// Points display
		if (frm.doc.points) {
			let sign = frm.doc.points > 0 ? '+' : '';
			frm.dashboard.add_indicator(__('Points: {0}{1}', [sign, frm.doc.points]), 
				frm.doc.points > 0 ? 'green' : 'red');
		}
		
		// Balance display
		if (frm.doc.balance_after !== undefined) {
			frm.dashboard.add_indicator(__('Balance After: {0}', [frm.doc.balance_after]), 'blue');
		}
		
		// Source document link
		if (frm.doc.source_doctype && frm.doc.source_document) {
			frm.add_custom_button(__('View Source'), function() {
				frappe.set_route('Form', frm.doc.source_doctype, frm.doc.source_document);
			});
		}
		
		// Member balance summary
		if (frm.doc.member && !frm.is_new()) {
			frm.add_custom_button(__('View Member Balance'), function() {
				frappe.call({
					method: 'frappe.client.get_value',
					args: {
						doctype: 'Rewards Ledger',
						filters: {member: frm.doc.member},
						fieldname: 'balance_after',
						order_by: 'transaction_date desc',
						limit: 1
					},
					callback: function(r) {
						if (r.message) {
							frappe.msgprint({
								title: __('Current Balance'),
								message: __('Member {0} has {1} reward points', 
									[frm.doc.member, r.message.balance_after]),
								indicator: 'blue'
							});
						}
					}
				});
			});
		}
		
		// Read-only enforcement (ledger entries should not be edited)
		if (!frm.is_new()) {
			frm.set_read_only();
			frm.disable_save();
		}
	},
	
	entry_type: function(frm) {
		// Set points sign based on entry type
		if (frm.doc.entry_type === 'Earn' && frm.doc.points < 0) {
			frm.set_value('points', Math.abs(frm.doc.points));
		}
		if ((frm.doc.entry_type === 'Redeem' || frm.doc.entry_type === 'Expire') && frm.doc.points > 0) {
			frm.set_value('points', -Math.abs(frm.doc.points));
		}
	}
});
