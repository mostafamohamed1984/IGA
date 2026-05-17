import frappe
from frappe.model.document import Document


class RegistrySetDefinitions(Document):

    def validate(self):
        if not self.slots:
            frappe.throw("Registry Set Definitions must have at least one slot.")
        self._compute_derived_fields()
        self._validate_slot_nos()

    def _compute_derived_fields(self):
        self.slot_count = len(self.slots)
        self.max_score = sum(s.weight or 1.0 for s in self.slots)

    def _validate_slot_nos(self):
        seen = set()
        for s in self.slots:
            if s.slot_no in seen:
                frappe.throw(f"Duplicate Slot No. {s.slot_no} found in set '{self.set_code}'.")
            seen.add(s.slot_no)
