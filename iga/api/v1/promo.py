import frappe
from frappe import _


def validate():
    """POST /api/v1/promo/validate"""
    data = frappe.local.form_dict
    code = data.get("code", "").strip().upper()
    if not code:
        return {"valid": False, "reason": "not_found"}

    promo = frappe.db.get_value("IGA Promo Code", code, "*", as_dict=1)
    if not promo:
        return {"valid": False, "reason": "not_found"}

    if not promo.active:
        return {"valid": False, "reason": "inactive"}

    if promo.expires_at:
        from frappe.utils import getdate
        if getdate(promo.expires_at) < getdate():
            return {"valid": False, "reason": "expired"}

    return {
        "valid": True,
        "code": {
            "code": promo.code,
            "type": promo.type,
            "value": promo.value,
            "description": promo.description,
            "expiresAt": str(promo.expires_at) if promo.expires_at else None,
            "active": bool(promo.active),
        }
    }
