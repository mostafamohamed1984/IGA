import frappe
from frappe import _
from frappe.utils import cstr


def verify_certificate(cert_no):
    """GET /api/v1/verify/{cert_no}"""
    return _get_verify_result(cert_no)


def verify_nfc():
    """POST /api/v1/verify/nfc"""
    body = frappe.local.form_dict
    encoded = body.get("payload")
    if not encoded:
        frappe.throw(_("Payload is required"), frappe.DoesNotExistError)

    from iga.international_grading_agency.doctype.nfc_settings.nfc_settings import NFCSettings

    cert_no, valid = NFCSettings.verify_nfc_payload(encoded)
    if not valid:
        frappe.local.response["http_status_code"] = 401
        return {
            "code": "INVALID_NFC_SIGNATURE",
            "message": "NFC signature could not be verified",
            "nfc_signature_valid": False,
        }

    result = _get_verify_result(cert_no)
    if isinstance(result, dict) and "code" in result:
        return result

    result["nfc_signature_valid"] = True
    return result


def _get_verify_result(cert_no):
    item = frappe.db.get_value("Submission Item", {"certificate_number": cert_no}, "*", as_dict=1)
    if not item:
        frappe.local.response["http_status_code"] = 404
        return {"code": "CERT_NOT_FOUND", "message": "Certificate not found"}

    submission_status = frappe.db.get_value("Submission", item.parent_submission, "status")

    # Payment/review check
    if item.result_type == "Rejected":
        frappe.local.response["http_status_code"] = 410
        return {"code": "CERT_WITHDRAWN", "message": "Certificate not available — item was rejected"}

    if submission_status not in ("Shipped", "Ready for Pickup", "Completed"):
        frappe.local.response["http_status_code"] = 425
        return {"code": "TOO_EARLY", "message": "Verification not yet available — submission still in progress"}

    ref_code = None
    description = None
    description_ar = None
    mintmark = None
    if item.item_reference:
        ref = frappe.get_value("Item Reference Catalog", item.item_reference,
            ["ref_code", "description_en", "description_ar", "mintmark"], as_dict=1)
        if ref:
            ref_code = ref.ref_code
            description = ref.description_en
            description_ar = ref.description_ar
            mintmark = ref.mintmark

    final_grade_str = ""
    if item.final_grade:
        grade_doc = frappe.get_value("Grade Scale Master", item.final_grade, "grade_name")
        if grade_doc:
            final_grade_str = grade_doc

    # Population context computed inline
    population_context = None
    if ref_code and item.final_grade:
        all_certs = frappe.get_all("Submission Item",
            filters={
                "item_reference": item.item_reference,
                "result_type": ("in", ("Encapsulated", "Details")),
            },
            fields=["final_grade"]
        )
        at_grade = sum(1 for c in all_certs if c.final_grade == item.final_grade)
        higher = sum(1 for c in all_certs if c.final_grade != item.final_grade and _grade_numeric(c.final_grade) > _grade_numeric(item.final_grade))
        lower = sum(1 for c in all_certs if c.final_grade != item.final_grade and _grade_numeric(c.final_grade) < _grade_numeric(item.final_grade))
        population_context = {
            "at_grade": at_grade,
            "higher": higher,
            "lower": lower,
            "is_top_grade": higher == 0
        }

    return {
        "certificate_number": item.certificate_number,
        "ref_code": ref_code,
        "result_type": item.result_type or "Encapsulated",
        "label_country_denom": item.label_country_denom or "",
        "label_year_line": item.label_year_line or "",
        "mintmark": mintmark,
        "label_series_line": item.label_series_line,
        "final_grade": final_grade_str,
        "designations": [],
        "holder_type": item.holder_type or "",
        "images": {
            "obverse": item.images_obverse,
            "reverse": item.images_reverse
        },
        "graded_on": cstr(item.graded_on) if item.graded_on else "",
        "description": description,
        "description_ar": description_ar,
        "population_context": population_context,
        "nfc_signature_valid": None
    }


def _grade_numeric(grade_name):
    if not grade_name:
        return 0
    import re
    nums = re.findall(r'\d+', grade_name)
    return int(nums[0]) if nums else 0
