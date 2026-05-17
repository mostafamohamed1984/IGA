# IGA Backend Implementation - Complete

**Date:** 2026-05-17  
**Status:** Backend Structure Complete (No API Layer)

---

## Summary

All backend Python methods and DocTypes have been implemented within the ERPNext structure. The API layer implementation is deferred as per user requirements.

---

## Part 1: Backend Python Methods (18 methods) ✅

### 1. submission.py (2 methods)
**Location:** `doctype/submission/submission.py`

#### `generate_proforma_invoice()`
- Creates Proforma Sales Invoice for submission
- Links invoice to submission and tracking ID
- Adds service line items per submission item
- Applies discounts and VAT
- Returns invoice details

#### `get_active_subscription()`
- Retrieves active membership subscription for customer
- Filters by Active status
- Orders by end_date descending
- Returns subscription details with credits remaining

---

### 2. membership_subscriptions.py (1 method)
**Location:** `doctype/membership_subscriptions/membership_subscriptions.py`

#### `renew_subscription()`
- Renews subscription for another billing period
- Calculates new end date (monthly or annual)
- Adds included credits from plan
- Creates renewal Sales Invoice
- Returns renewal confirmation with new dates

---

### 3. member_registry_sets.py (1 method)
**Location:** `doctype/member_registry_sets/member_registry_sets.py`

#### `recalculate_score()`
- Recalculates registry set score from filled slots
- Gets numeric grade for each slot
- Applies slot weights
- Calculates completion percentage
- Updates rank within set definition
- Returns score, completion, and rank

**Validation Methods:**
- `_validate_set_definition()` - Ensures set definition is active
- `_validate_slots()` - Validates certificate ownership and completion
- `_recalculate_rank()` - Calculates rank among all member sets

---

### 4. iga_grading_settings.py (1 method)
**Location:** `doctype/iga_grading_settings/iga_grading_settings.py`

#### `test_grading_calculation()`
- Tests grading calculation with sample data
- Uses scoring components with weights
- Calculates weighted scores
- Maps total score to numeric grade (1-70)
- Returns breakdown and final grade

**Validation Methods:**
- `_validate_json_fields()` - Validates grade_map and penalty_rules JSON
- `_validate_scoring_components()` - Ensures weights sum to 100%
- `_map_score_to_grade()` - Maps score (0-100) to grade (1-70)

---

### 5. submission_workflow_settings.py (1 method)
**Location:** `doctype/submission_workflow_settings/submission_workflow_settings.py`

#### `test_automation()`
- Tests automation rules against a submission
- Finds matching rules for event
- Simulates rule execution
- Returns execution results

**Validation Methods:**
- `_validate_stages()` - Validates workflow stages
- `_validate_automation_rules()` - Validates automation rules

---

### 6. nfc_settings.py (2 methods)
**Location:** `doctype/nfc_settings/nfc_settings.py`

#### `test_nfc_connection()`
- Tests connection to NFC service API
- Sends ping request with authentication
- Returns connection status

#### `generate_nfc_data()`
- Generates test NFC chip data
- Creates payload with certificate info
- Generates HMAC signature
- Encodes payload for NFC chip
- Returns payload, signature, and encoded data

**Helper Methods:**
- `_generate_signature()` - Generates HMAC-SHA256 signature
- `_encode_payload()` - Base64 encodes payload and signature

---

### 7. label_print_settings.py (3 methods)
**Location:** `doctype/label_print_settings/label_print_settings.py`

#### `print_test_label()`
- Prints or previews test label
- Generates label HTML from submission item
- Sends to printer API if not preview mode
- Returns HTML preview or print confirmation

#### `preview_template()`
- Previews a label template
- Loads template from Label Template Master
- Generates preview HTML
- Returns formatted preview

#### `check_printer_status()`
- Checks printer status via API
- Returns online status, paper, ink, queue length
- Handles connection errors gracefully

**Validation Methods:**
- `_validate_dimensions()` - Validates label width/height (10-500mm)
- `_validate_dpi()` - Validates print DPI (150-1200)
- `_generate_label_html()` - Generates label HTML from item data

---

### 8. shipping_settings.py (3 methods)
**Location:** `doctype/shipping_settings/shipping_settings.py`

#### `test_carrier_connection()`
- Tests connection to carrier API
- Sends ping request with authentication
- Returns connection status

#### `calculate_shipping()`
- Calculates shipping cost for submission
- Gets zone base rate
- Calculates weight surcharge (50g per item)
- Adds service level fee (Standard/Express/Overnight)
- Adds insurance (1% of declared value)
- Returns cost breakdown

#### `track_shipment()`
- Tracks shipment via carrier API
- Returns tracking events with status, location, timestamp
- Handles API errors gracefully

**Validation Methods:**
- `_validate_zones()` - Validates shipping zones for duplicates

---

### 9. item_reference_catalog.py (1 method)
**Location:** `doctype/item_reference_catalog/item_reference_catalog.py`

#### `generate_reference_code()`
- Generates reference code from Module Settings template
- Maps collectible type to code (CN, MD, TK, BN, PC, CC)
- Gets or creates Reference Code Generator
- Increments sequence
- Replaces template tokens
- Returns generated code

**Validation Methods:**
- `_validate_year()` - Validates year_ad and year_ah ranges
- `_generate_ref_code_if_needed()` - Auto-generates on Active status

---

### 10. module_settings.py (2 methods)
**Location:** `doctype/module_settings/module_settings.py`

#### `generate_reference_code()` (whitelisted function)
- Generates reference code for testing
- Uses Module Settings template
- Creates or updates Reference Code Generator
- Returns generated code

#### `migrate_countries_to_master()` (whitelisted function)
- Migrates countries from Country Configuration to Country Master
- Checks for existing countries
- Creates new Country Master records
- Returns migration count

**Validation Methods:**
- `_validate_code_template()` - Validates template has valid tokens
- `_validate_registry_weights()` - Warns if all weights are zero

---

### 11. reference_code_generator.py (1 method)
**Location:** `doctype/reference_code_generator/reference_code_generator.py`

#### `preview_next_code()` (whitelisted function)
- Previews next reference code
- Gets Module Settings template
- Calculates next sequence
- Generates code with next sequence
- Returns preview code

**Helper Methods:**
- `_generate_key()` - Generates generator key from type/country/year

---

## Part 2: Price Guide System ✅

### DocTypes Created

#### 1. Price Guide (Main DocType)
**Location:** `doctype/price_guide/`

**Fields:**
- `reference_item` (Link to Item Reference Catalog) - Primary key
- `category` (Select: Modern, Early Modern, Medieval, Medals & Tokens)
- `country` (Link to Country Master)
- `year` (Int)
- `mint` (Data)
- `variety` (Data)
- `grade_values` (Table: Price Guide Entry)
- `last_updated` (Datetime, read-only)
- `updated_by` (Link to User, read-only)
- `status` (Select: Draft, Active, Archived)
- `editorial_notes` (Text Editor)

**Features:**
- Auto-populates from Item Reference Catalog
- Validates grade/designation uniqueness
- Updates metadata on save
- Clears cache on update

**JavaScript Features:**
- Status indicators
- Activate/Archive buttons
- View reference item
- View population data
- Price chart visualization
- Auto-sort grade values by numeric grade
- Validation for positive market values

---

#### 2. Price Guide Entry (Child Table)
**Location:** `doctype/price_guide_entry/`

**Fields:**
- `grade` (Link to Grade Scale Master)
- `designation` (Link to Designation Master)
- `market_value` (Currency)
- `currency` (Link to Currency, default: EGP)

**Features:**
- Editable grid
- In-list view for all fields
- Currency support

---

### Price Guide Python Methods

**Location:** `doctype/price_guide/price_guide.py`

#### `_populate_from_reference()`
- Auto-populates category, country, year, mint from reference item
- Maps collectible type to category

#### `_validate_grade_values()`
- Ensures at least one grade value exists
- Checks for duplicate grade/designation combinations

#### `before_save()`
- Updates last_updated timestamp
- Sets updated_by to current user

#### `on_update()`
- Clears cache for this price guide entry

---

## Statistics

| Component | Count | Status |
|-----------|-------|--------|
| **DocTypes** | 40 | ✅ 100% (38 original + 2 Price Guide) |
| **JavaScript Handlers** | 30 | ✅ 100% (29 original + 1 Price Guide) |
| **Backend Python Methods** | 18 | ✅ 100% |
| **Price Guide System** | 2 DocTypes | ✅ 100% |
| **API Endpoints** | 28 | ⏭️ Deferred (not needed) |
| **Website Pages** | 28 | ⏭️ Deferred (separate project) |

---

## File Structure

```
theapp/IGA/iga/international_grading_agency/
├── doctype/
│   ├── submission/
│   │   ├── submission.json
│   │   ├── submission.py ✅ (2 methods added)
│   │   └── submission.js ✅
│   ├── membership_subscriptions/
│   │   ├── membership_subscriptions.json
│   │   ├── membership_subscriptions.py ✅ (1 method added)
│   │   └── membership_subscriptions.js ✅
│   ├── member_registry_sets/
│   │   ├── member_registry_sets.json
│   │   ├── member_registry_sets.py ✅ (NEW - full implementation)
│   │   └── member_registry_sets.js ✅
│   ├── iga_grading_settings/
│   │   ├── iga_grading_settings.json
│   │   ├── iga_grading_settings.py ✅ (NEW - full implementation)
│   │   └── iga_grading_settings.js ✅
│   ├── submission_workflow_settings/
│   │   ├── submission_workflow_settings.json
│   │   ├── submission_workflow_settings.py ✅ (NEW - full implementation)
│   │   └── submission_workflow_settings.js ✅
│   ├── nfc_settings/
│   │   ├── nfc_settings.json
│   │   ├── nfc_settings.py ✅ (NEW - full implementation)
│   │   └── nfc_settings.js ✅
│   ├── label_print_settings/
│   │   ├── label_print_settings.json
│   │   ├── label_print_settings.py ✅ (NEW - full implementation)
│   │   └── label_print_settings.js ✅
│   ├── shipping_settings/
│   │   ├── shipping_settings.json
│   │   ├── shipping_settings.py ✅ (NEW - full implementation)
│   │   └── shipping_settings.js ✅
│   ├── item_reference_catalog/
│   │   ├── item_reference_catalog.json
│   │   ├── item_reference_catalog.py ✅ (NEW - full implementation)
│   │   └── item_reference_catalog.js ✅
│   ├── module_settings/
│   │   ├── module_settings.json
│   │   ├── module_settings.py ✅ (NEW - full implementation)
│   │   └── module_settings.js ✅
│   ├── reference_code_generator/
│   │   ├── reference_code_generator.json
│   │   ├── reference_code_generator.py ✅ (NEW - full implementation)
│   │   └── reference_code_generator.js ✅
│   ├── price_guide/ ✅ NEW
│   │   ├── __init__.py
│   │   ├── price_guide.json
│   │   ├── price_guide.py
│   │   └── price_guide.js
│   └── price_guide_entry/ ✅ NEW
│       ├── __init__.py
│       ├── price_guide_entry.json
│       └── price_guide_entry.py
```

---

## Testing Checklist

### Backend Methods
- [ ] Test `generate_proforma_invoice()` with sample submission
- [ ] Test `get_active_subscription()` with active/inactive subscriptions
- [ ] Test `renew_subscription()` with monthly and annual plans
- [ ] Test `recalculate_score()` with filled registry slots
- [ ] Test `test_grading_calculation()` with sample scores
- [ ] Test `test_automation()` with sample submission
- [ ] Test `generate_nfc_data()` with certificate data
- [ ] Test `print_test_label()` in preview mode
- [ ] Test `calculate_shipping()` with different zones
- [ ] Test `generate_reference_code()` with different types
- [ ] Test `migrate_countries_to_master()` migration

### Price Guide
- [ ] Create Price Guide entry with grade values
- [ ] Test auto-population from reference item
- [ ] Test grade value sorting
- [ ] Test duplicate grade/designation validation
- [ ] Test Activate/Archive workflow
- [ ] Test price chart visualization

---

## Next Steps (If Needed)

### 1. API Layer (Deferred)
If API layer is needed in the future:
- Create `/api/v1/` endpoint structure
- Implement OAuth2/JWT authentication
- Implement rate limiting
- Implement caching
- Create 28 API endpoints per Website Brief

### 2. Website Frontend (Separate Project)
- 18 public pages
- 10 authenticated pages
- Bilingual EN/AR with RTL
- Integration with API endpoints

### 3. Data Migration
- Graded Items Archive → Submission Item
- Country Configuration → Country Master

### 4. Testing
- Unit tests for all backend methods
- Integration tests for workflows
- Performance testing

---

## Dependencies

### External APIs (Optional)
- **NFC Service API** - For NFC chip encoding/verification
- **Printer API** - For label printing
- **Carrier API** - For shipment tracking

### ERPNext Core
- Sales Invoice
- Customer
- User
- Currency

---

## Notes

1. **No API Layer**: As per user requirements, API endpoints are not implemented. All functionality exists within ERPNext DocTypes and can be accessed via Frappe's native API if needed.

2. **Price Guide**: Fully functional within ERPNext. Can be managed through the desk interface. Website integration would require API endpoints (deferred).

3. **Backend Methods**: All methods are whitelisted where appropriate and can be called from JavaScript or external systems.

4. **Testing**: All backend methods should be tested within ERPNext before production use.

5. **External Services**: NFC, Printer, and Carrier integrations are stubbed and will need actual API credentials and endpoints.

---

**Status:** ✅ Backend Implementation Complete  
**Date:** 2026-05-17  
**Next Phase:** Testing & Data Migration (when ready)
