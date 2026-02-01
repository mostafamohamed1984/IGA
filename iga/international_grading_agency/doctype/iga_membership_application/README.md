# IGA Membership Application Module

## Overview
Complete implementation of the IGA Membership Application system with public web form, automatic validation, and customer creation.

## Files Created

### 1. DocType Definition
- `iga_membership_application.json` - 27 fields across 3 sections
- `iga_membership_application.py` - Python controller with validation logic
- `iga_membership_application.js` - Client-side validation and UI enhancements

### 2. Web Form
- `web_form/iga_membership_application_form/` - Public-facing form
- Route: `/membership-application`
- Arabic labels with RTL support

## Field Structure

### Section A: Membership + Customer Data (12 fields)
1. `membership_tier` - Silver/Gold/Diamond (Required)
2. `full_name` - Min 3 chars, trimmed (Required)
3. `gender` - ذكر/أنثى/أفضل عدم الذكر
4. `date_of_birth` - Must be <= today
5. `nationality` - Free text
6. `national_id_or_passport` - Free text
7. `mobile_primary` - Phone validation (Required)
8. `mobile_secondary` - Phone validation
9. `email` - Unique, validated (Required)
10. `preferred_contact_method` - واتساب/مكالمة/Email (Required, Default: واتساب)
11. `address_text` - Long text
12. `accept_terms` - Must be checked (Required)

### Section B: Survey Questions (11 fields)
13. `user_profile_type` - Profile type (Required)
14. `collectibles_interest` - MultiSelect (Required)
15. `expected_items_first_3_months` - Range selection (Required)
16. `avg_item_value_range` - Value range
17. `acceptable_grading_price_range` - Price range (Required)
18. `pay_more_when` - MultiSelect
19. `used_foreign_graders_before` - نعم/لا (Required)
20. `foreign_company_name` - Conditional (shows if نعم)
21. `choose_iga_reasons` - MultiSelect (Required)
22. `iga_barriers` - MultiSelect (Required)
23. `top_3_priorities` - MultiSelect, MAX 3 (Required)

### Section C: System Fields (4 fields)
24. `naming_series` - .YY.-.MM.-.#### (Hidden, Auto)
25. `membership_id` - Copy of doc.name (Read-only, Unique)
26. `valid_from` - Auto-set to today on creation (Read-only)
27. `valid_thru` - Auto-calc: valid_from + 12 months - 1 day (Read-only)

## Validation Rules

### Python Controller (`validate` method):
- ✅ Full name: min 3 chars, trim spaces
- ✅ Date of birth: must be <= today
- ✅ Phone format: 10-15 digits
- ✅ Email uniqueness: enforced
- ✅ Accept terms: must be checked
- ✅ Top 3 priorities: max 3 selections
- ✅ Valid_from: locked after first save
- ✅ Valid_thru: auto-calculated

### Client Script (JavaScript):
- ✅ Top 3 priorities: real-time validation
- ✅ Email format: real-time validation
- ✅ Date of birth: future date prevention

## Automation Scripts

### 1. Auto-set Validity Dates (Before Save)
```python
from frappe.utils import today, getdate, add_months, add_days

# Set valid_from on first creation
if not doc.valid_from:
    doc.valid_from = today()

# Calculate valid_thru: 12 months - 1 day
doc.valid_thru = add_days(add_months(getdate(doc.valid_from), 12), -1)
```

### 2. Set Membership ID (After Insert)
```python
if not doc.membership_id:
    doc.membership_id = doc.name
    doc.db_set("membership_id", doc.membership_id, update_modified=False)
```

### 3. Lock Valid_From (Before Save)
```python
if not doc.is_new():
    old = doc.get_doc_before_save()
    if old and doc.valid_from != old.valid_from:
        doc.valid_from = old.valid_from
```

## Customer Auto-Creation

### Whitelisted Method: `create_customer_from_membership`
Creates or updates:
- **Customer** record (using full_name, email, mobile)
- **Contact** record (linked to customer)
- **Address** record (if address_text provided)

**Usage:**
```python
frappe.call({
    method: 'iga.international_grading_agency.doctype.iga_membership_application.iga_membership_application.create_customer_from_membership',
    args: {
        membership_name: 'membership_id'
    }
})
```

## Web Form Configuration

### Settings:
- **Route**: `/membership-application`
- **Login Required**: No (Public)
- **Allow Multiple**: No
- **Allow Edit**: Yes
- **Allow Incomplete**: Yes
- **Published**: Yes

### Arabic Labels:
- Title: "طلب عضوية IGA"
- Button: "تقديم"
- Success Message: "شكرًا لتقديمك! سيتم مراجعة طلبك قريبًا"

### Introduction Text:
```html
<p>مرحبًا بك في نموذج طلب عضوية IGA</p>
<p>الرجاء ملء جميع الحقول المطلوبة</p>
<p><a href="/terms">الشروط والأحكام</a> | <a href="/privacy">سياسة الخصوصية</a></p>
```

## Installation Steps

### 1. Install/Update the App
```bash
cd ~/frappe-bench
bench --site [your-site] migrate
bench --site [your-site] clear-cache
bench restart
```

### 2. Configure Web Form
1. Go to: **Website → Web Form → iga-membership-application-form**
2. Click **Get Fields** to fetch all fields from DocType
3. Reorder fields if needed (Section A → Section B, hide Section C)
4. Update introduction text with Terms & Privacy URLs
5. Save and **Publish**

### 3. Test the Form
- Access: `https://yoursite.com/membership-application`
- Fill out form as guest user
- Verify validations work
- Check document creation in backend

### 4. Create Customer Records
- Open membership application
- Click **Create/Update Customer** button
- Verify Customer, Contact, and Address created

## Naming Convention

Format: `.YY.-.MM.-.####`

Examples:
- `26-02-0001` (February 2026, first application)
- `26-02-0002` (February 2026, second application)
- `26-03-0001` (March 2026, first application)

## Business Rules

1. **Membership Duration**: Fixed 12 months from valid_from
2. **Email Uniqueness**: One membership per email
3. **Valid_From Lock**: Cannot be changed after creation
4. **Top 3 Priorities**: Enforced maximum 3 selections
5. **Terms Acceptance**: Mandatory checkbox

## Next Steps

1. ✅ **Add Terms & Privacy Pages** - Create web pages for links
2. ✅ **Configure Email Notifications** - Send confirmation emails
3. ✅ **Add Payment Integration** - If membership fees required
4. ✅ **Create Membership Card Print Format** - For physical cards
5. ✅ **Set Up Renewal Workflow** - Auto-notify before expiry

## Testing Checklist

- [ ] Create membership via web form (guest user)
- [ ] Verify naming series: 26-02-0001
- [ ] Check valid_from = today
- [ ] Check valid_thru = valid_from + 12 months - 1 day
- [ ] Test top_3_priorities validation (max 3)
- [ ] Test email uniqueness
- [ ] Test date_of_birth future date prevention
- [ ] Test phone format validation
- [ ] Test accept_terms requirement
- [ ] Test foreign_company_name conditional display
- [ ] Create customer from membership
- [ ] Verify Customer, Contact, Address created
- [ ] Test month rollover (26-01-9999 → 26-02-0001)

## Support

For issues or questions, contact: mustafanazieer@gmail.com

---

**Implementation Status:** ✅ COMPLETE  
**Ready for:** Testing & Deployment  
**Created:** 2026-02-01
