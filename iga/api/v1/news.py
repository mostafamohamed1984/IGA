import frappe


def list_all():
    """GET /api/v1/news"""
    limit = frappe.form_dict.get("limit", 0)
    filters = {"published": 1}
    articles = frappe.get_all("IGA News Article",
        filters=filters,
        fields=["slug", "title", "title_ar", "excerpt", "excerpt_ar",
                "date", "category", "category_ar"],
        order_by="date desc",
        limit=limit or None
    )
    if limit:
        articles = articles[:int(limit)]
    return articles


def get_article(slug):
    """GET /api/v1/news/{slug}"""
    article = frappe.get_value("IGA News Article",
        {"slug": slug, "published": 1},
        ["slug", "title", "title_ar", "excerpt", "excerpt_ar",
         "body", "body_ar", "date", "category", "category_ar",
         "cover_image"],
        as_dict=1
    )
    if not article:
        frappe.local.response["http_status_code"] = 404
        return {"code": "NOT_FOUND", "message": "Article not found"}
    return article
