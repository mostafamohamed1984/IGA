frappe.ui.form.on('Price Guide', {
	refresh: function(frm) {
		// Status indicator
		if (frm.doc.status === 'Draft') {
			frm.dashboard.add_indicator(__('Draft - Not visible on website'), 'orange');
		} else if (frm.doc.status === 'Archived') {
			frm.dashboard.add_indicator(__('Archived'), 'red');
		}
		
		// Last updated display
		if (frm.doc.last_updated) {
			frm.dashboard.add_indicator(__('Updated: {0}', [frappe.datetime.str_to_user(frm.doc.last_updated)]), 'blue');
		}
		
		// Activate button
		if (frm.doc.status === 'Draft' && frm.doc.grade_values && frm.doc.grade_values.length > 0) {
			frm.add_custom_button(__('Activate'), function() {
				frm.set_value('status', 'Active');
				frm.save();
			}).addClass('btn-primary');
		}
		
		// Archive button
		if (frm.doc.status === 'Active') {
			frm.add_custom_button(__('Archive'), function() {
				frappe.confirm(
					__('Archive this price guide? It will no longer be visible on the website.'),
					function() {
						frm.set_value('status', 'Archived');
						frm.save();
					}
				);
			});
		}
		
		// View reference item
		if (frm.doc.reference_item) {
			frm.add_custom_button(__('View Reference Item'), function() {
				frappe.set_route('Form', 'Item Reference Catalog', frm.doc.reference_item);
			});
		}
		
		// View population data
		if (frm.doc.reference_item) {
			frm.add_custom_button(__('View Population'), function() {
				show_population_data(frm);
			});
		}
		
		// Price chart
		if (frm.doc.grade_values && frm.doc.grade_values.length > 0) {
			frm.add_custom_button(__('View Price Chart'), function() {
				show_price_chart(frm);
			});
		}
		
		// Sort grade values by numeric grade
		if (frm.doc.grade_values && frm.doc.grade_values.length > 1) {
			frm.add_custom_button(__('Sort by Grade'), function() {
				sort_grade_values(frm);
			});
		}
	},
	
	reference_item: function(frm) {
		// Auto-populate fields from reference item
		if (frm.doc.reference_item) {
			frappe.call({
				method: 'frappe.client.get',
				args: {
					doctype: 'Item Reference Catalog',
					name: frm.doc.reference_item
				},
				callback: function(r) {
					if (r.message) {
						let ref = r.message;
						
						// Auto-populate category
						if (!frm.doc.category) {
							let category = 'Modern';
							if (ref.collectible_type === 'Medal' || ref.collectible_type === 'Token') {
								category = 'Medals & Tokens';
							} else if (ref.year_ad && ref.year_ad < 1951) {
								category = 'Early Modern';
							}
							frm.set_value('category', category);
						}
						
						// Auto-populate other fields
						if (!frm.doc.country) frm.set_value('country', ref.country);
						if (!frm.doc.year) frm.set_value('year', ref.year_ad || ref.year_ah);
						if (!frm.doc.mint) frm.set_value('mint', ref.mint);
					}
				}
			});
		}
	}
});

frappe.ui.form.on('Price Guide Entry', {
	grade: function(frm, cdt, cdn) {
		// Auto-sort when grade changes
		setTimeout(function() {
			sort_grade_values(frm);
		}, 500);
	},
	
	market_value: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// Validate positive value
		if (row.market_value < 0) {
			frappe.msgprint(__('Market value cannot be negative'));
			frappe.model.set_value(cdt, cdn, 'market_value', 0);
		}
	}
});

function sort_grade_values(frm) {
	if (!frm.doc.grade_values || frm.doc.grade_values.length <= 1) {
		return;
	}
	
	// Get numeric grades for sorting
	let grades_with_numeric = [];
	let promises = [];
	
	frm.doc.grade_values.forEach(function(entry) {
		let promise = frappe.call({
			method: 'frappe.client.get_value',
			args: {
				doctype: 'Grade Scale Master',
				filters: {scale_name: entry.grade},
				fieldname: 'numeric_grade'
			},
			async: false
		});
		promises.push(promise);
	});
	
	Promise.all(promises).then(function(results) {
		// Build array with numeric grades
		frm.doc.grade_values.forEach(function(entry, idx) {
			grades_with_numeric.push({
				entry: entry,
				numeric_grade: results[idx].message ? results[idx].message.numeric_grade : 0
			});
		});
		
		// Sort by numeric grade descending
		grades_with_numeric.sort(function(a, b) {
			return b.numeric_grade - a.numeric_grade;
		});
		
		// Rebuild table
		frm.clear_table('grade_values');
		grades_with_numeric.forEach(function(item) {
			let row = frm.add_child('grade_values');
			row.grade = item.entry.grade;
			row.designation = item.entry.designation;
			row.market_value = item.entry.market_value;
			row.currency = item.entry.currency;
		});
		
		frm.refresh_field('grade_values');
		frappe.show_alert({message: __('Grade values sorted'), indicator: 'green'});
	});
}

function show_population_data(frm) {
	frappe.call({
		method: 'iga.international_grading_agency.api.population.get_population_by_reference',
		args: {
			reference_code: frm.doc.reference_item
		},
		callback: function(r) {
			if (r.message) {
				let pop = r.message;
				let html = '<h4>Population Data</h4>';
				html += '<table class="table table-bordered">';
				html += '<tr><th>Grade</th><th>Population</th></tr>';
				
				for (let grade in pop.by_grade) {
					html += `<tr><td>${grade}</td><td>${pop.by_grade[grade]}</td></tr>`;
				}
				
				html += '</table>';
				html += `<p><small>Last Updated: ${pop.last_updated || 'N/A'}</small></p>`;
				
				frappe.msgprint({
					title: __('Population Data'),
					message: html,
					indicator: 'blue'
				});
			}
		}
	});
}

function show_price_chart(frm) {
	if (!frm.doc.grade_values || frm.doc.grade_values.length === 0) {
		return;
	}
	
	// Prepare chart data
	let labels = [];
	let values = [];
	
	frm.doc.grade_values.forEach(function(entry) {
		let label = entry.grade;
		if (entry.designation) label += ' ' + entry.designation;
		labels.push(label);
		values.push(entry.market_value);
	});
	
	let d = new frappe.ui.Dialog({
		title: __('Price Chart'),
		fields: [{
			fieldtype: 'HTML',
			fieldname: 'chart_html'
		}],
		size: 'large'
	});
	
	d.show();
	
	// Simple bar chart HTML
	let max_value = Math.max(...values);
	let html = '<div style="padding: 20px;">';
	
	labels.forEach(function(label, idx) {
		let value = values[idx];
		let width = (value / max_value) * 100;
		html += `
			<div style="margin-bottom: 10px;">
				<div style="font-weight: bold; margin-bottom: 3px;">${label}</div>
				<div style="background: #2490ef; height: 30px; width: ${width}%; 
				            display: flex; align-items: center; padding-left: 10px; color: white;">
					${value.toFixed(2)} EGP
				</div>
			</div>
		`;
	});
	
	html += '</div>';
	d.fields_dict.chart_html.$wrapper.html(html);
}
