import frappe
from frappe import _
from frappe.model.document import Document


class IGAGradingSettings(Document):

    def validate(self):
        self._validate_scoring_components()
        self._validate_weight_factors()

    def _validate_scoring_components(self):
        """Validate that scoring components sum to 100% for both types."""
        if not self.scoring_components:
            return

        unc_total = sum(c.weight_uncirculated or 0 for c in self.scoring_components)
        circ_total = sum(c.weight_circulated or 0 for c in self.scoring_components)

        if abs(unc_total - 100) > 0.01:
            frappe.throw(_("Uncirculated weights must sum to 100% (currently {0}%)").format(unc_total))

        if abs(circ_total - 100) > 0.01:
            frappe.throw(_("Circulated weights must sum to 100% (currently {0}%)").format(circ_total))

    def _validate_weight_factors(self):
        """Validate that new weight factor groups sum to 100%."""
        unc_fields = [self.weight_wear_unc, self.weight_surface_unc, self.weight_strike_unc,
                      self.weight_luster_unc, self.weight_eye_appeal_unc, self.weight_rim_edge_unc]
        if any(unc_fields):
            unc_total = sum(v or 0 for v in unc_fields)
            if abs(unc_total - 100) > 0.01:
                frappe.throw(_("Uncirculated weight factors must sum to 100% (currently {0}%)").format(unc_total))

        circ_fields = [self.weight_wear_circ, self.weight_surface_circ, self.weight_strike_circ,
                       self.weight_luster_circ, self.weight_eye_appeal_circ, self.weight_rim_edge_circ]
        if any(circ_fields):
            circ_total = sum(v or 0 for v in circ_fields)
            if abs(circ_total - 100) > 0.01:
                frappe.throw(_("Circulated weight factors must sum to 100% (currently {0}%)").format(circ_total))
