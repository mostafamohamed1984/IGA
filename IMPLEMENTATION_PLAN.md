# IGA Frappe App - Complete Implementation Plan

## Executive Summary

This document outlines the complete implementation plan to integrate the IGA Website Developer Brief v3.0 requirements with the existing Frappe ERPNext application. The plan covers all missing DocTypes, APIs, workflows, and integrations needed for Phase 1 launch.

---

## Current Status Analysis

### ✅ Already Implemented (Reference Module)
- Module Settings with Grade Scoring Configuration
- Reference Code Generator
- Item Reference Catalog (101 fields)
- Graded Items Archive
- Population Report
- Registry Points
- IGA Membership Application (basic structure)

### ❌ Missing Core Components

#### 1. **Submission Management System**
- Submission DocType (main submission record)
- Submission Item DocType (child table for items)
- Submission workflow stages
- Certificate number allocation
- Tracking ID generation

#### 2. **Service & Pricing Master Data**
- Service Master DocType (tiers, categories, pricing)
- Holder Types Master
- Designation Master
- Grade Scale Master

#### 3. **Membership & Customer Management**
- Enhanced Membership Application (survey questions)
- Membership Subscription DocType
- Membership Rewards/Credits system
- Customer auto-creation integration

#### 4. **Registry System**
- Registry Category DocType
- Registry Set Definition DocType
- Registry Member Set DocType
- Registry Slot DocType
- Leaderboard calculation

#### 5. **Support & Ticketing**
- Support Ticket DocType
- Ticket Message DocType (child table)
- Ticket types: General, Offer, Report Certificate, Guarantee Claim

#### 6. **Public API Layer (7 APIs)**
- Verify API (GET /api/v1/verify/{cert_no})
- Population API (GET /api/v1/population/...)
- Tracking API (GET /api/v1/tracking/{tracking_id})
- Submission API (POST /api/v1/submissions)
- Support API (POST /api/v1/support/tickets)
- Registry API (GET /api/v1/registry/...)
- Membership API (GET /api/v1/membership/...)

#### 7. **Invoicing & Payment Integration**
- Proforma Invoice generation
- Sales Invoice generation
- Down payment handling
- Credit application
- Rewards redemption

---

## Phase 1 Implementation Roadmap

### **Stage 1: Master Data & Configuration (Week 1-2)**

#### 1.1 Service Master DocType
```python
# Fields:
- service_code (unique)
- service_name
- category (Modern Coins, Early Modern, Medieval, etc.)
- tier (Value, Standard, Express, Priority)
- price_egp
- turnaround_days
- max_declared_value_egp
- is_active
```

#### 1.2 Holder Types Master
```python
# Fields:
- holder_code
- holder_name
- size_range (13-40mm, 41-65mm, Multi-item)
- description
- has_nfc (default: Yes)
```

#### 1.3 Designation Master
```python
# Fields:
- designation_code (PL, DCAM, FBL, Plus, Star, etc.)
- designation_name_en
- designation_name_ar
- ngc_equivalent
- pcgs_equivalent
- description
```

#### 1.4 Grade Scale Master
```python
# Fields:
- grade_code (MS70, MS69, etc.)
- grade_name
- numeric_value
- category (Mint State, Proof, Circulated, etc.)
- description
- sort_order
```

**Deliverables:**
- 4 new DocTypes with JSON definitions
- Python controllers with validation
- Fixture files for initial data
- Import scripts for bulk data

---

### **Stage 2: Submission Management System (Week 3-4)**

#### 2.1 Submission DocType (Main)
```python
# Core Fields:
- submission_no (auto-generated: SUB-YYYY-####)
- tracking_id (unique, 12-char alphanumeric)
- customer (Link to Customer)
- submission_date
- service_tier (Link to Service Master)
- category
- is_bulk (checkbox)
- uses_credit (checkbox)
- submission_source (Customer/Dealer/Walk-in/Partner/Migration)

# Dealer Fields:
- dealer (Link to Customer, if Dealer Program)
- submitted_on_behalf_of (email)
- dealer_reference_no

# Status & Workflow:
- customer_visible_status (Created/Received/Grading/Slabbing/QC/Imaging/Shipped/Ready for Pickup/Completed/On Hold)
- internal_stage (more granular)
- on_hold_reason
- eta

# Financial:
- proforma_invoice (Link to Sales Invoice)
- sales_invoice (Link to Sales Invoice)
- total_amount_egp
- vat_amount_egp
- down_payment_applied
- credits_applied
- payment_status

# Items:
- items (Table: Submission Item)
- items_count
- items_breakdown (JSON: per-stage counts)

# Timestamps:
- received_date
- grading_complete_date
- completed_date
```

#### 2.2 Submission Item DocType (Child Table)
```python
# Fields:
- certificate_number (unique, allocated on creation)
- item_reference (Link to Item Reference Catalog)
- declared_value_egp
- declared_grade
- current_stage (Created/Received/Grading/Slabbing/QC/Imaging/Shipped/Completed)
- result_type (Encapsulated/Details/Not Encapsulated/Rejected)
- final_grade
- designations (Table MultiSelect)
- holder_type (Link to Holder Types Master)
- graded_on
- images_obverse (Attach Image)
- images_reverse (Attach Image)
- nfc_chip_id
- nfc_signature
- public_notes
- internal_notes
```

#### 2.3 Certificate Number Allocation
```python
# Logic:
- Allocate atomically on Submission creation
- Format: IGA-{YEAR}-{SEQUENCE-8-digits}
- Example: IGA-2026-00000001
- Use database locking to prevent duplicates
- Store in Submission Item immediately
```

#### 2.4 Tracking ID Generation
```python
# Logic:
- Generate on Submission creation
- Format: 12-character alphanumeric (uppercase)
- Example: A3K9M2P7Q1R5
- Ensure uniqueness
- Public-facing identifier
```

#### 2.5 Submission Workflow
```python
# Stages:
1. Created → Proforma Invoice issued
2. Received → Physical intake, barcodes assigned
3. Grading → Six scoring components evaluated
4. Slabbing → NFC encoded, encapsulated
5. QC → Senior grader review
6. Imaging → Photos uploaded to CDN
7. Shipped/Ready for Pickup → Carrier tracking or counter hold
8. Completed → Delivery confirmed, Sales Invoice finalized

# On Hold:
- Can occur at any stage
- Non-positional (banner display)
- Reversible
- Requires reason
```

**Deliverables:**
- 2 new DocTypes (Submission, Submission Item)
- Certificate allocation logic with locking
- Tracking ID generator
- Workflow state machine
- Stage transition validations
- Email notifications per stage

---

### **Stage 3: Enhanced Membership System (Week 5)**

#### 3.1 Update IGA Membership Application
Add survey questions from Field_Spec.html:
```python
# New Fields (B) Survey Questions:
- user_profile_type (Select)
- collectibles_interest (MultiSelect)
- expected_items_first_3_months (Select)
- avg_item_value_range (Select)
- acceptable_grading_price_range (Select)
- pay_more_when (MultiSelect)
- used_foreign_graders_before (Select)
- foreign_company_name (Data, conditional)
- choose_iga_reasons (MultiSelect)
- iga_barriers (MultiSelect)
- top_3_priorities (MultiSelect, max 3)
```

#### 3.2 Membership Subscription DocType
```python
# Fields:
- subscription_no (auto)
- customer (Link)
- plan_code (SILVER/GOLD/DIAMOND/DEALER)
- billing_period (Monthly/Annual)
- start_date
- end_date
- status (Active/Inactive/Cancelled/Expired)
- auto_renew (checkbox)
- credits_remaining
- credits_total
- membership_sales_invoice (Link)
- renewal_date
- cancelled_date
- cancellation_reason
```

#### 3.3 Membership Rewards DocType
```python
# Fields:
- customer (Link)
- transaction_type (Earn/Redeem/Expire)
- points
- balance_after
- related_submission (Link, if Earn)
- related_invoice (Link, if Redeem)
- transaction_date
- expiry_date
- notes
```

#### 3.4 Customer Auto-Creation
```python
# On Membership Application Submit:
1. Check if Customer exists (by email)
2. If not, create Customer:
   - customer_name = full_name
   - customer_type = Individual/Company
   - email_id = email
   - mobile_no = mobile_primary
   - customer_group = IGA Members
3. Link Customer to Membership Application
4. Create Membership Subscription
5. Issue Membership Sales Invoice
```

**Deliverables:**
- Updated Membership Application with 10+ survey fields
- Membership Subscription DocType
- Membership Rewards DocType
- Customer auto-creation hook
- Membership card generation (PDF)

---

### **Stage 4: Registry System (Week 6-7)**

#### 4.1 Registry Category DocType
```python
# Fields:
- category_code (unique)
- category_name_en
- category_name_ar
- description
- sort_order
- is_active
```

#### 4.2 Registry Set Definition DocType
```python
# Fields:
- set_code (unique)
- set_name_en
- set_name_ar
- category (Link to Registry Category)
- description
- total_slots
- slots (Table: Registry Slot Definition)
- scoring_rules (JSON)
- is_public (checkbox)
- created_by_iga (checkbox)
```

#### 4.3 Registry Slot Definition (Child Table)
```python
# Fields:
- slot_number
- slot_name
- required_reference (Link to Item Reference Catalog, optional)
- required_grade_min
- required_grade_max
- required_designations (MultiSelect)
- points_base
- points_multiplier
```

#### 4.4 Registry Member Set DocType
```python
# Fields:
- member_set_no (auto)
- customer (Link)
- set_definition (Link to Registry Set Definition)
- set_name_custom (optional)
- slots_filled (Table: Registry Member Slot)
- total_slots
- filled_slots
- completion_percentage
- total_score
- rank (within set definition)
- is_public (checkbox, opt-in)
- created_date
- last_updated
```

#### 4.5 Registry Member Slot (Child Table)
```python
# Fields:
- slot_number
- slot_definition (Link to Registry Slot Definition)
- certificate_number (Link to Submission Item)
- item_reference (Link, auto-filled)
- grade (auto-filled)
- designations (auto-filled)
- slot_score
- filled_date
```

#### 4.6 Slot Fill Validation
```python
# On slot fill:
1. Verify certificate_number exists
2. Verify certificate belongs to customer
3. Verify certificate matches slot requirements:
   - Reference item (if specified)
   - Grade range
   - Designations
4. Calculate slot_score
5. Recalculate member set total_score
6. Update rank within set definition
```

#### 4.7 Leaderboard Calculation
```python
# Per Set Definition:
1. Query all Member Sets for this definition
2. Filter by is_public = Yes (for public leaderboard)
3. Order by total_score DESC
4. Assign rank
5. Cache results (refresh on slot fill)
```

**Deliverables:**
- 4 new DocTypes (Category, Set Definition, Member Set, Slot Definition)
- Slot fill validation logic
- Score calculation engine
- Leaderboard query report
- Public/private visibility controls

---

### **Stage 5: Support & Ticketing System (Week 8)**

#### 5.1 Support Ticket DocType
```python
# Fields:
- ticket_no (auto: TICK-YYYY-####)
- customer (Link)
- subject
- ticket_type (General/Offer/Report Certificate/Guarantee Claim)
- status (Open/In Progress/Waiting/Resolved/Closed)
- priority (Low/Medium/High/Urgent)
- related_submission (Link, optional)
- related_certificate (Data, optional)
- messages (Table: Ticket Message)
- assigned_to (Link to User)
- created_date
- last_update
- resolved_date
- closed_date
```

#### 5.2 Ticket Message (Child Table)
```python
# Fields:
- message_no
- sender (Link to User or Customer)
- sender_type (Customer/Staff)
- message_body (Long Text)
- attachments (Attach)
- sent_date
- is_internal (checkbox, staff-only notes)
```

#### 5.3 Make an Offer Flow
```python
# From Verify page:
1. User clicks "Make an Offer" on certificate
2. Form captures:
   - offer_amount
   - message
   - contact_details
3. Creates Support Ticket:
   - ticket_type = "Offer"
   - related_certificate = cert_no
   - subject = "Offer on {cert_no}"
   - message = offer details
4. IGA staff relay to certificate owner manually
```

**Deliverables:**
- 2 new DocTypes (Support Ticket, Ticket Message)
- Ticket creation API
- Email notifications
- Staff assignment logic
- Offer form integration

---

### **Stage 6: Public API Layer (Week 9-10)**

#### 6.1 Verify API
```python
# GET /api/v1/verify/{cert_no}
# Response:
{
  "certificate_number": "IGA-2026-00000001",
  "result_type": "Encapsulated",
  "label_country_denom": "Egypt - 5 Piastres",
  "label_year_line": "1952 AD",
  "label_series_line": "King Farouk",
  "final_grade": "MS65",
  "designations": ["PL"],
  "holder_type": "Standard (13-40mm)",
  "images": {
    "obverse": "https://cdn.iga.com/...",
    "reverse": "https://cdn.iga.com/..."
  },
  "graded_on": "2026-01-15",
  "nfc_signature_valid": true
}

# Status Codes:
- 200: Verified (Encapsulated/Details, Shipped/Ready)
- 404: Not Found
- 410: Gone (Rejected)
- 425: Too Early (not yet Shipped)
- 429: Rate Limited
- 401: Invalid Signature (NFC)
```

#### 6.2 NFC Verify API
```python
# POST /api/v1/verify/nfc
# Request:
{
  "nfc_chip_id": "...",
  "nfc_signature": "..."
}
# Response: Same as GET verify, plus signature validation
```

#### 6.3 Population API
```python
# GET /api/v1/population/reference/{ref_code}
# Response:
{
  "ref_code": "CO-EGY-1952-047",
  "title": "Egypt 5 Piastres 1952",
  "population_matrix": [
    {"grade": "MS70", "count": 0},
    {"grade": "MS69", "count": 2},
    {"grade": "MS68", "count": 5},
    ...
  ],
  "total_population": 47,
  "last_updated": "2026-01-22T10:30:00Z"
}

# GET /api/v1/population/search
# Query params: category, country, year, mint, variety, designation
# Response: Array of population summaries
```

#### 6.4 Tracking API
```python
# GET /api/v1/tracking/{tracking_id}
# Response:
{
  "tracking_id": "A3K9M2P7Q1R5",
  "customer_visible_status": "Grading",
  "items_count": 5,
  "items_breakdown": {
    "Created": 0,
    "Received": 0,
    "Grading": 3,
    "Slabbing": 2,
    "QC": 0,
    "Imaging": 0,
    "Shipped": 0,
    "Completed": 0
  },
  "eta": "2026-02-05",
  "last_event": {
    "stage": "Grading",
    "timestamp": "2026-01-22T14:20:00Z",
    "note": "Items in grading process"
  },
  "on_hold": false,
  "on_hold_reason": null
}

# Status Codes:
- 200: OK
- 404: Tracking ID not found
- 429: Rate Limited
```

#### 6.5 Submission API
```python
# POST /api/v1/submissions
# Request:
{
  "service_tier": "Standard",
  "category": "Modern Coins",
  "is_bulk": false,
  "uses_credit": false,
  "submission_source": "Customer",
  "dealer": null,
  "submitted_on_behalf_of": null,
  "dealer_reference_no": null,
  "items": [
    {
      "item_reference": "CO-EGY-1952-047",
      "declared_value": 5000,
      "declared_grade": "MS65"
    }
  ]
}

# Response:
{
  "submission_no": "SUB-2026-0001",
  "tracking_id": "A3K9M2P7Q1R5",
  "proforma_invoice_no": "PINV-2026-0001",
  "status": "Created",
  "items": [
    {
      "certificate_number": "IGA-2026-00000001",
      "item_reference": "CO-EGY-1952-047"
    }
  ],
  "total_amount_egp": 935,
  "vat_amount_egp": 130.90,
  "total_with_vat": 1065.90
}

# Status Codes:
- 201: Created
- 400: Validation Error
- 401: Unauthorized
- 402: Payment Required (membership inactive)
- 403: Not Entitled (tier not allowed)
- 409: Subscription Inactive
```

#### 6.6 Support API
```python
# POST /api/v1/support/tickets
# Request:
{
  "subject": "Question about grading",
  "ticket_type": "General",
  "body": "...",
  "related_submission": null,
  "related_certificate": null,
  "attachments": []
}

# Response:
{
  "ticket_no": "TICK-2026-0001",
  "status": "Open",
  "created_date": "2026-01-22T15:00:00Z"
}

# POST /api/v1/support/tickets/{ticket_no}/messages
# Request:
{
  "message_body": "...",
  "attachments": []
}

# Response:
{
  "message_no": 2,
  "sent_date": "2026-01-22T15:05:00Z"
}
```

#### 6.7 Registry API
```python
# GET /api/v1/registry/categories (public)
# GET /api/v1/registry/sets (public)
# GET /api/v1/registry/sets/{code} (public)
# GET /api/v1/registry/my-sets (member)
# POST /api/v1/registry/my-sets (member)
# PUT /api/v1/registry/my-sets/{no}/slots (member)
# GET /api/v1/registry/leaderboard/{code}
```

#### 6.8 Membership API
```python
# GET /api/v1/membership/plans (public)
# POST /api/v1/membership/subscribe (member)
# GET /api/v1/membership/subscription (member)
# POST /api/v1/membership/subscription/cancel (member)
# GET /api/v1/membership/rewards (member)
# POST /api/v1/membership/rewards/redeem (member)
```

**Deliverables:**
- 7 API modules with versioned endpoints
- Rate limiting (per IP for public, per token for member)
- OAuth2/JWT authentication
- Response caching (Verify, Population)
- API documentation (Swagger/OpenAPI)
- Error handling with standard codes
- Audit logging

---

### **Stage 7: Invoicing & Payment Integration (Week 11)**

#### 7.1 Proforma Invoice Generation
```python
# On Submission creation:
1. Calculate total:
   - Sum of (item_count × service_tier_price)
   - Apply bulk discount if is_bulk
   - Add VAT (14%)
2. Create Sales Invoice:
   - invoice_type = "Proforma"
   - customer = submission.customer
   - items = submission items
   - status = "Pending"
3. Link to Submission
4. Send email with PDF
```

#### 7.2 Sales Invoice Generation
```python
# Before Submission packing:
1. Create Sales Invoice:
   - invoice_type = "Sales"
   - customer = submission.customer
   - items = submission items (actual results)
   - Apply down_payment if paid
   - Apply credits if uses_credit
   - status = "Pending"
2. Link to Submission
3. Send email with PDF
```

#### 7.3 Down Payment Handling
```python
# Fields on Submission:
- down_payment_required (calculated)
- down_payment_amount
- down_payment_paid (checkbox)
- down_payment_date
- down_payment_reference

# Logic:
- Down payment = 50% of proforma total (configurable)
- Required before Received stage
- Applied to Sales Invoice
```

#### 7.4 Credit Application
```python
# On Submission with uses_credit:
1. Check customer's credits_remaining
2. Calculate credit_to_apply = min(credits_remaining, invoice_total)
3. Deduct from Membership Subscription
4. Apply to Sales Invoice
5. Log in Membership Rewards (Redeem)
```

#### 7.5 Rewards Awarding
```python
# On Sales Invoice payment confirmation:
1. Calculate points = invoice_total × plan_multiplier
2. Create Membership Rewards (Earn)
3. Add to customer's balance
4. Set expiry_date = +12 months
```

**Deliverables:**
- Proforma Invoice auto-generation
- Sales Invoice auto-generation
- Down payment tracking
- Credit application logic
- Rewards awarding logic
- Invoice PDF templates
- Email notifications

---

### **Stage 8: Testing & Documentation (Week 12)**

#### 8.1 Unit Tests
- Test each DocType's validation logic
- Test certificate allocation (concurrency)
- Test tracking ID generation (uniqueness)
- Test workflow transitions
- Test API endpoints (all status codes)
- Test slot fill validation
- Test score calculation
- Test invoice generation

#### 8.2 Integration Tests
- Test full submission flow (creation → completion)
- Test membership signup → subscription → rewards
- Test registry set creation → slot fill → leaderboard
- Test support ticket creation → messages → resolution
- Test API authentication & rate limiting

#### 8.3 Performance Tests
- Test Verify API under load (1000 req/s)
- Test Population API caching
- Test Tracking API response time
- Test concurrent certificate allocation

#### 8.4 Documentation
- API documentation (Swagger)
- User guides (staff & members)
- Admin configuration guide
- Deployment guide
- Troubleshooting guide

**Deliverables:**
- Test suite (pytest)
- Test coverage report (>80%)
- Performance test results
- Complete documentation set

---

## Data Migration Plan

### 1. Historical Reference Items
- Export from existing system
- Map to Item Reference Catalog fields
- Bulk import via Data Import Tool
- Validate ref_codes

### 2. Historical Graded Items
- Export from existing system
- Map to Submission Item fields
- Allocate certificate numbers
- Import with status = "Completed"

### 3. Existing Customers
- Export from existing system
- Map to Customer fields
- Create Membership Subscriptions
- Import with historical data

---

## Deployment Checklist

### Pre-Deployment
- [ ] All DocTypes created and tested
- [ ] All APIs implemented and tested
- [ ] Fixtures loaded (grades, services, holders, designations)
- [ ] Master data imported (references, customers)
- [ ] Email templates configured
- [ ] PDF templates configured
- [ ] SSL certificates installed
- [ ] CDN configured for images
- [ ] Backup strategy in place

### Deployment
- [ ] Deploy to staging environment
- [ ] Run full test suite
- [ ] User acceptance testing (UAT)
- [ ] Performance testing
- [ ] Security audit
- [ ] Deploy to production
- [ ] Monitor logs and errors
- [ ] Train staff

### Post-Deployment
- [ ] Monitor API performance
- [ ] Monitor error rates
- [ ] Collect user feedback
- [ ] Address bugs and issues
- [ ] Plan Phase 2 features

---

## Phase 2 Features (Deferred)

### 1. Mobile Application
- Native iOS and Android apps
- Same Public API Layer
- NFC tap verification
- Push notifications

### 2. Banknotes and Trading Cards
- Activate as live grading categories
- Load category-specific master data
- Update forms and workflows

### 3. Verify Warning Flags
- Add public_warnings[] field to Verify API
- Support: Counterfeit Holder, Reported Stolen, Mechanical Error, Removed from Population
- Display warnings on Verify result

### 4. Photograde
- Visual grading reference library
- Curated reference images
- Grade comparison tool

### 5. Coin Explorer
- Full catalog depth (CoinFacts-style)
- Mintage, history, varieties
- Editorial commentary

### 6. Cross-Service Stolen Items Database
- Industry-wide integration
- Stolen items flagging
- Verification against external databases

### 7. Public Registry Leaderboard Marketing
- Curated public showcases
- Top-collector profiles
- Awards program
- Annual recognition

### 8. Full Peer-to-Peer Marketplace
- Offer DocType
- Counter-offers
- Public offers feed per cert
- Payment handling
- Dispute resolution

---

## Technical Stack

### Backend
- **Framework:** Frappe (Python)
- **Database:** MariaDB
- **Cache:** Redis
- **Queue:** RQ (Redis Queue)
- **API:** REST (JSON)
- **Auth:** OAuth2 / JWT

### Frontend
- **Admin:** Frappe Desk (built-in)
- **Public Website:** Frappe Portal / Custom
- **Mobile:** React Native (Phase 2)

### Infrastructure
- **Server:** Ubuntu 20.04 LTS
- **Web Server:** Nginx
- **App Server:** Gunicorn
- **CDN:** Cloudflare / AWS CloudFront
- **Storage:** AWS S3 (images)
- **Email:** SMTP / SendGrid
- **Monitoring:** Sentry / New Relic

---

## Resource Requirements

### Development Team
- 1 × Senior Frappe Developer (full-time, 12 weeks)
- 1 × Frontend Developer (part-time, 6 weeks)
- 1 × QA Engineer (part-time, 4 weeks)
- 1 × DevOps Engineer (part-time, 2 weeks)

### Infrastructure
- Staging server (2 vCPU, 4GB RAM)
- Production server (4 vCPU, 8GB RAM)
- Database server (4 vCPU, 16GB RAM)
- CDN bandwidth (1TB/month)
- S3 storage (500GB)

---

## Risk Mitigation

### Technical Risks
- **Certificate allocation race conditions:** Use database locking
- **API rate limiting bypass:** Implement IP-based + token-based limits
- **NFC signature validation:** Use industry-standard crypto libraries
- **Image storage costs:** Optimize images, use CDN caching

### Business Risks
- **Data migration errors:** Extensive testing, rollback plan
- **User adoption:** Comprehensive training, support documentation
- **Performance issues:** Load testing, horizontal scaling plan
- **Security vulnerabilities:** Regular audits, penetration testing

---

## Success Metrics

### Technical KPIs
- API response time < 200ms (p95)
- API uptime > 99.9%
- Certificate allocation success rate > 99.99%
- Zero data loss incidents

### Business KPIs
- Membership signups > 100 in first month
- Submissions > 500 in first month
- Verify API calls > 10,000 in first month
- Customer satisfaction > 4.5/5

---

## Next Steps

1. **Review and approve this plan** with IGA leadership
2. **Allocate resources** (team, infrastructure, budget)
3. **Set up development environment** (staging server, git repo)
4. **Begin Stage 1** (Master Data & Configuration)
5. **Weekly progress reviews** with stakeholders
6. **Adjust timeline** based on actual progress

---

**Document Version:** 1.0  
**Created:** 2026-01-22  
**Author:** IGA Development Team  
**Status:** Draft - Awaiting Approval
