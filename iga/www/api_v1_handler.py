import frappe
from frappe import _
import json

from iga.api.v1 import verify as v_verify
from iga.api.v1 import submissions as v_submissions
from iga.api.v1 import tracking as v_tracking
from iga.api.v1 import membership as v_membership
from iga.api.v1 import registry as v_registry
from iga.api.v1 import support as v_support
from iga.api.v1 import services as v_services
from iga.api.v1 import population as v_population
from iga.api.v1 import price_guide as v_price_guide
from iga.api.v1 import promo as v_promo
from iga.api.v1 import news as v_news
from iga.api.v1 import invoices as v_invoices
from iga.api.v1 import dealer as v_dealer
from iga.api.v1 import catalog as v_catalog


def get_context(context):
    """Entry point for all /api/v1/* requests."""
    path = frappe.local.request.path.strip("/")
    method = frappe.local.request.method.upper()

    prefix = "api/v1/"
    if path.startswith(prefix):
        path = path[len(prefix):]
    
    path = path.rstrip("/")
    segments = path.split("/") if path else []

    try:
        result = _dispatch(method, segments)
        frappe.local.response["content_type"] = "application/json"
        return result
    except frappe.DoesNotExistError:
        frappe.local.response["http_status_code"] = 404
        return {"code": "NOT_FOUND", "message": "Resource not found"}
    except frappe.PermissionError:
        frappe.local.response["http_status_code"] = 403
        return {"code": "FORBIDDEN", "message": "Access denied"}
    except Exception as e:
        if frappe.local.response.get("http_status_code", 200) >= 400:
            return frappe.local.response
        frappe.local.response["http_status_code"] = 500
        return {"code": "INTERNAL_ERROR", "message": str(e)}


def _dispatch(method, segments):
    if not segments:
        return {"status": "ok", "version": "1.0"}

    domain = segments[0]

    # GET /api/v1/verify/{cert_no}  |  POST /api/v1/verify/nfc
    if domain == "verify":
        if len(segments) >= 2:
            if segments[1] == "nfc" and method == "POST":
                return v_verify.verify_nfc()
            return v_verify.verify_certificate(segments[1])

    # GET /api/v1/tracking/{tracking_id}
    if domain == "tracking" and len(segments) >= 2:
        return v_tracking.get_tracking(segments[1])

    # /api/v1/submissions
    if domain == "submissions":
        if len(segments) == 1:
            if method == "GET":
                return v_submissions.list_submissions()
            if method == "POST":
                return v_submissions.create_submission()
        elif len(segments) == 2:
            if segments[1] == "quote" and method == "POST":
                return v_submissions.get_quote()
            if method == "GET":
                return v_submissions.get_detail(segments[1])
        elif len(segments) == 3 and segments[2] == "activity" and method == "GET":
            return v_submissions.get_activity(segments[1])
        elif len(segments) == 3 and segments[2] == "cancel" and method == "POST":
            return v_submissions.cancel(segments[1])

    # /api/v1/membership
    if domain == "membership":
        if len(segments) == 2 and segments[1] == "plans" and method == "GET":
            return v_membership.list_plans()
        if len(segments) == 2 and segments[1] == "me":
            if method == "GET":
                return v_membership.get_current_user()
            if method == "PATCH":
                return v_membership.update_profile()
        if len(segments) == 3 and segments[1] == "me":
            if segments[2] == "password" and method == "POST":
                return {"status": "ok"}
            if segments[2] == "notifications" and method == "PATCH":
                return {"status": "ok"}
        if segments[1] == "subscribe" and method == "POST":
            return v_membership.subscribe()
        if segments[1] == "subscription":
            if method == "GET":
                return v_membership.get_subscription()
            if len(segments) >= 3 and segments[2] == "cancel" and method == "POST":
                return v_membership.cancel_subscription()
        if segments[1] == "rewards":
            if len(segments) == 2 and method == "GET":
                return v_membership.get_rewards()
            if len(segments) >= 3 and segments[2] == "ledger" and method == "GET":
                return v_membership.get_rewards_ledger()
            if len(segments) >= 3 and segments[2] == "redeem" and method == "POST":
                return v_membership.redeem_rewards()

    # /api/v1/registry
    if domain == "registry":
        return v_registry.route(method, segments)

    # /api/v1/support/tickets
    if domain == "support" and segments[1] == "tickets":
        if method == "POST" and len(segments) == 2:
            return v_support.create_ticket()
        if method == "GET" and len(segments) == 2:
            return v_support.list_tickets()
        if len(segments) == 3 and method == "GET":
            return v_support.get_ticket(segments[2])
        if len(segments) == 4 and segments[3] == "messages" and method == "POST":
            return v_support.add_message(segments[2])

    # /api/v1/services
    if domain == "services":
        if segments[1] == "grading" and method == "GET":
            return v_services.get_grading()
        if segments[1] == "options" and method == "GET":
            return v_services.get_options()
        if segments[1] == "add-ons" and method == "GET":
            return v_services.get_add_ons()
        if segments[1] == "postage" and method == "GET":
            return v_services.get_postage()

    # /api/v1/population
    if domain == "population":
        if segments[1] == "reference" and len(segments) >= 3 and method == "GET":
            return v_population.get_by_reference(segments[2])
        if segments[1] == "search" and method == "GET":
            return v_population.search()

    # /api/v1/price-guide
    if domain == "price-guide":
        if segments[1] == "trending" and method == "GET":
            return v_price_guide.get_trending()
        if segments[1] == "top-pop" and method == "GET":
            return v_price_guide.get_top_pop()
        if segments[1] == "registry-stars" and method == "GET":
            return v_price_guide.get_registry_stars()
        if len(segments) == 2 and method == "GET":
            return v_price_guide.get_detail(segments[1])
        if len(segments) == 1 and method == "GET":
            return v_price_guide.list_all()

    # /api/v1/promo/validate
    if domain == "promo" and segments[1] == "validate" and method == "POST":
        return v_promo.validate()

    # /api/v1/news
    if domain == "news":
        if len(segments) == 1 and method == "GET":
            return v_news.list_all()
        if len(segments) >= 2 and method == "GET":
            return v_news.get_article(segments[1])

    # /api/v1/invoices
    if domain == "invoices":
        if method == "GET" and len(segments) == 1:
            return v_invoices.list_all()
        if method == "GET" and len(segments) >= 2:
            return v_invoices.get_detail(segments[1])

    # /api/v1/dealer
    if domain == "dealer":
        if segments[1] == "submissions" and method == "GET":
            return v_dealer.get_submissions()
        if segments[1] == "stats" and method == "GET":
            return v_dealer.get_stats()
        if segments[1] == "top-collectors" and method == "GET":
            return v_dealer.get_top_collectors()

    # /api/v1/catalog/coins
    if domain == "catalog" and segments[1] == "coins":
        if method == "GET" and len(segments) == 2:
            return v_catalog.search_coins()
        if method == "GET" and len(segments) >= 3:
            return v_catalog.get_coin(segments[2])

    # /api/v1/customer/certificates
    if domain == "customer" and segments[1] == "certificates" and method == "GET":
        return v_registry.get_eligible_certificates()

    frappe.local.response["http_status_code"] = 404
    return {"code": "NOT_FOUND", "message": f"No handler for {method} /api/v1/{'/'.join(segments)}"}
