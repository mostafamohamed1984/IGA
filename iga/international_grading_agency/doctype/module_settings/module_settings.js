frappe.ui.form.on('Module Settings', {
	refresh: function(frm) {
		// Single DocType indicator
		frm.dashboard.add_indicator(__('Module-wide Configuration'), 'blue');
		
		// Reference code settings display
		if (frm.doc.auto_generate_on_active) {
			frm.dashboard.add_indicator(__('Auto-generate codes enabled'), 'green');
		}
		if (frm.doc.code_format_template) {
			frm.dashboard.add_indicator(__('Format: {0}', [frm.doc.code_format_template]), 'blue');
		}
		
		// Registry formula validation
		validate_registry_weights(frm);
		
		// Test reference code generation
		frm.add_custom_button(__('Test Code Generation'), function() {
			test_code_generation(frm);
		});
		
		// Calculate registry points example
		frm.add_custom_button(__('Test Registry Formula'), function() {
			test_registry_formula(frm);
		});
		
		// Migration warnings for deprecated sections
		if (frm.doc.country_configuration && frm.doc.country_configuration.length > 0) {
			frm.dashboard.add_indicator(__('Warning: Country Configuration is deprecated. Migrate to Country Master.'), 'red');
			frm.add_custom_button(__('Migrate Countries'), function() {
				migrate_countries(frm);
			}, __('Migration'));
		}
		
		if (frm.doc.grade_scoring_configuration && frm.doc.grade_scoring_configuration.length > 0) {
			frm.dashboard.add_indicator(__('Warning: Grade Scoring Configuration is deprecated. Use IGA Grading Settings.'), 'orange');
		}
	},
	
	code_format_template: function(frm) {
		// Validate template format
		if (frm.doc.code_format_template) {
			let valid_tokens = ['{TYPE}', '{CTY}', '{YYYY}', '{YY}', '{SEQ3}', '{SEQ4}', '{SEQ5}'];
			let template = frm.doc.code_format_template;
			let has_valid_token = false;
			
			valid_tokens.forEach(function(token) {
				if (template.includes(token)) has_valid_token = true;
			});
			
			if (!has_valid_token) {
				frappe.msgprint({
					title: __('Invalid Template'),
					message: __('Template must include at least one valid token: {0}', [valid_tokens.join(', ')]),
					indicator: 'red'
				});
			} else {
				frappe.show_alert({
					message: __('Valid template format'),
					indicator: 'green'
				});
			}
		}
	},
	
	grade_weight: function(frm) {
		validate_registry_weights(frm);
	},
	
	population_weight: function(frm) {
		validate_registry_weights(frm);
	},
	
	value_weight: function(frm) {
		validate_registry_weights(frm);
	}
});

function validate_registry_weights(frm) {
	let grade_weight = frm.doc.grade_weight || 0;
	let population_weight = frm.doc.population_weight || 0;
	let value_weight = frm.doc.value_weight || 0;
	
	let total = grade_weight + population_weight + value_weight;
	
	if (total === 0) {
		frappe.msgprint({
			title: __('Warning'),
			message: __('All registry weights are zero. Registry points will not be calculated.'),
			indicator: 'orange'
		});
	} else {
		frappe.show_alert({
			message: __('Registry formula: Grade({0}) + Population({1}) + Value({2})', 
				[grade_weight, population_weight, value_weight]),
			indicator: 'blue'
		});
	}
}

function test_code_generation(frm) {
	let d = new frappe.ui.Dialog({
		title: __('Test Reference Code Generation'),
		fields: [
			{
				fieldtype: 'Select',
				fieldname: 'collectible_type',
				label: 'Collectible Type',
				options: 'Coin\nMedal\nToken\nBanknote\nPostcard\nCollectible Card',
				reqd: 1,
				default: 'Coin'
			},
			{
				fieldtype: 'Data',
				fieldname: 'country_code',
				label: 'Country Code',
				reqd: 1,
				default: 'EG',
				description: '2-3 letter code'
			},
			{
				fieldtype: 'Int',
				fieldname: 'year',
				label: 'Year',
				reqd: 1,
				default: new Date().getFullYear()
			},
			{
				fieldtype: 'Section Break'
			},
			{
				fieldtype: 'HTML',
				fieldname: 'result_html'
			}
		],
		primary_action_label: __('Generate'),
		primary_action: function() {
			let values = d.get_values();
			
			frappe.call({
				method: 'iga.international_grading_agency.doctype.module_settings.module_settings.generate_reference_code',
				args: {
					collectible_type: values.collectible_type,
					country_code: values.country_code,
					year: values.year
				},
				callback: function(r) {
					if (r.message) {
						let html = `
							<div class="alert alert-success">
								<h5>Generated Reference Code</h5>
								<p style="font-size: 18px; font-family: monospace; font-weight: bold;">${r.message}</p>
								<hr>
								<small>Template: ${frm.doc.code_format_template}</small>
							</div>
						`;
						d.fields_dict.result_html.$wrapper.html(html);
					}
				}
			});
		}
	});
	d.show();
}

function test_registry_formula(frm) {
	let d = new frappe.ui.Dialog({
		title: __('Test Registry Points Formula'),
		fields: [
			{
				fieldtype: 'Int',
				fieldname: 'grade_score',
				label: 'Grade Score (1-70)',
				reqd: 1,
				default: 65
			},
			{
				fieldtype: 'Int',
				fieldname: 'population',
				label: 'Population Count',
				reqd: 1,
				default: 100
			},
			{
				fieldtype: 'Currency',
				fieldname: 'market_value',
				label: 'Market Value (EGP)',
				reqd: 1,
				default: 1000
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
			let values = d.get_values();
			
			let grade_component = values.grade_score * frm.doc.grade_weight;
			let population_component = (1000 / Math.max(values.population, 1)) * frm.doc.population_weight;
			let value_component = (values.market_value / 100) * frm.doc.value_weight;
			let total_points = grade_component + population_component + value_component;
			
			let html = `
				<table class="table table-bordered">
					<tr>
						<th>Component</th>
						<th>Calculation</th>
						<th>Points</th>
					</tr>
					<tr>
						<td>Grade</td>
						<td>${values.grade_score} × ${frm.doc.grade_weight}</td>
						<td>${grade_component.toFixed(2)}</td>
					</tr>
					<tr>
						<td>Population</td>
						<td>(1000 / ${values.population}) × ${frm.doc.population_weight}</td>
						<td>${population_component.toFixed(2)}</td>
					</tr>
					<tr>
						<td>Value</td>
						<td>(${values.market_value} / 100) × ${frm.doc.value_weight}</td>
						<td>${value_component.toFixed(2)}</td>
					</tr>
					<tr>
						<th colspan="2">Total Registry Points</th>
						<th>${total_points.toFixed(2)}</th>
					</tr>
				</table>
			`;
			
			d.fields_dict.result_html.$wrapper.html(html);
		}
	});
	d.show();
}

function migrate_countries(frm) {
	frappe.confirm(
		__('This will migrate all countries from Country Configuration to Country Master. Continue?'),
		function() {
			frappe.call({
				method: 'iga.international_grading_agency.doctype.module_settings.module_settings.migrate_countries_to_master',
				callback: function(r) {
					if (r.message) {
						frappe.msgprint({
							title: __('Migration Complete'),
							message: __('Migrated {0} countries to Country Master', [r.message.count]),
							indicator: 'green'
						});
						frm.reload_doc();
					}
				}
			});
		}
	);
}
