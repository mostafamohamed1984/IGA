import frappe
from frappe import _
from frappe.model.document import Document


class SubmissionWorkflowSettings(Document):
    
    def validate(self):
        self._validate_stages()
        self._validate_automation_rules()
    
    def _validate_stages(self):
        """Validate workflow stages."""
        if not self.stages:
            return
        
        # Check for duplicate stage codes
        codes = [s.stage_code for s in self.stages if s.stage_code]
        if len(codes) != len(set(codes)):
            frappe.throw(_("Duplicate stage codes found"))
        
        # Ensure at least one terminal stage
        terminal_stages = [s for s in self.stages if s.is_terminal]
        if not terminal_stages:
            frappe.throw(_("At least one stage must be marked as terminal"))
    
    def _validate_automation_rules(self):
        """Validate automation rules."""
        if not self.automation_rules:
            return
        
        for rule in self.automation_rules:
            if not rule.trigger_event:
                frappe.throw(_("Automation rule must have a trigger event"))
            
            if not rule.action_type:
                frappe.throw(_("Automation rule must have an action type"))
    
    @frappe.whitelist()
    def test_automation(self, submission, event):
        """Test automation rules against a submission."""
        if not submission:
            return {"error": "No submission provided"}
        
        sub_doc = frappe.get_doc("Submission", submission)
        
        # Find matching rules
        matching_rules = []
        for rule in self.automation_rules or []:
            if rule.trigger_event == event:
                matching_rules.append({
                    "rule_name": rule.rule_name,
                    "trigger_event": rule.trigger_event,
                    "action_type": rule.action_type,
                    "action_value": rule.action_value
                })
        
        if not matching_rules:
            return {
                "message": f"No automation rules found for event: {event}",
                "matching_rules": []
            }
        
        # Simulate rule execution
        results = []
        for rule in matching_rules:
            result = {
                "rule": rule["rule_name"],
                "action": rule["action_type"],
                "status": "Would Execute"
            }
            
            if rule["action_type"] == "Send Email":
                result["details"] = f"Would send email to: {sub_doc.customer}"
            elif rule["action_type"] == "Update Field":
                result["details"] = f"Would update field: {rule['action_value']}"
            elif rule["action_type"] == "Create Task":
                result["details"] = "Would create task"
            
            results.append(result)
        
        return {
            "submission": submission,
            "event": event,
            "matching_rules": len(matching_rules),
            "results": results
        }
