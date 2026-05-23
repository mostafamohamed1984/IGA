import frappe


def get_all():
    """GET /api/v1/services"""
    return {
        "grading": get_grading(),
        "options": get_options(),
        "add_ons": get_add_ons(),
        "postage": get_postage(),
    }


def get_grading():
    """GET /api/v1/services/grading"""
    services = frappe.get_all("Service Master",
        fields=["category", "tier as tier", "base_fee as price",
                "turnaround_days as turnaround",
                "max_declared_value as max_value",
                "is_active"],
        order_by="category, tier"
    )
    for s in services:
        if s.get("price") is None:
            s["priceLabel"] = "contactAgent"
        if s.get("max_value") is None:
            s["maxValueLabel"] = "unlimited"
        s["turnaroundUnit"] = "days"
        if s.get("turnaround"):
            s["turnaround"] = str(s["turnaround"])
    return services


def get_options():
    """GET /api/v1/services/options"""
    return [
        {"code": "GRADING", "name": "Grading", "nameAr": "تقييم",
         "description": "Standard grading service", "descriptionAr": "خدمة التقييم القياسية",
         "pricingRule": "tier_full", "discountPercent": None, "autoApplied": False},
        {"code": "RE-GRADE", "name": "Re-Grade", "nameAr": "إعادة تقييم",
         "description": "Re-evaluate a previously graded item", "descriptionAr": "إعادة تقييم قطعة تم تقييمها سابقًا",
         "pricingRule": "tier_full", "discountPercent": None, "autoApplied": False},
        {"code": "CROSS-OVER", "name": "Cross-Over", "nameAr": "نقل التقييم",
         "description": "Transfer grading from another service", "descriptionAr": "نقل التقييم من خدمة أخرى",
         "pricingRule": "tier_full", "discountPercent": None, "autoApplied": False},
        {"code": "RE-SLAB", "name": "Re-Slab", "nameAr": "إعادة التغليف",
         "description": "Re-holder an existing IGA slab", "descriptionAr": "إعادة تغليف حافظة IGA الحالية",
         "pricingRule": "tier_minus_pct", "discountPercent": 20, "autoApplied": False},
        {"code": "BULK", "name": "Bulk", "nameAr": "تجميعي",
         "description": "Bulk submission (5+ items, 10% discount)", "descriptionAr": "تقديم تجميعي (5+ قطع، خصم 10%)",
         "pricingRule": "tier_minus_pct", "discountPercent": 10, "autoApplied": True},
        {"code": "RESTORATION", "name": "Restoration", "nameAr": "ترميم",
         "description": "Professional conservation service", "descriptionAr": "خدمة الترميم الاحترافية",
         "pricingRule": "contact_agent", "discountPercent": None, "autoApplied": False},
    ]


def get_add_ons():
    """GET /api/v1/services/add-ons"""
    return [
        {"key": "specialLabels", "name": "Special Labels", "price": 25,
         "descEn": "Custom label design", "descAr": "تصميم ملصق مخصص"},
        {"key": "firstReleases", "name": "First Releases", "price": 15,
         "descEn": "First release designation", "descAr": "تصنيف الإصدار الأول"},
        {"key": "pedigree", "name": "Pedigree", "price": 30,
         "descEn": "Provenance attribution on label", "descAr": "إسناد المصدر على الملصق"},
        {"key": "varieties", "name": "Varieties", "price": 20,
         "descEn": "Variety attribution", "descAr": "تصنيف التنوع"},
        {"key": "mintErrors", "name": "Mint Errors", "price": 25,
         "descEn": "Mint error attribution", "descAr": "تصنيف أخطاء السك"},
        {"key": "overSizeSlab", "name": "Oversize Slab", "price": 35,
         "descEn": "Oversized holder for large items", "descAr": "حافظة كبيرة للقطع الكبيرة"},
        {"key": "proLabAnalysis", "name": "Pro Lab Analysis", "price": None,
         "priceLabel": "contactAgent",
         "descEn": "Advanced laboratory analysis", "descAr": "تحليل معملي متقدم"},
        {"key": "detailedImaging", "name": "Detailed Imaging", "price": 20,
         "descEn": "High-resolution detailed images", "descAr": "صور عالية الدقة مفصلة"},
        {"key": "multiInsertSlab", "name": "Multi-Insert Slab", "price": 40,
         "descEn": "Multi-coin holder slab", "descAr": "حافظة متعددة القطع"},
    ]


def get_postage():
    """GET /api/v1/services/postage"""
    # Return active postage matrix or default
    matrix = frappe.get_all("Postage Matrix",
        filters={"is_active": 1},
        fields=["name", "currency", "rates"],
        limit=1
    )
    if matrix:
        m = matrix[0]
        rates = frappe.get_all("Postage Matrix Entry",
            filters={"parent": m.name},
            fields=["min_pieces", "max_pieces", "value_up_to_500",
                    "value_500_to_2000", "value_2000_to_10000",
                    "value_above_10000", "per_piece"],
            order_by="min_pieces"
        )
        return {
            "valueBreakpoints": [500, 2000, 10000],
            "pieceBreakpoints": list(set(r.min_pieces for r in rates)),
            "rates": rates,
        }
    else:
        return {
            "valueBreakpoints": [500, 2000, 10000],
            "pieceBreakpoints": [1, 6, 21],
            "rates": [
                {"min_pieces": 1, "max_pieces": 5, "value_up_to_500": 50,
                 "value_500_to_2000": 75, "value_2000_to_10000": 100,
                 "value_above_10000": 150, "per_piece": 0},
                {"min_pieces": 6, "max_pieces": 20, "value_up_to_500": 100,
                 "value_500_to_2000": 150, "value_2000_to_10000": 200,
                 "value_above_10000": 300, "per_piece": 0},
                {"min_pieces": 21, "max_pieces": None, "value_up_to_500": 10,
                 "value_500_to_2000": 15, "value_2000_to_10000": 20,
                 "value_above_10000": 30, "per_piece": 1},
            ],
        }
