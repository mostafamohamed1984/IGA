# IGA Coin Project Phase 1 Implementation Plan

## Goal Description
Implement the core "IGA Grading" custom application within ERPNext to manage the coin grading workflows, master data, and certification process as per Phase 1 requirements.

## Proposed Changes

### 1. IGA Custom App Infrastructure
#### [NEW] `iga_grading` App
- Initialize new Frappe app.
- Configure `hooks.py` for desktop icons, fixtures, and permissions.

### 2. Master Data DocTypes
Create the detailed reference data structures required for consistent coin identification.

#### [NEW] `Coin Type`
- **Fields:** Denomination, Country, Year, Mint Mark, Series, Composition.
- **Naming:** Auto-format based on fields (e.g., "1932-S-Quarter-Silver").

#### [NEW] `Designation`
- **Fields:** Code (MS, PF), Full Name, Description.

#### [NEW] `Grade Scale`
- **Fields:** Grade Number (1-70), Label (MS-65), Description.

### 3. Submission Management
Enable the intake of coins from customers.

#### [MODIFY] `Customer`
- Add custom field: `Customer Type` (Collector/Dealer).

#### [NEW] `Submission`
- **Fields:** Customer, Date, Status (Draft, Received, In Grading, Ready for QC, Complete, Shipped).
- **Workflow:** Transitions between statuses managed by specific roles.

#### [NEW] `Submission Item` (Child Table)
- **Fields:** Coin Type Link, Declared Value, Service Level.

### 4. Grading & Certification
The core logic for grading coins.

#### [NEW] `Coin Instance`
- **Fields:** Certification Number (Unique, Auto-generated), Submission Link, Final Grade Link, Date Graded.
- **Logic:** Generation of 8-10 digit unique cert number upon creation.

#### [NEW] `Grading Input`
- **Fields:** Linked Coin Instance, Surface (1-10), Strike (1-10), Luster (1-10), Eye Appeal (1-10), Technical Grade.
- **Logic:** Calculate final grade suggestion based on input components.

### 5. RBAC & Permissions
- **System Manager:** Full Access.
- **Grader:** Read/Write `Grading Input`, Read `Submission`, No Delete.
- **QC Officer:** Read/Write `Grading Input` (Review), Approve `Submission`.
- **Imaging Operator:** Read/Write `Image Upload` (Phase 3).
- **Operations:** Read/Write `Submission` (Intake/Shipping).

## Verification Plan

### Automated Tests
- **Unit Tests:**
  - Test Certification Number uniqueness and generation format.
  - Test Grade Calculation logic (inputs -> final score).
  - Test Submission workflow transitions.

### Manual Verification
1. **Master Data Entry:**
   - Create a sample "Coin Type" (e.g., 1884 Morgan Dollar).
   - Create a "Grade Scale" entry (e.g., MS-63).
2. **Submission Flow:**
   - Log in as "Operations".
   - Create a new Submission for a Customer.
   - Add items and submit.
   - Verify Status changes to "Received".
3. **Grading Flow:**
   - Log in as "Grader".
   - Open the Submission.
   - Create "Grading Input" for an item.
   - Verify calculated grade appears.
4. **Certification:**
   - Finalize the grading.
   - Check `Coin Instance` creation and Cert Number assignment.
