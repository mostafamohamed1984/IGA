import frappe
from frappe import _


def get_tracking(tracking_id):
    """GET /api/v1/tracking/{tracking_id}"""
    sub = frappe.get_value("Submission", {"tracking_id": tracking_id},
        ["name", "tracking_id", "status", "item_count", "eta"], as_dict=1)
    if not sub:
        frappe.local.response["http_status_code"] = 404
        return {"code": "TRACKING_NOT_FOUND", "message": "Tracking ID not found"}

    items = frappe.get_all("Submission Item",
        filters={"parent_submission": sub.name},
        fields=["current_stage"]
    )

    stages = ["Created", "Received", "Grading", "Slabbing", "QC",
              "Imaging", "Shipped", "Ready for Pickup", "Completed", "On Hold"]
    breakdown = {s: 0 for s in stages}
    for item in items:
        stage = item.current_stage or "Created"
        if stage in breakdown:
            breakdown[stage] += 1

    last_event = frappe.db.get_value("Submission", sub.name, "modified")

    return {
        "tracking_id": sub.tracking_id,
        "customer_visible_status": sub.status,
        "items_count": sub.item_count,
        "items_breakdown": breakdown,
        "eta": sub.get("eta"),
        "last_event": str(last_event) if last_event else ""
    }
