import frappe
from frappe import _


def route(method, segments):
    """Router for all /api/v1/registry/* paths."""
    if len(segments) == 1:
        return {"error": "not_found"}

    action = segments[1]

    if action == "categories" and method == "GET":
        return get_categories()
    if action == "stats" and method == "GET":
        return get_live_stats()
    if action == "activity" and method == "GET":
        return get_activity_feed()
    if action == "my-achievements" and method == "GET":
        return get_my_achievements()
    if action == "awards" and method == "GET":
        return get_awards()

    if action == "my-sets":
        if method == "GET":
            return get_my_sets()
        if method == "POST":
            return create_my_set()
        if method == "PUT" and len(segments) >= 5 and segments[3] == "slots":
            return update_slots(segments[2])
        if len(segments) >= 4:
            set_id = segments[2]
            sub_action = segments[3]
            if sub_action == "cover" and method == "PUT":
                return update_set_cover(set_id)
            if sub_action == "narrative" and method == "PUT":
                return update_set_narrative(set_id)
            if sub_action == "visibility" and method == "PUT":
                return update_set_visibility(set_id)

    if action == "sets":
        if method == "GET":
            if len(segments) == 2:
                return get_all_sets()
            if len(segments) >= 3 and segments[2] != "comments":
                return get_set_detail(segments[2])
        if len(segments) >= 3 and segments[2] == "comments":
            set_id = segments[1]
            if method == "GET":
                return get_set_comments(set_id)
            if method == "POST":
                return post_set_comment(set_id)

    if action == "leaderboard" and method == "GET":
        return get_leaderboard(segments)

    if action == "top-pop" and len(segments) >= 3 and method == "GET":
        return get_top_pop(segments[2])

    if action == "watchlist":
        if method == "GET":
            return get_watchlist()
        if len(segments) >= 3:
            set_id = segments[2]
            if method == "POST":
                return add_to_watchlist(set_id)
            if method == "DELETE":
                return remove_from_watchlist(set_id)

    if action == "compare" and method == "GET":
        return compare_sets()

    frappe.local.response["http_status_code"] = 404
    return {"error": "not_found"}


def get_categories():
    cats = frappe.get_all("Registry Categories",
        filters={"is_active": 1},
        fields=["category_code as code", "category_name_en as name",
                "description", "sort_order"]
    )
    for c in cats:
        c["sets_count"] = frappe.db.count("Registry Set Definitions",
            {"category": c["code"], "is_active": 1})
    return cats


def get_all_sets():
    category = frappe.form_dict.get("category")
    set_type = frappe.form_dict.get("type")
    filters = {"is_active": 1}
    if category:
        filters["category"] = category
    if set_type == "custom":
        sets = frappe.get_all("Member Registry Sets",
            filters={"is_public": 1},
            fields=["name as id", "set_name_custom as name",
                    "total_score as score", "completion_percentage as completion_pct",
                    "is_public as visibility"]
        )
    else:
        sets = frappe.get_all("Registry Set Definitions",
            filters=filters,
            fields=["set_code as code", "set_name_en as name",
                    "category_code as category_code",
                    "description", "total_slots as slots_count"]
        )
    return sets


def get_set_detail(set_code):
    set_def = frappe.get_value("Registry Set Definitions",
        {"set_code": set_code}, "*", as_dict=1)
    if set_def:
        slots = frappe.get_all("Registry Set Slots",
            filters={"parent": set_def.name},
            fields=["slot_number as slot_no", "slot_name as description",
                    "required_grade_min as required_grade"],
            order_by="slot_number"
        )
        return {
            "code": set_def.set_code,
            "name": set_def.set_name_en,
            "category_code": set_def.category,
            "description": set_def.description,
            "slots_count": set_def.total_slots,
            "scoring_rules": set_def.scoring_rules or "",
            "slots": slots,
            "top_members": []
        }
    member_set = frappe.get_value("Member Registry Sets",
        {"name": set_code}, "*", as_dict=1)
    if member_set:
        slots = frappe.get_all("Member Registry Set Slot",
            filters={"parent": member_set.name},
            fields=["slot_number as slot_no", "slot_name as description",
                    "certificate_number", "final_grade as assigned_grade"],
            order_by="slot_number"
        )
        return {
            "member_set_no": member_set.name,
            "set_name": member_set.set_name_custom or "",
            "score": member_set.total_score,
            "rank": member_set.rank,
            "completion_pct": member_set.completion_percentage,
            "is_public": member_set.is_public,
            "slots": slots,
        }
    frappe.throw(_("Set not found"), frappe.DoesNotExistError)


def get_my_sets():
    customer = _get_session_customer()
    sets = frappe.get_all("Member Registry Sets",
        filters={"customer": customer},
        fields=["name as member_set_no", "set_name_custom as set_name",
                "total_score as score", "rank",
                "completion_percentage as completion_pct",
                "is_public", "filled_slots"],
        order_by="total_score desc"
    )
    return sets


def create_my_set():
    data = frappe.local.form_dict
    customer = _get_session_customer()

    is_custom = data.get("type") == "custom"
    doc = frappe.get_doc({
        "doctype": "Member Registry Sets",
        "customer": customer,
        "set_definition": data.get("set_definition_code") if not is_custom else None,
        "set_name_custom": data.get("name") if is_custom else data.get("set_name"),
        "is_public": data.get("is_public", 0),
    })

    if is_custom:
        for s in data.get("slots", []):
            doc.append("slots", {
                "slot_number": s.get("slot_no"),
                "slot_name": s.get("description"),
            })

    doc.insert(ignore_permissions=True)

    return {
        "member_set_no": doc.name,
        "set_name": doc.set_name_custom,
        "score": doc.total_score,
        "rank": doc.rank,
        "completion_pct": doc.completion_percentage,
        "is_public": doc.is_public,
    }


def update_slots(member_set_no):
    data = frappe.local.form_dict
    customer = _get_session_customer()
    doc = frappe.get_doc("Member Registry Sets", member_set_no)
    if doc.customer != customer:
        frappe.throw(_("Access denied"), frappe.PermissionError)

    for slot_data in data.get("slots", []):
        slot_no = slot_data.get("slot_no")
        cert_no = slot_data.get("certificate_number")
        for slot in doc.slots:
            if slot.slot_number == slot_no:
                slot.certificate_number = cert_no
                break

    doc.save(ignore_permissions=True)
    return {"status": "updated", "score": doc.total_score}


def update_set_cover(set_id):
    data = frappe.local.form_dict
    doc = frappe.get_doc("Member Registry Sets", set_id)
    _check_owner(doc)
    doc.set_image = data.get("cover_image")
    doc.save(ignore_permissions=True)
    return {"status": "updated"}


def update_set_narrative(set_id):
    data = frappe.local.form_dict
    doc = frappe.get_doc("Member Registry Sets", set_id)
    _check_owner(doc)
    doc.notes = data.get("narrative")
    doc.save(ignore_permissions=True)
    return {"status": "updated"}


def update_set_visibility(set_id):
    data = frappe.local.form_dict
    doc = frappe.get_doc("Member Registry Sets", set_id)
    _check_owner(doc)
    doc.is_public = 1 if data.get("visibility") == "public" else 0
    doc.save(ignore_permissions=True)
    return {"status": "updated"}


def get_leaderboard(segments):
    if len(segments) >= 3 and segments[2] == "collectors":
        return _collector_leaderboard()

    set_code = segments[2] if len(segments) >= 3 else None
    if set_code:
        members = frappe.get_all("Member Registry Sets",
            filters={"set_definition": set_code, "is_public": 1},
            fields=["customer", "total_score as score",
                    "completion_percentage as completion_pct",
                    "rank", "name"],
            order_by="rank asc",
            limit=100
        )
        result = []
        for m in members:
            cust = frappe.get_value("Customer", m.customer, ["iga_username", "iga_display_name"], as_dict=1)
            result.append({
                "rank": m.rank,
                "username": cust.iga_username if cust else "",
                "score": m.score,
                "completion_pct": m.completion_pct,
            })
        return result

    frappe.local.response["http_status_code"] = 404
    return {"error": "not_found"}


def _collector_leaderboard():
    members = frappe.get_all("Member Registry Sets",
        filters={"is_public": 1},
        fields=["customer"],
        group_by="customer"
    )
    result = []
    for rank, m in enumerate(members, 1):
        cust = frappe.get_value("Customer", m.customer,
            ["iga_username", "iga_display_name", "iga_avatar_url"], as_dict=1)
        total_score = frappe.db.sql(
            "SELECT SUM(total_score) FROM `tabMember Registry Sets` WHERE customer=%s AND is_public=1",
            m.customer
        )[0][0] or 0
        sets_count = frappe.db.count("Member Registry Sets",
            {"customer": m.customer, "is_public": 1})
        result.append({
            "rank": rank,
            "customer_id": m.customer,
            "display_name": cust.iga_display_name if cust else "",
            "username": cust.iga_username if cust else "",
            "avatar_url": cust.iga_avatar_url if cust else None,
            "total_score": round(total_score, 2),
            "sets_count": sets_count,
            "achievements_count": 0,
            "trend": "flat",
        })
    return result


def get_live_stats():
    return {
        "collectors": frappe.db.count("Member Registry Sets", distinct="customer"),
        "sets": frappe.db.count("Member Registry Sets"),
        "coins": frappe.db.count("Submission Item",
            filters={"result_type": ("in", ("Encapsulated", "Details"))}),
        "awards": 0,
    }


def get_activity_feed():
    return []


def get_my_achievements():
    return {"earned": [], "progress": {}}


def get_awards():
    return {"categories": [], "winners": [], "calendar": []}


def get_top_pop(ref_code):
    items = frappe.get_all("Submission Item",
        filters={"item_reference": ref_code, "result_type": "Encapsulated"},
        fields=["certificate_number", "final_grade as grade", "parent_submission"],
        order_by="final_grade desc",
        limit=10
    )
    result = []
    for item in items:
        cust = frappe.db.get_value("Submission", item.parent_submission, "customer")
        cust_info = frappe.get_value("Customer", cust,
            ["iga_display_name", "iga_username"], as_dict=1) if cust else None
        result.append({
            "reference_code": ref_code,
            "description": ref_code,
            "grade": item.grade,
            "certificate_number": item.certificate_number,
            "customer_id": cust,
            "display_name": cust_info.iga_display_name if cust_info else "",
        })
    return result


def get_eligible_certificates():
    customer = _get_session_customer()
    submissions = frappe.get_all("Submission",
        filters={"customer": customer},
        fields=["name"]
    )
    sub_names = [s.name for s in submissions]
    items = frappe.get_all("Submission Item",
        filters={
            "parent_submission": ("in", sub_names),
            "result_type": ("in", ("Encapsulated", "Details")),
        },
        fields=["certificate_number", "item_reference", "final_grade"]
    )
    result = []
    for item in items:
        ref = frappe.get_value("Item Reference Catalog", item.item_reference,
            "description_en") if item.item_reference else None
        grade_name = frappe.get_value("Grade Scale Master", item.final_grade,
            "grade_name") if item.final_grade else item.final_grade
        result.append({
            "certificate_number": item.certificate_number,
            "description": ref or item.item_reference or "",
            "grade": grade_name or "",
        })
    return result


def get_set_comments(set_id):
    return []


def post_set_comment(set_id):
    data = frappe.local.form_dict
    return {
        "id": f"{set_id}-c1",
        "set_id": set_id,
        "author": {"customer_id": "", "display_name": "You"},
        "body": data.get("body", ""),
        "created_at": str(frappe.utils.now_datetime()),
        "likes": 0,
    }


def get_watchlist():
    return []


def add_to_watchlist(set_id):
    return {"status": "added", "set_id": set_id}


def remove_from_watchlist(set_id):
    return {"status": "removed", "set_id": set_id}


def compare_sets():
    a = frappe.form_dict.get("a")
    b = frappe.form_dict.get("b")
    return {
        "set_a": {},
        "set_b": {},
        "rows": [],
        "score_a": 0,
        "score_b": 0,
    }


def _check_owner(doc):
    customer = _get_session_customer()
    if doc.customer != customer:
        frappe.throw(_("Access denied"), frappe.PermissionError)


def _get_session_customer():
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Authentication required"), frappe.PermissionError)
    customer = frappe.db.get_value("Customer", {"email_id": user}, "name")
    if not customer:
        frappe.throw(_("No customer profile found"), frappe.PermissionError)
    return customer
