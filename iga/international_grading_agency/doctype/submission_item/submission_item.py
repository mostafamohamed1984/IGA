import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class SubmissionItem(Document):

    def before_insert(self):
        self._generate_certificate_number()

    def _generate_certificate_number(self):
        if not self.certificate_number:
            # Get the submission_no from parent Submission
            submission_no = frappe.db.get_value("Submission", self.parent_submission, "submission_no")
            if not submission_no:
                frappe.throw(_("Parent Submission has no submission_no"))
            # Count existing items for this submission to get seq
            seq = frappe.db.count(
                "Submission Item",
                {"parent_submission": self.parent_submission}
            ) + 1
            self.certificate_number = f"{submission_no}-{seq:02d}"

    def validate(self):
        self._validate_result_consistency()
        self._auto_detect_result_type()

    def _validate_result_consistency(self):
        """If any problem results_in_no_grade, result_type must not be Encapsulated."""
        disqualifying = any(
            p.results_in_no_grade for p in (self.problems or [])
        )
        if disqualifying and self.result_type == "Encapsulated":
            frappe.throw(_(
                "Certificate {0} has a disqualifying problem but Result Type is 'Encapsulated'. "
                "Change Result Type to 'Details' or 'Not Encapsulated'."
            ).format(self.certificate_number))

    def _auto_detect_result_type(self):
        """Auto-set result_type to Details when any problem forces no grade."""
        if not self.result_type:
            has_disqualifying = any(p.results_in_no_grade for p in (self.problems or []))
            if has_disqualifying:
                self.result_type = "Details"

    def record_grading(self, grade, graded_by=None):
        """Set final grade and audit fields. Called by grading station."""
        self.final_grade = grade
        self.graded_on = now_datetime()
        self.graded_by = graded_by or frappe.session.user
        self.station = "Grading"
        self.save(ignore_permissions=True)
        # Cascade: update parent submission after grading
        frappe.get_doc("Submission", self.parent_submission).on_update()

    def is_gradeable(self):
        """Return True if this item can receive a final numeric grade."""
        has_disqualifying = any(p.results_in_no_grade for p in (self.problems or []))
        return not has_disqualifying

    def is_public_visible(self):
        """Return True if this item should be accessible via the Verify public API."""
        if self.result_type not in ("Encapsulated", "Details"):
            return False
        parent_status = frappe.db.get_value("Submission", self.parent_submission, "status")
        return parent_status in ("Shipped", "Ready for Pickup", "Completed")
