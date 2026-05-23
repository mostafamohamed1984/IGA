import frappe


def search_coins():
    """GET /api/v1/catalog/coins?q={text}&limit=20"""
    args = frappe.local.form_dict
    q = args.get("q", "").strip()
    limit = min(int(args.get("limit", 20)), 100)

    filters = {"status": "Active"}
    if q:
        filters["description_en"] = ("like", f"%{q}%")

    coins = frappe.get_all("Item Reference Catalog",
        filters=filters,
        fields=["ref_code", "title", "description_en as description",
                "description_ar", "country", "year_ad as year",
                "denomination_value", "denomination_unit",
                "mintmark", "collectible_type"],
        limit=limit
    )
    return coins


def get_coin(ref_code):
    """GET /api/v1/catalog/coins/{ref_code}"""
    coin = frappe.get_value("Item Reference Catalog",
        {"ref_code": ref_code, "status": "Active"},
        ["ref_code", "title", "description_en as description",
         "description_ar", "country", "year_ad as year",
         "denomination_value", "denomination_unit",
         "mintmark", "collectible_type",
         "metal", "purity", "weight_g", "diameter_mm",
         "mintage_qty", "series_set_issue as series",
         "front_image", "back_image",
         "trending_score", "registry_active_set_count"],
        as_dict=1
    )
    if not coin:
        frappe.local.response["http_status_code"] = 404
        return {"code": "NOT_FOUND", "message": "Coin not found"}
    return coin
