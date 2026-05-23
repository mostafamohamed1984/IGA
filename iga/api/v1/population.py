import frappe


def get_by_reference(ref_code):
    """GET /api/v1/population/reference/{ref_code}"""
    catalog = frappe.get_value("Item Reference Catalog",
        {"ref_code": ref_code}, "name", as_dict=1)
    if not catalog:
        return None

    items = frappe.get_all("Submission Item",
        filters={
            "item_reference": catalog.name,
            "result_type": ("in", ("Encapsulated", "Details")),
        },
        fields=["final_grade"]
    )

    by_grade = {}
    for item in items:
        grade = item.final_grade or "Unspecified"
        by_grade[grade] = by_grade.get(grade, 0) + 1

    return {
        "reference_code": ref_code,
        "totals": {
            "by_grade": by_grade,
            "by_designation": {},
        },
        "last_updated": str(frappe.utils.now_datetime()),
        "count": len(items),
    }


def search():
    """GET /api/v1/population/search"""
    args = frappe.local.form_dict
    q = args.get("q", "")
    category = args.get("category", "")
    country = args.get("country", "")
    mint = args.get("mint", "")
    variety = args.get("variety", "")

    filters = {"status": "Active"}
    if q:
        filters["description_en"] = ("like", f"%{q}%")
    if country:
        filters["country"] = country

    refs = frappe.get_all("Item Reference Catalog",
        filters=filters,
        fields=["ref_code as reference_code", "description_en as coin_name",
                "country", "year_ad as year", "collectible_type as type",
                "mintmark"],
        limit_page_length=50
    )

    result = []
    for r in refs:
        items = frappe.get_all("Submission Item",
            filters={
                "item_reference": r.reference_code,
                "result_type": ("in", ("Encapsulated", "Details")),
            },
            fields=["final_grade"]
        )
        by_grade = {}
        for item in items:
            grade = item.final_grade or ""
            by_grade[grade] = by_grade.get(grade, 0) + 1

        result.append({
            "reference_code": r.reference_code,
            "coin_name": r.coin_name or "",
            "country": r.country or "",
            "country_name_en": r.country or "",
            "country_name_ar": "",
            "country_flag": "",
            "year": r.year or 0,
            "category": category or "",
            "type": r.type or "",
            "totals": {"by_grade": by_grade, "by_designation": {}},
            "count": len(items),
        })

    return {
        "results": result,
        "total_count": len(result),
        "page": 1,
        "page_size": 50,
    }
