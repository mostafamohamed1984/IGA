import frappe
from frappe import _


def create_ticket():
    """POST /api/v1/support/tickets"""
    data = frappe.local.form_dict
    customer = None
    user = frappe.session.user
    if user != "Guest":
        customer = frappe.db.get_value("Customer", {"email_id": user}, "name")

    # Create Issue (native ERPNext DocType) with custom fields
    issue = frappe.get_doc({
        "doctype": "Issue",
        "subject": data.get("subject", ""),
        "description": data.get("body", ""),
        "customer": customer,
        "iga_ticket_type": data.get("type", "General"),
        "iga_guest_name": data.get("guest_name") if not customer else None,
        "iga_guest_email": data.get("guest_email") if not customer else None,
        "iga_guest_phone": data.get("guest_phone") if not customer else None,
        "iga_related_certificate": data.get("related_certificate"),
        "iga_related_submission": data.get("related_submission"),
        "status": "Open",
    })
    issue.insert(ignore_permissions=True)

    return {
        "ticket_no": issue.name,
        "status": issue.status,
        "subject": issue.subject,
        "type": issue.iga_ticket_type,
        "last_updated": str(issue.modified),
    }


def list_tickets():
    """GET /api/v1/support/tickets"""
    customer = _get_session_customer()
    tickets = frappe.get_all("Issue",
        filters={"customer": customer},
        fields=["name as ticket_no", "subject", "iga_ticket_type as type",
                "status", "iga_related_submission as related_submission",
                "iga_related_certificate as related_certificate",
                "modified as last_updated"],
        order_by="modified desc"
    )
    return tickets


def get_ticket(ticket_no):
    """GET /api/v1/support/tickets/{ticket_no}"""
    customer = _get_session_customer()
    ticket = frappe.get_value("Issue", ticket_no, "*", as_dict=1)
    if not ticket:
        frappe.throw(_("Ticket not found"), frappe.DoesNotExistError)
    if ticket.customer != customer:
        frappe.throw(_("Access denied"), frappe.PermissionError)

    messages = []
    if ticket.description:
        messages.append({
            "id": f"{ticket_no}-1",
            "sender": "customer",
            "body": ticket.description,
            "created_at": str(ticket.creation),
        })

    return {
        "ticket_no": ticket.name,
        "subject": ticket.subject,
        "type": ticket.iga_ticket_type,
        "status": ticket.status,
        "related_submission": ticket.iga_related_submission,
        "related_certificate": ticket.iga_related_certificate,
        "last_updated": str(ticket.modified),
        "messages": messages,
    }


def add_message(ticket_no):
    """POST /api/v1/support/tickets/{ticket_no}/messages"""
    data = frappe.local.form_dict
    customer = _get_session_customer()
    ticket = frappe.get_doc("Issue", ticket_no)
    if ticket.customer != customer:
        frappe.throw(_("Access denied"), frappe.PermissionError)

    # Append to description (simple approach — real system would use Communication)
    previous = ticket.description or ""
    ticket.description = previous + "\n\n[Customer]\n" + data.get("body", "")
    ticket.save(ignore_permissions=True)

    return {
        "id": f"{ticket_no}-msg",
        "sender": "customer",
        "body": data.get("body", ""),
        "created_at": str(frappe.utils.now_datetime()),
    }


def _get_session_customer():
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Authentication required"), frappe.PermissionError)
    customer = frappe.db.get_value("Customer", {"email_id": user}, "name")
    if not customer:
        frappe.throw(_("No customer profile found"), frappe.PermissionError)
    return customer
