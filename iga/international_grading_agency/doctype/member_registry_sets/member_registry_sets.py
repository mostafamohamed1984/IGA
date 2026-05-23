import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class MemberRegistrySets(Document):
    
    def autoname(self):
        self.member_set_no = frappe.model.naming.make_autoname("IGA-REG-.YYYY.-.#####")
        self.name = self.member_set_no
    
    def validate(self):
        self._validate_set_definition()
        self._validate_slots()
        self._compute_filled_count()
        self.last_updated = now_datetime()
        if not self.definition_version and self.set_definition:
            self.definition_version = frappe.db.get_value("Registry Set Definitions", self.set_definition, "version")
    
    def _validate_set_definition(self):
        """Ensure set definition exists and is active."""
        if not self.set_definition:
            return
        
        set_def = frappe.get_doc("Registry Set Definitions", self.set_definition)
        if set_def.status != "Active":
            frappe.throw(_("Registry Set Definition {0} is not active.").format(self.set_definition))
    
    def _compute_filled_count(self):
        if self.slots:
            self.filled_count = sum(1 for s in self.slots if s.graded_item)

    def _validate_slots(self):
        """Validate that filled slots match owned certificates."""
        if not self.slots:
            return
        
        for slot in self.slots:
            if slot.graded_item:
                # Verify certificate exists and belongs to member
                cert = frappe.db.get_value(
                    "Submission Item",
                    slot.graded_item,
                    ["name", "parent_submission", "result_type", "current_stage"],
                    as_dict=True
                )
                
                if not cert:
                    frappe.throw(_("Certificate {0} not found.").format(slot.graded_item))
                
                # Verify ownership
                submission = frappe.db.get_value("Submission", cert.parent_submission, "customer")
                if submission != self.member:
                    frappe.throw(_("Certificate {0} does not belong to member {1}.").format(
                        slot.graded_item, self.member
                    ))
                
                # Verify completion
                if cert.current_stage != "Completed":
                    frappe.throw(_("Certificate {0} is not completed yet.").format(slot.graded_item))
                
                if cert.result_type not in ["Encapsulated", "Details"]:
                    frappe.throw(_("Certificate {0} cannot be used in registry (Result Type: {1}).").format(
                        slot.graded_item, cert.result_type
                    ))
    
    @frappe.whitelist()
    def recalculate_score(self):
        """Recalculate registry set score based on filled slots."""
        if not self.set_definition or not self.slots:
            self.score = 0
            self.completion_pct = 0
            self.save(ignore_permissions=True)
            return {"score": 0, "completion_pct": 0}
        
        set_def = frappe.get_doc("Registry Set Definitions", self.set_definition)
        
        total_score = 0
        filled_slots = 0
        total_slots = len(self.slots)
        
        for slot in self.slots:
            if slot.graded_item and slot.grade:
                # Get numeric grade
                numeric_grade = frappe.db.get_value(
                    "Grade Scale Master",
                    {"scale_name": slot.grade},
                    "numeric_grade"
                ) or 0
                
                # Apply slot weight
                slot_score = numeric_grade * (slot.weight or 1.0)
                total_score += slot_score
                filled_slots += 1
                
                # Update slot score
                frappe.db.set_value("Member Registry Set Slot", slot.name, "slot_score", slot_score)
        
        # Calculate completion percentage
        completion_pct = (filled_slots / total_slots * 100) if total_slots > 0 else 0
        
        # Update member set
        self.score = total_score
        self.completion_pct = completion_pct
        self.last_scored_on = now_datetime()
        self.save(ignore_permissions=True)
        
        # Recalculate rank
        self._recalculate_rank()
        
        return {
            "score": total_score,
            "completion_pct": completion_pct,
            "rank": self.rank
        }
    
    def _recalculate_rank(self):
        """Calculate rank within the set definition."""
        if not self.set_definition:
            return
        
        # Get all member sets for this definition, ordered by score
        all_sets = frappe.get_all(
            "Member Registry Sets",
            filters={
                "set_definition": self.set_definition,
                "status": "Active"
            },
            fields=["name", "score"],
            order_by="score desc"
        )
        
        # Find rank
        rank = 1
        for idx, member_set in enumerate(all_sets, 1):
            if member_set.name == self.name:
                rank = idx
                break
        
        self.rank = rank
        self.db_update()
