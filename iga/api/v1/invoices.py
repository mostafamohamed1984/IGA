import frappe
from frappe import _


def list_all():
    """GET /api/v1/invoices"""
    customer = _get_session_customer()
    invoices = frappe.get_all("Sales Invoice",
        filters={"customer": customer},
        fields=["name as invoice_no", "iga_invoice_type as type",
                "iga_submission as submission_no",
                "posting_date as date", "net_total as subtotal",
                "total_taxes_and_charges as vat",
                "grand_total as total", "status",
                "outstanding_amount as balance_due",
                "total_advance as down_payment_applied"],
        order_by="posting_date desc"
    )
    for inv in invoices:
        inv["credits_applied"] = 0
        inv["pdf_url"] = None
        inv["line_items"] = []
        inv["submission_no"] = inv.get("submission_no")
    return invoices


def get_detail(invoice_no):
    """GET /api/v1/invoices/{invoice_no}"""
    customer = _get_session_customer()
    inv = frappe.get_value("Sales Invoice", invoice_no, "*", as_dict=1)
    if not inv:
        frappe.throw(_("Invoice not found"), frappe.DoesNotExistError)
    if inv.customer != customer:
        frappe.throw(_("Access denied"), frappe.PermissionError)

    items = frappe.get_all("Sales Invoice Item",
        filters={"parent": invoice_no},
        fields=["item_name as description", "qty", "rate as unit_price",
                "amount as total"]
    )

    return {
        "invoice_no": inv.name,
        "type": inv.iga_invoice_type or "Sales Invoice",
        "submission_no": inv.iga_submission,
        "date": str(inv.posting_date) if inv.posting_date else "",
        "subtotal": inv.net_total or 0,
        "vat": inv.total_taxes_and_charges or 0,
        "total": inv.grand_total or 0,
        "status": _map_invoice_status(inv.status),
        "down_payment_applied": inv.total_advance or 0,
        "credits_applied": 0,
        "balance_due": inv.outstanding_amount or 0,
        "pdf_url": None,
        "line_items": items,
    }


def _map_invoice_status(frappe_status):
    mapping = {
        "Draft": "Pending",
        "Submitted": "Under Review",
        "Paid": "Paid",
        "Cancelled": "Cancelled",
        "Overdue": "Under Review",
    }
    return mapping.get(frappe_status, "Pending")


def _get_session_customer():
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Authentication required"), frappe.PermissionError)
    customer = frappe.db.get_value("Customer", {"email_id": user}, "name")
    if not customer:
        frappe.throw(_("No customer profile found"), frappe.PermissionError)
    return customer
