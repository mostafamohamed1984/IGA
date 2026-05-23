import frappe
from frappe import _
from frappe.utils import today


def get_submissions():
    """GET /api/v1/dealer/submissions"""
    customer = _get_session_customer()
    subs = frappe.get_all("Submission",
        filters={"dealer": customer},
        fields=["submission_no", "dealer_reference_no as dealer_ref",
                "submitted_on_behalf_of as collector_name",
                "creation as submitted_at", "item_count as items_count",
                "status", "grand_total as total_egp"],
        order_by="creation desc"
    )
    return subs


def get_stats():
    """GET /api/v1/dealer/stats"""
    customer = _get_session_customer()
    subs = frappe.get_all("Submission",
        filters={"dealer": customer},
        fields=["status", "name"]
    )
    total = len(subs)
    active = sum(1 for s in subs if s.status not in ("Completed", "Cancelled"))
    completed_this_month = frappe.db.count("Submission",
        filters={
            "dealer": customer,
            "status": "Completed",
            "completed_on": ("between", [today() + "-01", today() + "-31"]),
        }
    )
    total_items = frappe.db.sql(
        "SELECT SUM(item_count) FROM `tabSubmission` WHERE dealer=%s", customer
    )[0][0] or 0

    return {
        "total_submissions": total,
        "active_in_flight": active,
        "completed_this_month": completed_this_month,
        "total_items_graded": total_items,
    }


def get_top_collectors():
    """GET /api/v1/dealer/top-collectors"""
    customer = _get_session_customer()
    dealers_collectors = frappe.db.sql("""
        SELECT submitted_on_behalf_of as collector_name,
               COUNT(*) as submissions,
               SUM(item_count) as total_items
        FROM `tabSubmission`
        WHERE dealer=%s AND submitted_on_behalf_of IS NOT NULL
        GROUP BY submitted_on_behalf_of
        ORDER BY submissions DESC
        LIMIT 20
    """, customer, as_dict=1)
    return dealers_collectors


def _get_session_customer():
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Authentication required"), frappe.PermissionError)
    customer = frappe.db.get_value("Customer", {"email_id": user}, "name")
    if not customer:
        frappe.throw(_("No customer profile found"), frappe.PermissionError)
    return customer
