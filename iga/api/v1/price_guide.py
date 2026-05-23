import frappe


def list_all():
    """GET /api/v1/price-guide"""
    args = frappe.local.form_dict
    page = int(args.get("page", 1))
    page_size = min(int(args.get("page_size", 24)), 100)
    shortcut = args.get("shortcut", "")
    query = args.get("query", "")
    sort = args.get("sort", "newest")

    filters = {"status": "Active"}
    if query:
        filters["description_en"] = ("like", f"%{query}%")

    refs = frappe.get_all("Item Reference Catalog",
        filters=filters,
        fields=["ref_code", "description_en as denomination",
                "year_ad as year", "country", "collectible_type as category",
                "series_set_issue as series", "mintmark"],
        order_by="creation desc" if sort == "newest" else "modified desc",
        limit_page_length=page_size,
        limit_start=(page - 1) * page_size
    )

    total = frappe.db.count("Item Reference Catalog", filters)

    results = []
    for r in refs:
        pricing = frappe.get_all("Item Reference Pricing",
            filters={"parent": r.ref_code},
            fields=["grade", "low", "median", "high", "currency", "confidence", "last_updated"]
        )
        by_grade = {}
        for p in pricing:
            grade_name = frappe.get_value("Grade Scale Master", p.grade, "grade_name") or p.grade
            by_grade[grade_name] = {
                "low": p.low,
                "median": p.median,
                "high": p.high,
            }

        results.append({
            "refCode": r.ref_code,
            "denomination": r.denomination or "",
            "year": r.year or 0,
            "country": r.country or "",
            "category": r.category or "",
            "series": r.series or "",
            "mintmark": r.mintmark or "",
            "pricing": {
                "byGrade": by_grade,
            },
            "signals": {
                "trendingScore": 0,
                "isTopPopTarget": False,
                "registryActiveSetCount": 0,
            }
        })

    return {
        "results": results,
        "total_count": total,
        "page": page,
        "page_size": page_size,
    }


def get_detail(ref_code):
    """GET /api/v1/price-guide/{ref_code}"""
    ref = frappe.get_value("Item Reference Catalog",
        {"ref_code": ref_code}, "*", as_dict=1)
    if not ref:
        frappe.local.response["http_status_code"] = 404
        return {"code": "NOT_FOUND", "message": "Reference not found"}

    pricing = frappe.get_all("Item Reference Pricing",
        filters={"parent": ref.name},
        fields=["grade", "low", "median", "high", "currency", "confidence", "last_updated"]
    )
    by_grade = {}
    for p in pricing:
        grade_name = frappe.get_value("Grade Scale Master", p.grade, "grade_name") or p.grade
        by_grade[grade_name] = {
            "low": p.low,
            "median": p.median,
            "high": p.high,
        }

    return {
        "refCode": ref.ref_code,
        "denomination": ref.description_en or ref.title,
        "year": ref.year_ad or 0,
        "country": ref.country or "",
        "category": ref.collectible_type or "",
        "series": ref.series_set_issue or "",
        "mintmark": ref.mintmark or "",
        "pricing": {"byGrade": by_grade},
        "signals": {
            "trendingScore": ref.trending_score or 0,
            "isTopPopTarget": False,
            "registryActiveSetCount": ref.registry_active_set_count or 0,
        }
    }


def get_trending():
    """GET /api/v1/price-guide/trending"""
    limit = int(frappe.form_dict.get("limit", 6))
    refs = frappe.get_all("Item Reference Catalog",
        filters={"status": "Active"},
        fields=["ref_code", "description_en as denomination",
                "year_ad as year", "country", "trending_score"],
        order_by="trending_score desc",
        limit=limit
    )
    return _build_coin_references(refs)


def get_top_pop():
    """GET /api/v1/price-guide/top-pop"""
    limit = int(frappe.form_dict.get("limit", 6))
    refs = frappe.get_all("Item Reference Catalog",
        filters={"status": "Active"},
        fields=["ref_code", "description_en as denomination",
                "year_ad as year", "country"],
        limit=limit
    )
    return _build_coin_references(refs)


def get_registry_stars():
    """GET /api/v1/price-guide/registry-stars"""
    limit = int(frappe.form_dict.get("limit", 6))
    refs = frappe.get_all("Item Reference Catalog",
        filters={"status": "Active"},
        fields=["ref_code", "description_en as denomination",
                "year_ad as year", "country", "registry_active_set_count"],
        order_by="registry_active_set_count desc",
        limit=limit
    )
    return _build_coin_references(refs)


def _build_coin_references(refs):
    results = []
    for r in refs:
        pricing = frappe.get_all("Item Reference Pricing",
            filters={"parent": r.ref_code},
            fields=["grade", "low", "median", "high"]
        )
        by_grade = {}
        for p in pricing:
            grade_name = frappe.get_value("Grade Scale Master", p.grade, "grade_name") or p.grade
            by_grade[grade_name] = {"low": p.low, "median": p.median, "high": p.high}

        results.append({
            "refCode": r.ref_code,
            "denomination": r.denomination or "",
            "year": r.year or 0,
            "country": r.country or "",
            "pricing": {"byGrade": by_grade},
            "signals": {
                "trendingScore": r.get("trending_score", 0),
                "registryActiveSetCount": r.get("registry_active_set_count", 0),
            }
        })
    return results
