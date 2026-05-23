import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class SubmissionItem(Document):

    def before_insert(self):
        self._generate_certificate_number()

    def _generate_certificate_number(self):
        if not self.certificate_number:
            submission_no = frappe.db.get_value("Submission", self.parent_submission, "submission_no")
            if not submission_no:
                frappe.throw(_("Parent Submission has no submission_no"))
            seq = frappe.db.count(
                "Submission Item",
                {"parent_submission": self.parent_submission}
            ) + 1
            self.certificate_number = f"{submission_no}-{seq:02d}"

    def validate(self):
        self._validate_result_consistency()
        self._auto_detect_result_type()
        self._validate_blocked_item()
        self._validate_qc_conditions()

    def _validate_result_consistency(self):
        disqualifying = any(
            p.results_in_no_grade for p in (self.problems or [])
        )
        if disqualifying and self.result_type == "Encapsulated":
            frappe.throw(_(
                "Certificate {0} has a disqualifying problem but Result Type is 'Encapsulated'. "
                "Change Result Type to 'Details' or 'Not Encapsulated'."
            ).format(self.certificate_number))

    def _auto_detect_result_type(self):
        if not self.result_type:
            has_disqualifying = any(p.results_in_no_grade for p in (self.problems or []))
            if has_disqualifying:
                self.result_type = "Details"

    def _validate_blocked_item(self):
        if self.is_blocked and not self.blocking_reason:
            frappe.throw(_("Blocking Reason is required when item is blocked."))

    def _validate_qc_conditions(self):
        if self.qc_status == "Failed" and not self.qc_failure_reason:
            frappe.throw(_("QC Failure Reason is required when QC status is 'Failed'."))
        if self.qc_status == "Rework" and not self.qc_rework_to:
            frappe.throw(_("QC Rework To is required when QC status is 'Rework'."))

    def record_grading(self, grade, graded_by=None):
        self.final_grade = grade
        self.graded_on = now_datetime()
        self.graded_by = graded_by or frappe.session.user
        self.station = "Grading"
        self.save(ignore_permissions=True)
        frappe.get_doc("Submission", self.parent_submission).on_update()

    def is_gradeable(self):
        has_disqualifying = any(p.results_in_no_grade for p in (self.problems or []))
        return not has_disqualifying

    def is_public_visible(self):
        if self.result_type not in ("Encapsulated", "Details"):
            return False
        parent_status = frappe.db.get_value("Submission", self.parent_submission, "status")
        return parent_status in ("Shipped", "Ready for Pickup", "Completed")
