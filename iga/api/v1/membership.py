import frappe
from frappe import _


def get_current_user():
    """GET /api/v1/membership/me"""
    customer = _get_session_customer()
    cust = frappe.get_value("Customer", customer,
        ["customer_name", "iga_display_name", "iga_display_name_ar",
         "iga_username", "email_id", "iga_avatar_url",
         "iga_plan_code", "iga_plan_status", "iga_is_dealer",
         "iga_rewards_balance", "creation as joined_at"], as_dict=1)
    if not cust:
        frappe.throw(_("Customer not found"), frappe.DoesNotExistError)

    return {
        "id": customer,
        "name": cust.iga_display_name or cust.customer_name,
        "nameEn": cust.customer_name,
        "email": cust.email_id,
        "avatarUrl": cust.iga_avatar_url,
        "plan": cust.iga_plan_code or "SILVER",
        "planStatus": cust.iga_plan_status or "Active",
        "isDealer": bool(cust.iga_is_dealer),
        "joinedAt": str(cust.joined_at) if cust.joined_at else "",
        "rewardsBalance": cust.iga_rewards_balance or 0,
    }


def update_profile():
    """PATCH /api/v1/membership/me"""
    customer = _get_session_customer()
    data = frappe.local.form_dict
    doc = frappe.get_doc("Customer", customer)
    if data.get("name"):
        doc.iga_display_name = data.get("name")
    if data.get("nameEn"):
        doc.customer_name = data.get("nameEn")
    if data.get("phone"):
        doc.mobile_no = data.get("phone")
    doc.save(ignore_permissions=True)
    return {"status": "updated"}


def list_plans():
    """GET /api/v1/membership/plans"""
    plans = frappe.get_all("Membership Plans",
        filters={"status": "Active"},
        fields=["plan_code as code", "plan_name as name",
                "monthly_fee as price_monthly", "annual_fee as price_annual",
                "included_credits as credit_bundle",
                "reward_multiplier", "max_redeem_pct",
                "feature_bullets as features"]
    )
    for p in plans:
        p["currency"] = "EGP"
        if p.get("features"):
            try:
                import json
                p["features"] = json.loads(p["features"]) if isinstance(p["features"], str) else p["features"]
            except (ValueError, TypeError):
                p["features"] = []
        else:
            p["features"] = []
    return plans


def subscribe():
    """POST /api/v1/membership/subscribe"""
    data = frappe.local.form_dict
    customer = _get_session_customer()

    sub = frappe.get_doc({
        "doctype": "Membership Subscriptions",
        "customer": customer,
        "plan": data.get("plan_code"),
        "billing_period": "Annual" if data.get("billing_period") == "annual" else "Monthly",
        "start_date": frappe.utils.today(),
        "status": "Pending",
    })
    sub.insert(ignore_permissions=True)
    sub.submit()

    return {"invoice_no": sub.membership_invoice or ""}


def get_subscription():
    """GET /api/v1/membership/subscription"""
    customer = _get_session_customer()
    subs = frappe.get_all("Membership Subscriptions",
        filters={"customer": customer, "status": ("!=", "Cancelled")},
        fields=["plan", "status", "billing_period", "end_date as renewal_date",
                "credits_remaining"],
        order_by="creation desc",
        limit=1
    )
    if not subs:
        return None
    sub = subs[0]
    plan = frappe.get_value("Membership Plans", sub.plan, ["plan_code", "plan_name"], as_dict=1)
    return {
        "plan_code": plan.plan_code if plan else "",
        "plan_name": plan.plan_name if plan else "",
        "status": sub.status,
        "billing_period": sub.billing_period.lower() if sub.billing_period else "monthly",
        "renewal_date": str(sub.renewal_date) if sub.renewal_date else "",
        "credits_remaining": sub.credits_remaining or 0,
    }


def cancel_subscription():
    """POST /api/v1/membership/subscription/cancel"""
    customer = _get_session_customer()
    subs = frappe.get_all("Membership Subscriptions",
        filters={"customer": customer, "status": "Active"},
        fields=["name"],
        limit=1
    )
    if subs:
        doc = frappe.get_doc("Membership Subscriptions", subs[0].name)
        doc.status = "Cancelled"
        doc.save(ignore_permissions=True)
    return {"status": "cancelled"}


def get_rewards():
    """GET /api/v1/membership/rewards"""
    customer = _get_session_customer()
    ledger = frappe.get_all("Rewards Ledger",
        filters={"member": customer},
        fields=["transaction_date as date", "notes as description",
                "points", "entry_type as type"],
        order_by="transaction_date desc",
        limit=5
    )
    total_points = frappe.db.get_value("Customer", customer, "iga_rewards_balance") or 0
    return {
        "points": total_points,
        "ledger": ledger
    }


def get_rewards_ledger():
    """GET /api/v1/membership/rewards/ledger"""
    customer = _get_session_customer()
    entries = frappe.get_all("Rewards Ledger",
        filters={"member": customer},
        fields=["name as id", "transaction_date as date",
                "entry_type as type", "points",
                "source_document as related", "notes as description",
                "balance_after"],
        order_by="transaction_date desc"
    )
    for e in entries:
        e["type"] = e["type"].lower()
    return entries


def redeem_rewards():
    """POST /api/v1/membership/rewards/redeem"""
    data = frappe.local.form_dict
    customer = _get_session_customer()
    points = data.get("points", 0)
    invoice_no = data.get("invoice_no")

    balance = frappe.db.get_value("Customer", customer, "iga_rewards_balance") or 0
    if points > balance:
        frappe.throw(_("Insufficient reward points"))

    if invoice_no:
        invoice = frappe.get_cached_doc("Sales Invoice", invoice_no)
        invoice_total = invoice.grand_total or 0
        plan_code = frappe.db.get_value("Customer", customer, "iga_plan_code") or "SILVER"
        plan = frappe.get_cached_doc("Membership Plans", {"plan_code": plan_code})
        max_pct = plan.max_redeem_pct or 25
        max_points = round(invoice_total * (max_pct / 100), 2)
        if points > max_points:
            frappe.throw(_(
                "Cannot redeem more than {0}% ({1} EGP) of invoice {2} total."
            ).format(max_pct, max_points, invoice_no))

    new_balance = balance - points
    frappe.db.set_value("Customer", customer, "iga_rewards_balance", new_balance)

    frappe.get_doc({
        "doctype": "Rewards Ledger",
        "member": customer,
        "entry_type": "Redeem",
        "points": points,
        "balance_after": new_balance,
        "notes": f"Redeemed against invoice {invoice_no}",
        "source_doctype": "Sales Invoice",
        "source_document": invoice_no,
    }).insert(ignore_permissions=True)

    return {"points_remaining": new_balance}


def _get_session_customer():
    user = frappe.session.user
    if user == "Guest":
        frappe.throw(_("Authentication required"), frappe.PermissionError)
    customer = frappe.db.get_value("Customer", {"email_id": user}, "name")
    if not customer:
        customer = frappe.db.get_value("Customer", {"iga_username": user}, "name")
    if not customer:
        frappe.throw(_("No customer profile found"), frappe.PermissionError)
    return customer
