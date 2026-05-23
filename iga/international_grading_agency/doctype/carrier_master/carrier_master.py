from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document


class CarrierMaster(Document):
    def validate(self):
        if self.carrier_code:
            self.carrier_code = self.carrier_code.upper().replace(" ", "_")
