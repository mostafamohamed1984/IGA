import frappe
from frappe import _
import json


def list_submissions():
    """GET /api/v1/submissions"""
    customer = _get_session_customer()
    submissions = frappe.get_all("Submission",
        filters={"customer": customer},
        fields=["submission_no", "tracking_id", "status", "item_count",
                "creation as submitted_on", "service_tier", "category"],
        order_by="creation desc"
    )
    return submissions


def get_detail(submission_no):
    """GET /api/v1/submissions/{submission_no}"""
    customer = _get_session_customer()
    sub = frappe.get_value("Submission", {"submission_no": submission_no}, "*", as_dict=1)
    if not sub:
        frappe.throw(_("Submission not found"), frappe.DoesNotExistError)
    if sub.customer != customer:
        frappe.throw(_("Access denied"), frappe.PermissionError)

    items = frappe.get_all("Submission Item",
        filters={"parent_submission": sub.name},
        fields=["item_reference", "declared_value", "declared_grade",
                "service_option", "add_ons", "notes", "certificate_number",
                "current_stage", "result_type"]
    )

    return {
        "submission_no": sub.submission_no,
        "tracking_id": sub.tracking_id,
        "status": sub.status,
        "items_count": sub.item_count,
        "submitted_on": sub.creation,
        "service_tier": sub.service_tier,
        "category": sub.category,
        "items": items,
        "proforma_invoice_no": sub.proforma_invoice,
        "sales_invoice_no": sub.sales_invoice,
        "received_on": sub.received_on,
        "grading_complete_on": sub.grading_complete_on,
        "completed_on": sub.completed_on,
    }


def create_submission():
    """POST /api/v1/submissions"""
    data = frappe.local.form_dict
    customer = _get_session_customer()

    sub = frappe.get_doc({
        "doctype": "Submission",
        "customer": customer,
        "service_tier": data.get("service_tier"),
        "category": data.get("category"),
        "is_bulk": data.get("is_bulk", 0),
        "uses_credit": data.get("uses_credit", 0),
        "submission_source": data.get("submission_source", "Customer"),
        "dealer": data.get("dealer"),
        "submitted_on_behalf_of": data.get("submitted_on_behalf_of"),
        "dealer_reference_no": data.get("dealer_reference_no"),
        "payment_method": data.get("payment_method", "CASH"),
        "payment_method_note": data.get("payment_method_note"),
        "promo_code": data.get("promo_code"),
    })

    # Add items
    for itm in data.get("items", []):
        sub.append("items", {
            "item_reference": itm.get("item_reference"),
            "declared_value": itm.get("declared_value", 0),
            "declared_grade": itm.get("declared_grade"),
            "service_option": itm.get("service_option"),
            "add_ons": json.dumps(itm.get("add_ons", [])),
            "notes": itm.get("notes"),
        })

    sub.insert(ignore_permissions=True)

    generated_items = frappe.get_all("Submission Item",
        filters={"parent_submission": sub.name},
        fields=["certificate_number"]
    )

    return {
        "submission_no": sub.submission_no,
        "tracking_id": sub.tracking_id,
        "proforma_invoice_no": sub.proforma_invoice,
        "status": sub.status,
        "items": generated_items
    }


def get_quote():
    """POST /api/v1/submissions/quote"""
    data = frappe.local.form_dict
    from iga.international_grading_agency.doctype.submission.submission import compute_quote
    return compute_quote(
        service_tier=data.get("service_tier"),
        category=data.get("category"),
        is_bulk=data.get("is_bulk", 0),
        items=data.get("items", [])
    )


def get_activity(submission_no):
    """GET /api/v1/submissions/{submission_no}/activity"""
    customer = _get_session_customer()
    sub = frappe.get_value("Submission", {"submission_no": submission_no}, ["name", "customer"], as_dict=1)
    if not sub:
        frappe.throw(_("Submission not found"), frappe.DoesNotExistError)
    if sub.customer != customer:
        frappe.throw(_("Access denied"), frappe.PermissionError)

    submission_doc = frappe.get_doc("Submission", sub.name)
    return submission_doc.get_activity()


def cancel(submission_no):
    """POST /api/v1/submissions/{submission_no}/cancel"""
    customer = _get_session_customer()
    sub = frappe.get_value("Submission", {"submission_no": submission_no}, ["name", "customer", "status"], as_dict=1)
    if not sub:
        frappe.throw(_("Submission not found"), frappe.DoesNotExistError)
    if sub.customer != customer:
        frappe.throw(_("Access denied"), frappe.PermissionError)
    if sub.status != "Created":
        frappe.throw(_("Only submissions in 'Created' status can be cancelled"))

    doc = frappe.get_doc("Submission", sub.name)
    doc.status = "Cancelled"
    doc.save(ignore_permissions=True)
    frappe.local.response["http_status_code"] = 204
    return {}


def _get_session_customer():
    """Resolve the ERPNext Customer for the current session user."""
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Authentication required"), frappe.PermissionError)
    customer = frappe.db.get_value("Customer", {"custom_email": user}, "name")
    if not customer:
        customer = frappe.db.get_value("Customer", {"email_id": user}, "name")
    if not customer:
        frappe.throw(_("No customer profile found for this user"), frappe.PermissionError)
    return customer
