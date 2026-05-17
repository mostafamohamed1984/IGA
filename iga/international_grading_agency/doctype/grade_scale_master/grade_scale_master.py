# Grade Scale Master — Python controller

import frappe
from frappe.model.document import Document


class GradeScaleMaster(Document):
    def validate(self):
        if self.numeric_grade < 1 or self.numeric_grade > 70:
            frappe.throw("Numeric Grade must be between 1 and 70.")
