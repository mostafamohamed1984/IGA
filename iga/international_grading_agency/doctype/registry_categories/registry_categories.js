frappe.ui.form.on('Registry Categories', {
	refresh: function(frm) {
		// Status indicator
		if (frm.doc.status === 'Retired') {
			frm.dashboard.add_indicator(__('Retired - Not available for new registry sets'), 'red');
		}
		
		// Sort order display
		if (frm.doc.sort_order !== undefined) {
			frm.dashboard.add_indicator(__('Sort Order: {0}', [frm.doc.sort_order]), 'blue');
		}
		
		// Add button to view registry sets in this category
		if (!frm.is_new()) {
			frm.add_custom_button(__('View Registry Sets'), function() {
				frappe.route_options = {
					'category': frm.doc.name
				};
				frappe.set_route('List', 'Registry Set Definitions');
			});
		}
		
		// Reorder button
		frm.add_custom_button(__('Reorder Categories'), function() {
			show_reorder_dialog();
		});
	},
	
	category_code: function(frm) {
		// Auto-uppercase category codes
		if (frm.doc.category_code) {
			frm.set_value('category_code', frm.doc.category_code.toUpperCase());
		}
	}
});

function show_reorder_dialog() {
	frappe.call({
		method: 'frappe.client.get_list',
		args: {
			doctype: 'Registry Categories',
			fields: ['name', 'category_name', 'sort_order'],
			filters: {status: 'Active'},
			order_by: 'sort_order asc',
			limit_page_length: 100
		},
		callback: function(r) {
			if (r.message) {
				let categories = r.message;
				let html = '<div class="category-reorder">';
				html += '<p>Drag to reorder categories:</p>';
				html += '<ul id="sortable-categories" style="list-style: none; padding: 0;">';
				
				categories.forEach(function(cat) {
					html += `
						<li data-name="${cat.name}" style="padding: 10px; margin: 5px 0; background: #f5f5f5; cursor: move; border-radius: 4px;">
							<span class="indicator blue"></span> ${cat.category_name} (${cat.name})
						</li>
					`;
				});
				
				html += '</ul></div>';
				
				let d = new frappe.ui.Dialog({
					title: __('Reorder Categories'),
					fields: [{
						fieldtype: 'HTML',
						fieldname: 'reorder_html'
					}],
					primary_action_label: __('Save Order'),
					primary_action: function() {
						let new_order = [];
						$('#sortable-categories li').each(function(idx) {
							new_order.push({
								name: $(this).data('name'),
								sort_order: idx
							});
						});
						
						frappe.call({
							method: 'frappe.client.bulk_update',
							args: {
								docs: new_order.map(item => ({
									doctype: 'Registry Categories',
									name: item.name,
									sort_order: item.sort_order
								}))
							},
							callback: function() {
								frappe.show_alert({message: __('Category order updated'), indicator: 'green'});
								d.hide();
								cur_frm.reload_doc();
							}
						});
					}
				});
				
				d.fields_dict.reorder_html.$wrapper.html(html);
				d.show();
				
				// Enable drag-and-drop
				$('#sortable-categories').sortable({
					placeholder: 'ui-state-highlight',
					cursor: 'move'
				});
			}
		}
	});
}
