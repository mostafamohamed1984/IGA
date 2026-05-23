frappe.ui.form.on('Submission Workflow Settings', {
	refresh: function(frm) {
		// Single DocType indicator
		frm.dashboard.add_indicator(__('Submission Workflow Configuration'), 'blue');
		
		// Display workflow stages count
		if (frm.doc.stages && frm.doc.stages.length > 0) {
			frm.dashboard.add_indicator(__('Stages: {0}', [frm.doc.stages.length]), 'green');
		}
		
		// Display automation rules count
		if (frm.doc.automation_rules && frm.doc.automation_rules.length > 0) {
			frm.dashboard.add_indicator(__('Automation Rules: {0}', [frm.doc.automation_rules.length]), 'orange');
		}
		
		// Production stations count
		if (frm.doc.stations && frm.doc.stations.length > 0) {
			frm.dashboard.add_indicator(__('Stations: {0}', [frm.doc.stations.length]), 'blue');
		}
		
		// Transitions count
		if (frm.doc.transitions && frm.doc.transitions.length > 0) {
			frm.dashboard.add_indicator(__('Transitions: {0}', [frm.doc.transitions.length]), 'purple');
		}
		
		// Grader role
		if (frm.doc.default_grader_role) {
			frm.dashboard.add_indicator(__('Grader Role: {0}', [frm.doc.default_grader_role]), 'orange');
		}
		
		// Workflow diagram button
		frm.add_custom_button(__('View Workflow Diagram'), function() {
			show_workflow_diagram(frm);
		});
		
		// Test automation button
		frm.add_custom_button(__('Test Automation Rules'), function() {
			test_automation_rules(frm);
		});
	}
});

frappe.ui.form.on('Submission Workflow Stage', {
	stage_name: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// Auto-generate stage code from name
		if (row.stage_name && !row.stage_code) {
			let code = row.stage_name.toUpperCase().replace(/\s+/g, '_');
			frappe.model.set_value(cdt, cdn, 'stage_code', code);
		}
	},
	
	requires_approval: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// Show warning if approval required but no role specified
		if (row.requires_approval && !row.approval_role) {
			frappe.msgprint({
				title: __('Note'),
				message: __('Please specify an approval role for this stage'),
				indicator: 'orange'
			});
		}
	}
});

frappe.ui.form.on('Workflow Automation Rule', {
	trigger_event: function(frm, cdt, cdn) {
		let row = locals[cdt][cdn];
		
		// Show relevant fields based on trigger event
		if (row.trigger_event === 'Stage Change') {
			frappe.msgprint({
				title: __('Stage Change Trigger'),
				message: __('Specify the source and target stages for this rule'),
				indicator: 'blue'
			});
		}
	}
});

function show_workflow_diagram(frm) {
	if (!frm.doc.stages || frm.doc.stages.length === 0) {
		frappe.msgprint(__('No workflow stages defined'));
		return;
	}
	
	let html = '<div class="workflow-diagram" style="padding: 20px;">';
	html += '<h4>Submission Workflow</h4>';
	html += '<div style="display: flex; flex-direction: column; gap: 10px;">';
	
	frm.doc.stages.forEach(function(stage, idx) {
		let color = stage.is_terminal ? 'success' : (stage.requires_approval ? 'warning' : 'info');
		html += `
			<div class="alert alert-${color}" style="margin: 0;">
				<strong>${idx + 1}. ${stage.stage_name}</strong>
				${stage.stage_code ? ' (' + stage.stage_code + ')' : ''}
				${stage.requires_approval ? ' <span class="badge badge-warning">Requires Approval</span>' : ''}
				${stage.is_terminal ? ' <span class="badge badge-success">Terminal</span>' : ''}
				${stage.sla_hours ? '<br><small>SLA: ' + stage.sla_hours + ' hours</small>' : ''}
			</div>
		`;
		if (idx < frm.doc.stages.length - 1) {
			html += '<div style="text-align: center; color: #999;">↓</div>';
		}
	});
	
	html += '</div></div>';
	
	let d = new frappe.ui.Dialog({
		title: __('Workflow Diagram'),
		fields: [{
			fieldtype: 'HTML',
			fieldname: 'diagram_html'
		}],
		size: 'large'
	});
	d.fields_dict.diagram_html.$wrapper.html(html);
	d.show();
}

function test_automation_rules(frm) {
	if (!frm.doc.automation_rules || frm.doc.automation_rules.length === 0) {
		frappe.msgprint(__('No automation rules defined'));
		return;
	}
	
	let d = new frappe.ui.Dialog({
		title: __('Test Automation Rules'),
		fields: [
			{
				fieldtype: 'Link',
				fieldname: 'test_submission',
				label: 'Test Submission',
				options: 'Submission',
				reqd: 1
			},
			{
				fieldtype: 'Select',
				fieldname: 'test_event',
				label: 'Test Event',
				options: 'Stage Change\nItem Graded\nQC Approved\nPayment Received',
				reqd: 1
			},
			{
				fieldtype: 'Section Break'
			},
			{
				fieldtype: 'HTML',
				fieldname: 'result_html'
			}
		],
		primary_action_label: __('Test'),
		primary_action: function() {
			frappe.call({
				method: 'test_automation',
				doc: frm.doc,
				args: {
					submission: d.get_value('test_submission'),
					event: d.get_value('test_event')
				},
				callback: function(r) {
					if (r.message) {
						d.fields_dict.result_html.$wrapper.html(
							'<div class="alert alert-info">' + r.message + '</div>'
						);
					}
				}
			});
		}
	});
	d.show();
}
