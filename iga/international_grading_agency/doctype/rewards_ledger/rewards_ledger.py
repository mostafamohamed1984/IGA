import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import now_datetime


class RewardsLedger(Document):

    def autoname(self):
        self.ledger_no = frappe.model.naming.make_autoname("IGA-RWD-.YYYY.-.#####")
        self.name = self.ledger_no

    def validate(self):
        if self.entry_type == "Adjust" and not self.reason:
            frappe.throw(_("Reason is required for Adjust entries."))
        if self.expires_on and self.expired_offset_no:
            frappe.throw(_("Cannot set both Expires On and Expired Offset No."))

    def before_insert(self):
        self.transaction_date = now_datetime()
        self._compute_balance_after()

    def _compute_balance_after(self):
        """Compute running balance from previous entries for this member."""
        last = frappe.db.get_value(
            "Rewards Ledger",
            {"member": self.member, "docstatus": 1},
            "balance_after",
            order_by="transaction_date desc"
        )
        previous_balance = last if last is not None else 0
        self.balance_after = previous_balance + self.points
        if self.balance_after < 0:
            frappe.throw(_("Redemption exceeds available balance. Current balance: {0}").format(previous_balance))

    def before_submit(self):
        """Entries become immutable on submit."""
        pass

    def on_cancel(self):
        frappe.throw(_("Rewards Ledger entries cannot be cancelled."))

    @staticmethod
    def get_balance(member):
        """Return current points balance for a member."""
        last = frappe.db.get_value(
            "Rewards Ledger",
            {"member": member, "docstatus": 1},
            "balance_after",
            order_by="transaction_date desc"
        )
        return last or 0

    @staticmethod
    def add_entry(member, entry_type, points, source_doctype=None, source_document=None, notes=None):
        """Create, save, and submit a new ledger entry."""
        doc = frappe.new_doc("Rewards Ledger")
        doc.member = member
        doc.entry_type = entry_type
        doc.points = points
        doc.source_doctype = source_doctype
        doc.source_document = source_document
        doc.notes = notes
        doc.insert(ignore_permissions=True)
        doc.submit()
        return doc.name
