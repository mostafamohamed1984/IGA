from __future__ import unicode_literals
import frappe
from frappe import _
from frappe.model.document import Document

class ReferenceCodeSettings(Document):
    def validate(self):
        if self.padding < 1:
            frappe.throw(_("Sequence padding must be at least 1"))
        if self.starting_seq < 0:
            frappe.throw(_("Starting sequence must be 0 or greater"))
