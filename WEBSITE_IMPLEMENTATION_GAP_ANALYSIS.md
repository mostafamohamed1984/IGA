# IGA Website Implementation Gap Analysis

**Date:** 2026-05-17  
**Comparing:** Website Developer Brief v3.0 vs Current ERP Implementation

---

## Executive Summary

**DocTypes:** ✅ 38/38 Created (100%)  
**JavaScript Handlers:** ✅ 27/38 Created (71%)  
**Backend Python Methods:** ⚠️ 0/15 Implemented (0%)  
**API Endpoints:** ⚠️ 0/38 Implemented (0%)  
**Website Pages:** ❌ Not Started  

---

## 1. Missing Backend Components

### 1.1 API Gateway Layer
**Status:** ❌ Not Implemented

The Website Brief requires a complete Public API Layer at `/api/v1/...` with 7 distinct APIs:

1. **Verify API** (2 endpoints)
   - GET /api/v1/verify/{cert_no}
   - POST /api/v1/verify/nfc

2. **Population API** (2 endpoints)
   - GET /api/v1/population/reference/{ref_code}
   - GET /api/v1/population/search

3. **Submission Tracking API** (1 endpoint)
   - GET /api/v1/tracking/{tracking_id}

4. **Submission API** (5 endpoints)
   - POST /api/v1/submissions
   - GET /api/v1/submissions
   - GET /api/v1/submissions/{submission_no}
   - POST /api/v1/submissions/{submission_no}/cancel
   - POST /api/v1/submissions/quote

5. **Registry API** (7 endpoints)
   - GET /api/v1/registry/categories
   - GET /api/v1/registry/sets
   - GET /api/v1/registry/sets/{set_code}
   - GET /api/v1/registry/my-sets
   - POST /api/v1/registry/my-sets
   - PUT /api/v1/registry/my-sets/{member_set_no}/slots
   - GET /api/v1/registry/leaderboard/{set_code}

6. **Membership API** (7 endpoints)
   - GET /api/v1/membership/plans
   - POST /api/v1/membership/subscribe
   - GET /api/v1/membership/subscription
   - POST /api/v1/membership/subscription/cancel
   - GET /api/v1/membership/rewards
   - POST /api/v1/membership/rewards/redeem

7. **Support API** (4 endpoints)
   - POST /api/v1/support/tickets
   - GET /api/v1/support/tickets
   - GET /api/v1/support/tickets/{ticket_no}
   - POST /api/v1/support/tickets/{ticket_no}/messages

**Total:** 28 API endpoints across 7 APIs

**Action Required:**
- Create API gateway layer in ERPNext
- Implement OAuth2/JWT authentication
- Implement rate limiting (public endpoints)
- Implement response caching (Verify, Population)
- Implement all 28 endpoints per API Map specification

---

### 1.2 Backend Python Methods Called by JavaScript
**Status:** ⚠️ 0/15 Implemented

The JavaScript files created call backend methods that don't exist yet:

#### submission.py
- `generate_proforma_invoice()` - Creates proforma invoice on submission
- `get_active_subscription()` - Validates membership before submission

#### membership_subscriptions.py
- `renew_subscription()` - Handles subscription renewal

#### member_registry_sets.py
- `recalculate_score()` - Recalculates registry set score

#### iga_grading_settings.py
- `test_grading_calculation()` - Tests grading calculator

#### submission_workflow_settings.py
- `test_automation()` - Tests automation rules

#### nfc_settings.py
- `test_nfc_connection()` - Tests NFC API connection
- `generate_nfc_data()` - Generates test NFC chip data

#### label_print_settings.py
- `print_test_label()` - Sends test print to printer
- `preview_template()` - Generates label preview
- `check_printer_status()` - Checks printer status

#### shipping_settings.py
- `test_carrier_connection()` - Tests carrier API
- `calculate_shipping()` - Calculates shipping cost
- `track_shipment()` - Tracks shipment via carrier API

#### item_reference_catalog.py
- `generate_reference_code()` - Auto-generates reference codes

#### label_template_master.py
- `preview_template()` - Generates template preview

**Action Required:**
- Implement all 15 backend methods
- Add proper error handling and validation
- Add unit tests for each method

---

### 1.3 Price Guide System
**Status:** ❌ Not Implemented

Website Brief §3 (Price Guide) requires:
- Price Guide DocType (not created)
- Manual data entry interface in ERP
- Custom API endpoint (contract TBD with Eng. Mostafa)
- Search by reference, category, country, year, mint, variety, designation
- Hierarchical browse alternative
- Values by grade table/chart
- Last updated date
- Editorial notes field

**Action Required:**
- Create Price Guide DocType
- Create Price Guide Entry child table (grade → value mapping)
- Implement Price Guide API endpoint
- Create ERP form for manual data entry
- Add editorial notes field

---

### 1.4 Support Ticket Types
**Status:** ⚠️ Partial Implementation

Website Brief requires 4 specific ticket types:
1. General ✅ (native ERPNext Issue)
2. Offer ❌ (Make an Offer from Verify page)
3. Report Certificate ❌ (Report from Verify page)
4. Guarantee Claim ❌ (Grade Guarantee claims)

**Current:** Using native ERPNext Issue DocType  
**Missing:** Custom fields for:
- `ticket_type` (Select: General, Offer, Report Certificate, Guarantee Claim)
- `related_certificate` (Link to Submission Item)
- `offer_amount` (Currency, for Offer type)

**Action Required:**
- Extend Issue DocType with custom fields
- Add validation for ticket type-specific fields
- Update Support API to handle all 4 types

---

### 1.5 NFC Integration
**Status:** ❌ Not Implemented

Website Brief §5.7 and §6.3 require:
- NFC chip encoding during Slabbing stage
- Signed payload generation
- POST /api/v1/verify/nfc endpoint
- Signature validation
- Web NFC support on website

**Current:** NFC Settings DocType exists, but no implementation

**Action Required:**
- Implement NFC chip encoding workflow
- Create signature generation logic
- Implement NFC verification endpoint
- Add `nfc_signature_valid` field to Verify API response

---

### 1.6 Dealer Program Flow
**Status:** ⚠️ Partial Implementation

Website Brief §2.2 (Journey 5) requires:
- Dealer Program membership (DEALER plan code) ✅
- Submit on behalf of end collector ✅ (fields exist)
- Dealer reference number ✅ (field exists)
- End collector email notification ❌
- Dealer dashboard view ❌
- Dealer-submitted items aggregation ❌

**Action Required:**
- Implement end collector notification on completion
- Create Dealer dashboard view in website
- Add dealer-specific filters to Submission API

---

### 1.7 Rewards System
**Status:** ⚠️ Partial Implementation

Rewards Ledger DocType exists ✅  
**Missing:**
- Automatic reward point accrual on submission payment ❌
- Redemption validation (max_redeem_pct from plan) ❌
- Point expiry automation ❌
- Membership API rewards endpoints ❌

**Action Required:**
- Implement reward accrual on Sales Invoice payment
- Implement redemption validation
- Create scheduled job for point expiry
- Implement Membership API rewards endpoints

---

### 1.8 Registry Scoring System
**Status:** ⚠️ Partial Implementation

Registry DocTypes exist ✅  
**Missing:**
- Automatic score calculation ❌
- Rank calculation within set ❌
- Completion percentage calculation ❌
- Leaderboard generation ❌
- Slot fill validation (certificate ownership) ❌

**Action Required:**
- Implement scoring algorithm per Registry Set Definition
- Create scheduled job for rank recalculation
- Implement slot fill validation
- Implement Registry API endpoints

---

## 2. Missing DocTypes

### 2.1 Price Guide
**Status:** ❌ Not Created

**Required Fields:**
- reference_item (Link to Item Reference Catalog)
- category
- country
- year
- mint
- variety
- designation
- grade_values (Table: grade → value mapping)
- last_updated
- editorial_notes
- status (Active/Draft)

**Action Required:**
- Create Price Guide DocType
- Create Price Guide Entry child table

---

### 2.2 CMS/Content Management
**Status:** ❌ Not Created

Website Brief references "CMS read or fixture" for:
- News & Updates
- Authorized Dealers Directory
- FAQ
- Glossary
- Grade Guarantee content
- Security & Counterfeit Awareness content

**Options:**
1. Use ERPNext Web Page DocType (native)
2. Create custom News, FAQ, Glossary DocTypes
3. Use fixtures (JSON files)

**Action Required:**
- Decide on CMS approach
- Create necessary DocTypes or fixtures
- Implement CMS API endpoints

---

## 3. Workflow & Automation Gaps

### 3.1 Submission Workflow
**Status:** ⚠️ Partial Implementation

**Stages Defined:** ✅ (in Submission Workflow Settings)  
**Missing:**
- Automatic stage transitions ❌
- SLA tracking ❌
- On Hold state handling ❌
- Automation rules execution ❌
- Email notifications per stage ❌

**Action Required:**
- Implement workflow state machine
- Create automation rule engine
- Implement SLA tracking
- Create notification templates

---

### 3.2 Certificate Number Allocation
**Status:** ⚠️ Needs Verification

Website Brief §3 (Services) states:
> "certificate numbers allocated atomically per item"

**Current:** Submission Item has `certificate_number` field  
**Unclear:** Is atomic allocation implemented?

**Action Required:**
- Verify atomic allocation on submission creation
- Implement if missing
- Add uniqueness constraint
- Add auto-naming rule

---

### 3.3 Invoice Generation
**Status:** ⚠️ Partial Implementation

**Required:**
- Proforma Invoice on submission creation ❌
- Sales Invoice before Packing stage ❌
- Membership Sales Invoice on subscription ❌
- VAT calculation (14%) ❌
- Bulk discount application ❌
- Credit application ❌
- Down payment handling ❌

**Action Required:**
- Implement automatic invoice generation
- Create invoice calculation logic
- Implement discount and credit application

---

### 3.4 Image Management
**Status:** ❌ Not Implemented

Website Brief requires:
- Obverse and reverse images uploaded during Imaging stage
- Images linked to certificate
- Images served via CDN
- Images visible on Verify API

**Current:** Submission Item has `images` field (JSON)  
**Missing:** Upload workflow, CDN integration

**Action Required:**
- Implement image upload during Imaging stage
- Configure CDN (or use ERPNext file storage)
- Add image URLs to Verify API response

---

## 4. Data Migration Required

### 4.1 Graded Items Archive → Submission Item
**Status:** ⚠️ Migration Script Needed

**Graded Items Archive** is deprecated but contains historical data.

**Action Required:**
- Create migration script
- Map fields: certificate_number, item_reference, grade, status
- Set result_type = "Encapsulated"
- Set current_stage = "Completed"
- Mark Archive records as migrated

---

### 4.2 Country Configuration → Country Master
**Status:** ⚠️ Migration Script Needed

**Country Configuration** (child table in Module Settings) is deprecated.

**Action Required:**
- Create migration script
- Migrate to Country Master
- Update Module Settings to remove child table
- Update IGA Membership Application nationality field

---

## 5. Website Pages Not Started

### 5.1 Public Pages (18 pages)
**Status:** ❌ Not Started

1. Home
2. About Us
3. Services
4. Pricing & Turnaround
5. Membership (browse plans)
6. Submit (info page)
7. Verify
8. Tracking
9. Resources
10. Price Guide
11. Registry (browse)
12. News & Updates
13. Contact Us
14. Authorized Dealers Directory
15. Authorized Dealer Program (landing)
16. Grade Guarantee
17. Security & Counterfeit Awareness
18. Numismatic Glossary
19. Holders & Labels Reference

---

### 5.2 Authenticated Pages (10 pages)
**Status:** ❌ Not Started

1. Login / Sign Up
2. Dashboard
3. My Submissions
4. Submission Detail
5. My Membership
6. Invoices
7. Rewards
8. Registry / My Collection
9. Support Tickets
10. Dealer View (Dealer Program only)

---

## 6. Security & Infrastructure Gaps

### 6.1 Authentication
**Status:** ❌ Not Implemented

**Required:**
- OAuth2/JWT token issuance
- Token validation middleware
- httpOnly cookie storage
- Forgot Password flow
- Session management

**Action Required:**
- Implement OAuth2 server in ERPNext
- Create token validation middleware
- Implement password reset flow

---

### 6.2 Rate Limiting
**Status:** ❌ Not Implemented

**Required:**
- Public endpoints rate-limited per IP
- Authenticated endpoints scoped to token holder
- 429 TooManyRequests response

**Action Required:**
- Implement rate limiting middleware
- Configure limits per endpoint
- Add rate limit headers to responses

---

### 6.3 Caching
**Status:** ❌ Not Implemented

**Required:**
- Verify API cached 30-120s
- Population API cached 30-120s
- Cache invalidation on Submission Item state changes

**Action Required:**
- Implement Redis caching layer
- Configure cache TTLs
- Implement cache invalidation hooks

---

## 7. Testing Gaps

### 7.1 Unit Tests
**Status:** ❌ Not Created

**Required:**
- DocType validation tests
- Backend method tests
- API endpoint tests
- Workflow tests

**Action Required:**
- Create test suite
- Achieve >80% code coverage

---

### 7.2 Integration Tests
**Status:** ❌ Not Created

**Required:**
- End-to-end submission flow
- Membership signup → submission → invoice → payment
- Registry set creation → slot fill → score calculation
- Verify API all response states

**Action Required:**
- Create integration test suite
- Test all user journeys from Website Brief §2.2

---

## 8. Documentation Gaps

### 8.1 API Documentation
**Status:** ❌ Not Created

**Required:**
- OpenAPI/Swagger spec
- Request/response examples
- Error code reference
- Authentication guide

**Action Required:**
- Generate OpenAPI spec from API Map
- Create developer documentation

---

### 8.2 User Documentation
**Status:** ❌ Not Created

**Required:**
- Submission guidelines
- Membership terms
- Grading standards (PDF)
- FAQ

**Action Required:**
- Create user-facing documentation
- Generate PDFs for download

---

## 9. Priority Action Plan

### Phase 1: Critical Backend (Week 1-2)
1. ✅ Create all JavaScript handlers (DONE)
2. ⚠️ Implement API Gateway layer
3. ⚠️ Implement Verify API (2 endpoints)
4. ⚠️ Implement Tracking API (1 endpoint)
5. ⚠️ Implement Submission API (5 endpoints)
6. ⚠️ Implement authentication (OAuth2/JWT)
7. ⚠️ Implement certificate number atomic allocation
8. ⚠️ Implement invoice generation (Proforma, Sales)

### Phase 2: Membership & Registry (Week 3)
1. ⚠️ Implement Membership API (7 endpoints)
2. ⚠️ Implement Registry API (7 endpoints)
3. ⚠️ Implement rewards accrual and redemption
4. ⚠️ Implement registry scoring and leaderboards
5. ⚠️ Implement Support API (4 endpoints)

### Phase 3: Population & Price Guide (Week 4)
1. ⚠️ Implement Population API (2 endpoints)
2. ⚠️ Create Price Guide DocType
3. ⚠️ Implement Price Guide API
4. ⚠️ Create data migration scripts

### Phase 4: Website Frontend (Week 5-8)
1. ❌ Create public pages (18 pages)
2. ❌ Create authenticated pages (10 pages)
3. ❌ Implement bilingual EN/AR with RTL
4. ❌ Integrate all API endpoints
5. ❌ Implement NFC tap verification (Web NFC)

### Phase 5: Testing & Deployment (Week 9-10)
1. ❌ Create unit tests
2. ❌ Create integration tests
3. ❌ Performance testing
4. ❌ Security audit
5. ❌ Production deployment

---

## 10. Summary Statistics

| Component | Status | Progress |
|-----------|--------|----------|
| **DocTypes** | ✅ Complete | 38/38 (100%) |
| **JavaScript Handlers** | ✅ Mostly Complete | 27/38 (71%) |
| **Backend Methods** | ❌ Not Started | 0/15 (0%) |
| **API Endpoints** | ❌ Not Started | 0/28 (0%) |
| **Website Pages** | ❌ Not Started | 0/28 (0%) |
| **Data Migrations** | ❌ Not Started | 0/2 (0%) |
| **Tests** | ❌ Not Started | 0% |
| **Documentation** | ❌ Not Started | 0% |

**Overall Progress:** ~25% (DocTypes and JS handlers only)

---

## 11. Coordination Required

### With Eng. Mostafa Nazeer (ERP Integration Lead)
1. API Gateway architecture and implementation approach
2. Price Guide endpoint contract
3. Authentication strategy (OAuth2 vs JWT vs ERPNext native)
4. Rate limiting and caching strategy
5. NFC integration approach
6. Image storage and CDN configuration

### With IGA Leadership
1. Brand identity assets (logo, colors, typography, imagery)
2. Final Grade Guarantee policy text
3. Security & Counterfeit Awareness content
4. Glossary content
5. Authorized Dealers list
6. News & Updates content

---

**Document Status:** Gap Analysis Complete  
**Next Step:** Coordinate with Eng. Mostafa on API Gateway implementation  
**Estimated Remaining Effort:** 8-10 weeks full-time development
