# IGA DocType Analysis & Missing Components

## Status Summary

### ✅ All 38 DocTypes Created
All DocTypes from the Phase 1 plan have been created successfully.

### ⚠️ Conflicts & Overlaps Identified

#### 1. **Module Settings vs IGA Grading Settings**
**Conflict Type:** Functional Overlap

**Module Settings** (Old - Keep):
- Reference code generation settings
- Registry points formula (grade_weight, population_weight, value_weight)
- Grade Scoring Configuration (child table)
- Country Configuration (child table)

**IGA Grading Settings** (New - Keep):
- Scoring components (6 approved components)
- Grade map (JSON)
- Penalty rules (JSON)
- VAT rate
- Certificate prefix
- Tracking ID prefix
- Bulk min items default

**Resolution:** Both should coexist. They serve different purposes:
- **Module Settings** = Reference catalog & registry configuration
- **IGA Grading Settings** = Production grading workflow configuration

**Action Required:** None - no conflict

---

#### 2. **Graded Items Archive vs Submission Item**
**Conflict Type:** Functional Overlap

**Graded Items Archive** (Old):
- Links to Item Reference Catalog
- Grade parsing and validation
- Certification number (unique)
- Status: Graded/QC/Shipped
- Auto-naming: IGA-ARCH-.#####

**Submission Item** (New):
- Child table of Submission
- Certificate number allocation
- Full grading workflow
- Result types
- Images, NFC, designations

**Resolution:** **Graded Items Archive is redundant** - Submission Item is the authoritative record.

**Action Required:**
1. Mark Graded Items Archive as deprecated
2. Create data migration script: Graded Items Archive → Submission Item
3. Update Population Report to read from Submission Item instead
4. Keep Archive DocType for historical data only (read-only)

---

#### 3. **Registry Points vs Rewards Ledger**
**Conflict Type:** Different Purposes

**Registry Points** (Old):
- Auto-calculates registry points using formula
- Pulls score from Module Settings
- Pulls population from Graded Items Archive
- Manual value entry
- Auto-naming: {reference_item}-{grade_full}

**Rewards Ledger** (New):
- Membership rewards tracking
- Earn/Redeem/Expire transactions
- Points balance
- Links to submissions and invoices

**Resolution:** No conflict - different purposes:
- **Registry Points** = Collection scoring for leaderboards
- **Rewards Ledger** = Membership loyalty program

**Action Required:** None - no conflict

---

#### 4. **Country Configuration vs Country Master**
**Conflict Type:** Functional Overlap

**Country Configuration** (Old):
- Child table in Module Settings
- Used for webform nationality source

**Country Master** (New):
- Standalone master data
- ISO codes, currency, region
- Has mint flag
- Status (Active/Inactive)

**Resolution:** **Country Configuration is redundant** - Country Master is more complete.

**Action Required:**
1. Migrate data from Country Configuration → Country Master
2. Update Module Settings to link to Country Master instead of child table
3. Update IGA Membership Application nationality field to link to Country Master

---

### 🔴 Missing JavaScript Files (33 DocTypes)

#### Critical (Need JS for User Interaction):
1. **submission.js** - Most critical - workflow, stage transitions, calculations
2. **submission_item.js** - Certificate allocation, grade validation, image upload
3. **membership_subscriptions.js** - Credit management, renewal logic
4. **member_registry_sets.js** - Slot fill validation, score calculation
5. **service_master.js** - Pricing calculations, tier validation
6. **item_reference_catalog.js** - Already exists ✅

#### Important (Need JS for Validation/UX):
7. **grade_scale_master.js** - Grade validation
8. **designation_master.js** - Designation validation
9. **mint_error_master.js** - Error validation
10. **problem_definitions.js** - Problem validation
11. **holder_types_master.js** - Size validation
12. **label_template_master.js** - Template preview
13. **membership_plans.js** - Plan comparison, feature display
14. **rewards_ledger.js** - Balance calculation
15. **registry_set_definitions.js** - Slot management
16. **registry_categories.js** - Category management

#### Settings (Need JS for Configuration):
17. **iga_grading_settings.js** - JSON validation, component management
18. **membership_settings.js** - Rate calculations
19. **submission_workflow_settings.js** - Station management
20. **nfc_settings.js** - Payload validation
21. **label_print_settings.js** - Printer management
22. **shipping_settings.js** - Insurance tier management

#### Child Tables (Usually don't need JS):
23. **grading_scoring_component.js** - Not needed (child table)
24. **member_registry_set_slot.js** - Not needed (child table)
25. **registry_set_slots.js** - Not needed (child table)
26. **submission_item_designation.js** - Not needed (child table)
27. **submission_item_mint_error.js** - Not needed (child table)
28. **submission_item_problem.js** - Not needed (child table)
29. **workflow_station.js** - Not needed (child table)
30. **shipping_insurance_tier.js** - Not needed (child table)

#### Low Priority (Simple Masters):
31. **country_master.js** - Simple master, minimal JS needed
32. **reference_code_generator.js** - Backend only, no JS needed
33. **grade_scoring_configuration.js** - Child table, no JS needed

---

## JavaScript Files Priority Order

### Phase 1 - Critical (Week 1)
1. **submission.js**
2. **submission_item.js**
3. **membership_subscriptions.js**
4. **service_master.js**

### Phase 2 - Important (Week 2)
5. **member_registry_sets.js**
6. **grade_scale_master.js**
7. **designation_master.js**
8. **mint_error_master.js**
9. **problem_definitions.js**
10. **holder_types_master.js**

### Phase 3 - Settings (Week 3)
11. **iga_grading_settings.js**
12. **membership_settings.js**
13. **membership_plans.js**
14. **rewards_ledger.js**
15. **submission_workflow_settings.js**

### Phase 4 - Registry (Week 4)
16. **registry_set_definitions.js**
17. **registry_categories.js**
18. **label_template_master.js**
19. **nfc_settings.js**
20. **label_print_settings.js**
21. **shipping_settings.js**

### Phase 5 - Optional (Week 5)
22. **country_master.js**

---

## Data Migration Required

### 1. Graded Items Archive → Submission Item
```python
# Migration script needed:
# For each record in Graded Items Archive:
# 1. Create Submission (if not exists)
# 2. Create Submission Item with:
#    - certificate_number from Archive
#    - item_reference from Archive
#    - final_grade from Archive
#    - result_type = "Encapsulated"
#    - current_stage = "Completed"
# 3. Mark Archive record as migrated
```

### 2. Country Configuration → Country Master
```python
# Migration script needed:
# For each record in Country Configuration child table:
# 1. Create Country Master record
# 2. Map fields appropriately
# 3. Update Module Settings to remove child table
# 4. Update IGA Membership Application nationality field
```

---

## Recommended Actions

### Immediate (This Week)
1. ✅ Create JavaScript files for Phase 1 (4 files)
2. ⚠️ Test Submission workflow end-to-end
3. ⚠️ Create data migration scripts
4. ⚠️ Update Population Report to use Submission Item

### Short Term (Next 2 Weeks)
1. Create JavaScript files for Phase 2 & 3 (14 files)
2. Execute data migrations
3. Mark deprecated DocTypes as read-only
4. Update documentation

### Medium Term (Next Month)
1. Create remaining JavaScript files
2. Comprehensive testing
3. User training materials
4. API development (deferred per plan)

---

## DocType Dependency Map

```
Customer (ERPNext Core)
  ├─> Membership Subscriptions
  │     ├─> Membership Plans
  │     └─> Rewards Ledger
  ├─> Submission
  │     ├─> Service Master
  │     ├─> Submission Item
  │     │     ├─> Item Reference Catalog
  │     │     ├─> Grade Scale Master
  │     │     ├─> Designation Master
  │     │     ├─> Mint Error Master
  │     │     ├─> Problem Definitions
  │     │     ├─> Holder Types Master
  │     │     └─> Label Template Master
  │     └─> Sales Invoice (ERPNext Core)
  └─> Member Registry Sets
        ├─> Registry Set Definitions
        │     ├─> Registry Categories
        │     └─> Registry Set Slots
        └─> Submission Item (for certificate validation)

Item Reference Catalog
  ├─> Country Master
  └─> Reference Code Generator

Settings (Singletons)
  ├─> IGA Grading Settings
  ├─> Membership Settings
  ├─> Submission Workflow Settings
  ├─> NFC Settings
  ├─> Label Print Settings
  └─> Shipping Settings

Deprecated (Keep for Historical Data)
  ├─> Module Settings (partial - keep registry formula)
  ├─> Graded Items Archive (migrate to Submission Item)
  └─> Country Configuration (migrate to Country Master)
```

---

## Next Steps

1. **Create Phase 1 JavaScript files** (submission.js, submission_item.js, membership_subscriptions.js, service_master.js)
2. **Test critical workflows** (submission creation, certificate allocation, membership management)
3. **Create migration scripts** (Graded Items Archive, Country Configuration)
4. **Update Population Report** to use Submission Item
5. **Continue with Phase 2-5 JavaScript files**

---

**Document Version:** 1.0  
**Created:** 2026-05-17  
**Status:** Analysis Complete - Ready for Implementation
