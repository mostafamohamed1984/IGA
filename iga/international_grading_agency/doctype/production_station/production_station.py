from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document


class ProductionStation(Document):
    def validate(self):
        if self.station_code:
            self.station_code = self.station_code.upper().replace(" ", "_")
