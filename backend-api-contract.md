# IGA Website — Backend API Contract

> Handoff document for the API gateway implementing the Public API Layer (`/api/v1/...`).
> Generated from frontend service definitions on 2026-05-20.

---

## 0. Read this first

**Project.** IGA (International Grading Agency, `igaverify.com`) is a professional grading and authentication authority for collectible coins, medals, and tokens. The website is a bilingual (EN/AR) public marketing surface plus an authenticated member dashboard — Verify, Submit-for-grading, Tracking, Membership, Registry / Set Collection, Support, Invoices, and a Dealer portal. The front end is a Next.js 15 (App Router, TypeScript, TanStack Query, next-intl) thin client. It talks to ERPNext only through a versioned Public API Layer hosted at `/api/v1/...`. ERPNext is never reached directly from the browser.

**Service-layer pattern (non-negotiable).** Every API call goes through one of the files under `lib/api/`. Pages never `fetch()` directly. The function signature you implement on the server **must match exactly** what is documented per-endpoint here — names, casing, response field shapes. Today each function returns a mock fixture; once your gateway is live, only the function bodies change and the entire UI keeps working with no further front-end edits.

```ts
// lib/api/verify.ts — typical pattern
export async function verifyCertificate(certNo: string): Promise<VerifyResult> {
  if (USE_MOCKS) return mockVerifyCert(certNo);
  return apiClient.get<VerifyResult>(`/verify/${certNo}`);
}
```

**Mock-to-real switch.**
```bash
NEXT_PUBLIC_USE_MOCKS=false
NEXT_PUBLIC_API_BASE_URL=https://api.igaverify.com
```
That's it. No front-end code changes needed once the gateway speaks the contract below.

**Base URL.** Every documented path is appended to `${NEXT_PUBLIC_API_BASE_URL}/api/v1`. So `GET /verify/{cert_no}` actually means `GET https://api.igaverify.com/api/v1/verify/{cert_no}`.

**Auth.** Not wired yet. Frontend currently hard-codes a single mock user (Omar Wael, Gold plan). The backend should pick a session mechanism (HttpOnly cookie session or JWT). When the choice is made, the frontend will read the session via `lib/api/user.ts → getCurrentUser()` (currently a mock). Public endpoints stay anonymous.

**Locales.** `en` (default) and `ar`. Two patterns appear in responses:
- Fields stored as parallel pairs: `description` / `description_ar`, `title` / `title_ar`, `country_name_en` / `country_name_ar`. The frontend picks the right one based on the active locale.
- Pre-resolved values: a single `description` field whose language is selected by an `Accept-Language: en|ar` header. The frontend currently expects the parallel-pair pattern for the documented endpoints, with the exception of activity-log strings (which already arrive in both forms).
The backend should default to the parallel-pair pattern unless an endpoint section says otherwise.

---

## 1. Conventions

The names in this section are **part of the contract with ERPNext**. They appear in URLs, query params, response payloads, and customer-visible UI. Never invent variants. Where a value is shown for both display and wire format, the **wire format is the uppercase code**.

| Concept | Canonical spelling | Where it lives |
|---|---|---|
| Plan codes (wire) | `SILVER`, `GOLD`, `DIAMOND`, `DEALER` | `lib/api/membership.ts:15` |
| Plan display names | `Silver`, `Gold`, `Diamond`, `Dealer Program` | `lib/api/membership.ts:16`, `lib/data/plans.ts` |
| Submission stages | `Created` · `Received` · `Grading` · `Slabbing` · `QC` · `Imaging` · `Shipped` · `Ready for Pickup` · `Completed` · `On Hold` | `lib/api/tracking.ts:4-14` |
| Result types | `Encapsulated` · `Details` · `Not Encapsulated` · `Rejected` | `lib/api/verify.ts:7-11` |
| Service tiers | `Value` · `Standard` · `Express` · `Priority` | `lib/api/submissions.ts:15` |
| Item categories | `Modern` · `Early Modern` · `Medieval` · `Medals & Tokens` · `High Value` · `Unlimited` | `lib/api/submissions.ts:16-22` |
| Service option codes (wire) | `GRADING`, `RE-GRADE`, `CROSS-OVER`, `RE-SLAB`, `BULK`, `RESTORATION` | `lib/api/submissions.ts:24-30`, `lib/data/services.ts:36-42` |
| Add-on keys | `specialLabels`, `firstReleases`, `pedigree`, `varieties`, `mintErrors`, `overSizeSlab`, `proLabAnalysis`, `detailedImaging`, `multiInsertSlab` | `lib/data/services.ts:199-264` |
| Invoice types | `Proforma Invoice` · `Sales Invoice` · `Membership Sales Invoice` | `lib/mocks/invoices.ts:1-4` |
| Invoice statuses | `Pending` · `Under Review` · `Paid` · `Cancelled` | `lib/mocks/invoices.ts:6` |
| Support ticket types | `General` · `Offer` · `Report Certificate` · `Guarantee Claim` | `lib/api/support.ts:9-13` |
| Support ticket statuses | `Open` · `In Progress` · `Awaiting Customer` · `Resolved` · `Closed` | `lib/api/support.ts:15-20` |
| Payment methods | `CASH`, `BANK_TRANSFER`, `INSTAPAY`, `OTHER` | `lib/api/submissions.ts:32` |
| Cert number format | `{submission_no}-{item_no}` zero-padded — e.g. `AA00001-03` | `lib/mocks/submissions.ts:76-79` |
| Submission number format | `AA{00000}` zero-padded to 5 digits | `lib/mocks/submissions.ts:53-55,70-72` |
| Invoice number prefixes | `PI-` (Proforma), `SI-` (Sales), `MSI-` (Membership Sales) | `lib/mocks/invoices.ts` |
| Tracking ID format | `TRK-` + 6 alphanumeric chars (no `I` or `O`) | `lib/mocks/submissions.ts:57-64` |
| Ticket number format | `TKT-` + 5 zero-padded digits | `lib/mocks/support.ts:158-162` |
| Locales | `en` (default), `ar` | `CLAUDE.md`, `messages/{en,ar}.json` |
| Currency | `EGP` throughout, always returned in the `currency` field where applicable | `lib/api/submissions.ts:107`, `lib/data/plans.ts` |
| Dates | ISO 8601 strings. Pure-date fields (`graded_on`, `submitted_on`, `date`) use `YYYY-MM-DD`. Timestamped fields (`created_at`, `last_updated`, `last_event`) use full ISO with `Z`. | All mocks |
| VAT | 14% (constant `VAT_PERCENT`) applied to grading subtotals server-side | `lib/data/services.ts:70` |
| Bulk discount | 10% off when `is_bulk === true` AND item count ≥ 5 | `lib/data/services.ts:71-72`, `lib/mocks/submissions.ts:366-368` |

### Error response shape

The frontend HTTP wrapper (`lib/api/client.ts:20-28`) throws on `!res.ok` and reads `error.message` from the JSON body. Two mock implementations also throw `ApiError` instances with a `status` code (see `lib/mocks/verify.ts:84-92` and `lib/mocks/tracking.ts:9-16`). The proposed canonical error envelope:

```json
{
  "code": "CERT_NOT_FOUND",
  "message": "Certificate not found",
  "details": { /* optional */ }
}
```

with the appropriate HTTP status (404, 410, 425, 429, 401, 422, 500). The frontend currently only reads `message`, so adding `code` is forward-compatible but not yet load-bearing. Verify and Tracking already have well-defined status semantics — see those endpoints below.

---

## 2. APIs by domain

### 2.1 client

**Source:** `lib/api/client.ts`

The shared HTTP wrapper. Exports `apiClient.get`, `apiClient.post`, `apiClient.put` and the `USE_MOCKS` boolean. All other service files dispatch through this. The wrapper:

- Builds URLs as `${NEXT_PUBLIC_API_BASE_URL}/api/v1${path}`.
- Sends `Content-Type: application/json` and merges caller headers.
- Throws `Error & { status, body }` when `res.ok` is false, with `message` taken from the response body's `.message` field (falls back to `statusText`).

Backend: respond with valid JSON for every status code, set the right HTTP status, and the frontend's error handling Just Works. No domain endpoints live here.

---

### 2.2 user (current session)

**Source:** `lib/api/user.ts`
**Mock implementation:** `lib/mocks/user.ts`

#### Types

```ts
export type MockUser = {
  id: string;
  name: string;
  nameEn: string;
  email: string;
  avatarUrl: string | null;
  plan: PlanCode;
  planStatus: "Active" | "Inactive" | "Pending";
  isDealer: boolean;
  joinedAt: string;
  rewardsBalance: number;
};
```

> **Naming note.** The type is called `MockUser` only because the frontend hasn't renamed it yet. The shape **is** the contract — rename to `CurrentUser` server-side if you prefer. `name` is the locale-appropriate display name (Arabic for `ar`, English for `en`); `nameEn` is always Latin transliteration for invoices/legal text.

#### Endpoints

##### `getCurrentUser()` → `MockUser`
- **Method + path:** `GET /api/v1/membership/me`
- **Auth:** member (any logged-in customer; required as soon as auth ships)
- **Request:** none. Backend must resolve the session.
- **Response:** `MockUser` (see above)
- **Caching guidance:** no-cache or `private, max-age=60` per session.
- **Notes:** `isDealer` is independent of `plan === "DEALER"` — backend should set `isDealer: true` for any customer linked to a dealer account, regardless of subscription plan. The dashboard uses this to gate the `/dealer` route.

---

### 2.3 verify (public, the most-hit endpoint)

**Source:** `lib/api/verify.ts`
**Mock implementation:** `lib/mocks/verify.ts`

#### Types

```ts
export type ResultType =
  | "Encapsulated"
  | "Details"
  | "Not Encapsulated"
  | "Rejected";

export type PopulationContext = {
  /** Count certified at this exact grade */
  at_grade: number;
  /** Count certified at any higher grade */
  higher: number;
  /** Count certified at any lower grade */
  lower: number;
  /** True when this cert IS the highest graded for the reference */
  is_top_grade: boolean;
};

export type VerifyResult = {
  certificate_number: string;
  ref_code?: string;                       // coin catalog reference (for cross-links)
  result_type: ResultType;
  label_country_denom: string;             // "Egypt — 1 Pound"
  label_year_line: string;                 // "1968 (AH 1387)"
  mintmark?: string;                       // "Cairo Mint", "C"
  label_series_line: string | null;
  final_grade: string;                     // "MS 65", "Details — Cleaned", "Not Genuine"
  designations: string[];                  // ["PL", "FBL"]
  holder_type: string;                     // "Standard"
  images: {
    obverse?: string;                      // absolute URL
    reverse?: string;
  };
  graded_on: string;                       // ISO date
  nfc_signature_valid?: boolean;           // set by /verify/nfc only

  description?: string;                    // "1968 (AH 1387) Egypt 1 Pound — Aswan Dam Commemorative"
  description_ar?: string;

  population_context?: PopulationContext;
};
```

#### Endpoints

##### `verifyCertificate(certNo)` → `VerifyResult`
- **Method + path:** `GET /api/v1/verify/{cert_no}`
- **Auth:** public
- **Request:** path param `cert_no` (e.g. `AA00001-01`)
- **Response:** `VerifyResult`
- **Caching guidance:** cacheable for terminal results (cert never changes once `Completed`). Set `Cache-Control: public, max-age=300, stale-while-revalidate=86400` for `Encapsulated`/`Details`/`Not Encapsulated`/`Rejected` results; `no-cache` while a submission is still in flight (return 425).
- **Error states the frontend handles** (`lib/mocks/verify.ts:94-118`):
  - `404` — certificate not found (UI shows "Not Found")
  - `410` — cert withdrawn/voided (UI shows "Cert removed")
  - `425` — submission still in progress (UI shows "Not yet available")
  - `429` — rate limited (UI shows "Too many requests")
  - `401` — reserved for future authenticated views; not yet handled distinctly
- **Notes:** the page renders six distinct visual states (200 × four `result_type` values + 404/410/425/429). `description` is the **compact coin identifier** from the catalog (not a marketing paragraph). `population_context` is aggregated server-side from the population endpoint against `final_grade`. When `higher === 0`, set `is_top_grade: true`. See TODO(api) markers in `lib/api/verify.ts:26-57`.

##### `verifyNfc(payload)` → `VerifyResult`
- **Method + path:** `POST /api/v1/verify/nfc`
- **Auth:** public
- **Request body:** `{ "payload": string }` — opaque NFC signed payload tapped off the holder.
- **Response:** `VerifyResult` plus `nfc_signature_valid: true|false`.
- **Caching guidance:** never cache (POST + per-tap).
- **Notes:** the frontend treats this as the canonical "tap-to-verify" entry point. Backend validates the cryptographic signature and returns the same shape as the cert lookup; UI shows a distinct trust badge when `nfc_signature_valid === true`.

---

### 2.4 submissions (the wizard's bread and butter)

**Source:** `lib/api/submissions.ts`
**Mock implementation:** `lib/mocks/submissions.ts`

#### Types

```ts
export type ServiceTier = "Value" | "Standard" | "Express" | "Priority";
export type ItemCategory =
  | "Modern"
  | "Early Modern"
  | "Medieval"
  | "Medals & Tokens"
  | "High Value"
  | "Unlimited";

export type ServiceOptionCode =
  | "GRADING"
  | "RE-GRADE"
  | "CROSS-OVER"
  | "RE-SLAB"
  | "BULK"
  | "RESTORATION";

export type PaymentMethod = "CASH" | "BANK_TRANSFER" | "INSTAPAY" | "OTHER";

export type SubmissionItem = {
  item_reference: string;
  declared_value: number;
  declared_grade?: string;
  service_option?: ServiceOptionCode;
  add_ons?: string[];           // ADDON_SERVICES keys
  notes?: string;
  certificate_number?: string;
  current_stage?: SubmissionStage;
  result_type?: string;
};

export type CreateSubmissionInput = {
  service_tier: ServiceTier;
  category: ItemCategory;
  is_bulk?: boolean;
  uses_credit?: boolean;
  submission_source?: "Customer" | "Dealer" | "Walk-in" | "Partner" | "Migration";
  dealer?: string;
  submitted_on_behalf_of?: string;
  dealer_reference_no?: string;
  payment_method?: PaymentMethod;
  payment_method_note?: string;
  /** Customer-applied promo code (uppercase). The ERP re-validates server-side. */
  promo_code?: string;
  items: SubmissionItem[];
};

export type SubmissionSummary = {
  submission_no: string;
  tracking_id: string;
  status: SubmissionStage;
  items_count: number;
  submitted_on: string;
  service_tier: ServiceTier;
  category: ItemCategory;
};

export type SubmissionDetail = SubmissionSummary & {
  items: SubmissionItem[];
  proforma_invoice_no: string;
  sales_invoice_no?: string;
  dealer?: string;
  submitted_on_behalf_of?: string;
  dealer_reference_no?: string;
  received_on?: string;
  grading_complete_on?: string;
  completed_on?: string;
};

export type CreateSubmissionResult = {
  submission_no: string;
  tracking_id: string;
  proforma_invoice_no: string;
  status: SubmissionStage;
  items: Array<{ certificate_number: string }>;
};

export type QuoteInput = {
  service_tier: ServiceTier;
  category: ItemCategory;
  is_bulk?: boolean;
  items: Array<Pick<SubmissionItem, "item_reference" | "declared_value" | "add_ons">>;
};

export type QuoteResult = {
  base_subtotal: number;            // tier price × items count
  addons_subtotal: number;          // sum of all add-ons across items
  subtotal_before_discount: number; // base + addons
  bulk_discount: number;            // 10% of subtotal_before_discount when is_bulk && count >= 5
  subtotal: number;                 // subtotal_before_discount - bulk_discount (pre-VAT)
  vat: number;                      // 14%
  total: number;                    // subtotal + vat
  currency: string;                 // "EGP"
};

export type ActivityEntry = {
  id: string;
  date: string;
  description: string;
  descriptionAr: string;
};
```

#### Endpoints

##### `createSubmission(input)` → `CreateSubmissionResult`
- **Method + path:** `POST /api/v1/submissions`
- **Auth:** member (and dealer, when `submission_source === "Dealer"`)
- **Request body:** `CreateSubmissionInput`
- **Response:** `CreateSubmissionResult` — server-assigned `submission_no`, `tracking_id`, `proforma_invoice_no`, and one cert number per item.
- **Caching:** no-cache.
- **Notes:** backend must re-validate `promo_code` server-side regardless of any client-side check; reject with 422 if invalid/expired. `is_bulk` is informational from the wizard — server should still verify item count ≥ `BULK_THRESHOLD` (5) before applying the 10% discount.

##### `getSubmissions()` → `SubmissionSummary[]`
- **Method + path:** `GET /api/v1/submissions`
- **Auth:** member
- **Response:** list scoped to the authenticated customer.
- **Caching:** `private, max-age=30`. Dashboard polls on focus.

##### `getSubmission(submissionNo)` → `SubmissionDetail`
- **Method + path:** `GET /api/v1/submissions/{submission_no}`
- **Auth:** member (must own the submission; 403 otherwise)
- **Response:** `SubmissionDetail` — extends `SubmissionSummary` with item array + invoice numbers + lifecycle timestamps.

##### `cancelSubmission(submissionNo)` → `void`
- **Method + path:** `POST /api/v1/submissions/{submission_no}/cancel`
- **Auth:** member
- **Request body:** `{}` (empty; future may include a reason)
- **Response:** 204 / empty body.
- **Notes:** only allowed while `status === "Created"`. Backend should 409 if the submission has already been received.

##### `getSubmissionActivity(submissionNo)` → `ActivityEntry[]`
- **Method + path:** `GET /api/v1/submissions/{submission_no}/activity`
- **Auth:** member
- **Response:** ordered ascending by `date` (ISO timestamp). Each entry carries both `description` (EN) and `descriptionAr` (AR) pre-resolved.
- **Notes:** TODO(api) marker confirms this endpoint at `lib/api/submissions.ts:140`. Used by the Submission Detail page's activity log.

##### `getSubmissionQuote(input)` → `QuoteResult`
- **Method + path:** `POST /api/v1/submissions/quote`
- **Auth:** public — the wizard is anonymous-friendly until the user submits.
- **Request body:** `QuoteInput`
- **Response:** `QuoteResult`
- **Caching:** no-cache; this is server-computed against the live pricing master.
- **Notes:** the mock implementation in `lib/mocks/submissions.ts:354-381` documents the exact calculation order: base = tier price × items, add-ons summed individually, bulk discount 10% applied to (base + add-ons), VAT 14% applied last. Backend must use the same precedence; the wizard displays each line.

---

### 2.5 membership (plans, subscription, rewards)

**Source:** `lib/api/membership.ts`
**Mock implementation:** `lib/mocks/membership.ts`

#### Types

```ts
export type PlanCode = "SILVER" | "GOLD" | "DIAMOND" | "DEALER";
export type PlanName = "Silver" | "Gold" | "Diamond" | "Dealer Program";

export type MembershipPlan = {
  code: PlanCode;
  name: PlanName;
  price_monthly: number;
  price_annual: number;
  currency: string;
  features: string[];
  credit_bundle: number;
  reward_multiplier: number;
  max_redeem_pct: number;
};

export type Subscription = {
  plan_code: PlanCode;
  plan_name: PlanName;
  status: "Active" | "Inactive" | "Pending" | "Cancelled";
  billing_period: "monthly" | "annual";
  renewal_date: string;
  credits_remaining: number;
};

export type SubscribeInput = {
  plan_code: PlanCode;
  billing_period: "monthly" | "annual";
  auto_renew?: boolean;
};

export type RewardsBalance = {
  points: number;
  ledger: Array<{
    date: string;
    description: string;
    points: number;
    type: "earn" | "redeem" | "expire";
  }>;
};

export type RedeemInput = {
  invoice_no: string;
  points: number;
};

export type RewardsLedgerEntry = {
  id: string;
  date: string;
  type: "earn" | "redeem" | "expire";
  points: number;
  related: string | null;          // related submission_no / invoice_no
  description: string;
  balance_after: number;
};
```

#### Endpoints

##### `getMembershipPlans()` → `MembershipPlan[]`
- **Method + path:** `GET /api/v1/membership/plans`
- **Auth:** public
- **Caching:** `public, max-age=3600` — plan catalog rarely changes.
- **Notes:** `features` is locale-resolved (`Accept-Language`) or duplicated as `features_ar`; today the mock returns English-only because `lib/data/plans.ts` carries both `perks` and `perksAr` arrays. Decide which pattern, then document. `DEALER` plan has `price_annual: null` in the source data — backend should serialize as `null` or `0`.

##### `subscribe(input)` → `{ invoice_no: string }`
- **Method + path:** `POST /api/v1/membership/subscribe`
- **Auth:** member
- **Request body:** `SubscribeInput`
- **Response:** `{ invoice_no: string }` — the Membership Sales Invoice (`MSI-`) created server-side.

##### `getSubscription()` → `Subscription`
- **Method + path:** `GET /api/v1/membership/subscription`
- **Auth:** member
- **Caching:** `private, max-age=60`.

##### `cancelSubscription()` → `void`
- **Method + path:** `POST /api/v1/membership/subscription/cancel`
- **Auth:** member
- **Request body:** `{}` (future: cancellation reason field)
- **Notes:** subscription remains usable until `renewal_date`; backend sets `status: "Cancelled"` but does not zero `credits_remaining`.

##### `getRewards()` → `RewardsBalance`
- **Method + path:** `GET /api/v1/membership/rewards`
- **Auth:** member
- **Notes:** the `ledger` field is a short tail (≤3-5 entries). For the full history, the dashboard calls `getRewardsLedger()` below.

##### `getRewardsLedger()` → `RewardsLedgerEntry[]`
- **Method + path:** `GET /api/v1/membership/rewards/ledger`
- **Auth:** member
- **Response:** full chronological ledger (descending by `date`) with `balance_after` precomputed.
- **Notes:** TODO(api) marker at `lib/api/membership.ts:89`. This is currently unimplemented in the gateway design; confirm path with Eng. Mostafa.

##### `redeemRewards(input)` → `{ points_remaining: number }`
- **Method + path:** `POST /api/v1/membership/rewards/redeem`
- **Auth:** member
- **Request body:** `RedeemInput` — applies `points` against `invoice_no`.
- **Notes:** server must enforce the plan's `max_redeem_pct` cap against the invoice total and reject (422) if exceeded.

---

### 2.6 registry (sets, leaderboards, achievements, watchlist, comparison)

**Source:** `lib/api/registry.ts`
**Mock implementation:** `lib/mocks/registry.ts`, `lib/mocks/registry-v2.ts`
**Shared types:** `components/features/registry/types.ts`

This domain is large because the Registry feature was re-architected (v2). Some endpoints below are mock-only or hit overlapping URLs — the v2 list represents the target contract.

#### Types — v1 (older, still in use by `/registry/sets/[setId]`)

```ts
export type RegistryCategory = {
  code: string;
  name: string;
  description: string;
  sets_count: number;
};

export type SetDefinition = {
  code: string;
  name: string;
  category_code: string;
  description: string;
  slots_count: number;
  scoring_rules: string;
};

export type SetSlot = {
  slot_no: number;
  description: string;
  required_grade?: string;
  filled_by?: string;
  certificate_number?: string;
  assigned_grade?: string;
};

export type MyOwnedCertificate = {
  certificate_number: string;
  description: string;
  grade: string;
};

export type SetDetail = SetDefinition & {
  slots: SetSlot[];
  top_members: Array<{ username: string; score: number; rank: number }>;
};

export type MemberSet = {
  member_set_no: string;
  set_definition_code: string;
  set_name: string;
  score: number;
  rank: number;
  completion_pct: number;
  is_public: boolean;
  slots: SetSlot[];
};

export type LeaderboardEntry = {
  rank: number;
  username: string;
  score: number;
  completion_pct: number;
};
```

#### Types — v2 (from `components/features/registry/types.ts`)

```ts
export type SetType = "master" | "custom";
export type SetVisibility = "public" | "private" | "showcase";

export type AchievementTier =
  | "bronze" | "silver" | "gold" | "platinum" | "legendary";

export type SetOwner = {
  customer_id: string;
  display_name: string;
  username: string;
  avatar_url?: string;
  country?: string;
  member_since?: string;
};

export type SetSlotV2 = {
  slot_no: number;
  description: string;
  required_grade?: string;
  required_reference?: string;
  weight?: number;
  filled_by?: string;
  certificate_number?: string;
  assigned_grade?: string;
  is_top_pop?: boolean;
  designation?: string;
  thumbnail_url?: string;
};

export type SetStats = {
  rank: number;
  total_rank: number;
  score: number;
  max_score: number;
  completion_pct: number;
  watchers: number;
  views: number;
};

export type MemberSetSummary = {
  id: string;
  type: SetType;
  name: string;
  category_code: string;
  category_name: string;
  owner: SetOwner;
  cover_image?: string;
  visibility: SetVisibility;
  stats: SetStats;
  slots_count: number;
  filled_count: number;
  achievements: string[];
  updated_at: string;
};

export type MemberSetDetail = MemberSetSummary & {
  narrative: string;
  theme_tags: string[];
  slots: SetSlotV2[];
  created_at: string;
  scoring_rules?: string;
};

export type ActivityEventType =
  | "set_created" | "set_completed" | "rank_changed"
  | "achievement_earned" | "top_pop_achieved" | "coin_added";

export type ActivityEvent = {
  id: string;
  type: ActivityEventType;
  actor: { customer_id: string; display_name: string; avatar_url?: string };
  timestamp: string;
  details: {
    set_id?: string;
    set_name?: string;
    achievement_code?: string;
    new_rank?: number;
    old_rank?: number;
    certificate_number?: string;
    grade?: string;
    reference_code?: string;
  };
};

export type TopCollectorEntry = {
  rank: number;
  customer_id: string;
  display_name: string;
  username: string;
  avatar_url?: string;
  country?: string;
  total_score: number;
  sets_count: number;
  achievements_count: number;
  trend: "up" | "down" | "flat";
  trend_delta?: number;
};

export type AwardWinner = {
  award_code: string;
  year: number;
  place: 1 | 2 | 3;
  customer_id: string;
  display_name: string;
  set_id?: string;
  set_name?: string;
  prize: string;
};

export type SetComment = {
  id: string;
  set_id: string;
  author: { customer_id: string; display_name: string; avatar_url?: string };
  body: string;
  created_at: string;
  likes: number;
  parent_id?: string;
};

export type TopPopEntry = {
  reference_code: string;
  description: string;
  grade: string;
  designation?: string;
  customer_id: string;
  display_name: string;
  certificate_number: string;
  certified_at: string;
};

export type ComparisonRow = {
  slot_no: number;
  description: string;
  a: { filled: boolean; grade?: string; certificate_number?: string };
  b: { filled: boolean; grade?: string; certificate_number?: string };
};

export type ComparisonResult = {
  set_a: MemberSetSummary;
  set_b: MemberSetSummary;
  rows: ComparisonRow[];
  score_a: number;
  score_b: number;
};

export type RegistryLiveStats = {
  collectors: number;
  sets: number;
  coins: number;
  awards: number;
};

export type CreateCustomSetInput = {
  name: string;
  description: string;
  category_code: string;
  theme_tags: string[];
  is_public: boolean;
  cover_image?: string;
  slots: Array<{
    slot_no: number;
    description: string;
    required_reference?: string;
    weight?: number;
  }>;
};
```

#### Endpoints

##### `getRegistryCategories()` → `RegistryCategory[]`
- **Method + path:** `GET /api/v1/registry/categories`
- **Auth:** public
- **Caching:** `public, max-age=3600`.

##### `getRegistrySets(categoryCode?)` → `SetDefinition[]`
- **Method + path:** `GET /api/v1/registry/sets?category={code}`
- **Auth:** public
- **Notes:** `getAllSets(filters?)` below uses the same path with an additional `type=master|custom` filter — collapse them in the gateway.

##### `getRegistrySet(code)` → `SetDetail`
- **Method + path:** `GET /api/v1/registry/sets/{code}`
- **Auth:** public

##### `getMySets()` → `MemberSet[]`
- **Method + path:** `GET /api/v1/registry/my-sets`
- **Auth:** member

##### `createMySet(input)` → `MemberSet`
- **Method + path:** `POST /api/v1/registry/my-sets`
- **Auth:** member
- **Request body:** `{ set_definition_code, set_name, is_public? }` (v1) **or** `CreateCustomSetInput` (v2 custom set; sent with `type: "custom"` appended by `createCustomSet`).

##### `updateSlots(memberSetNo, slots)` → `MemberSet`
- **Method + path:** `PUT /api/v1/registry/my-sets/{member_set_no}/slots`
- **Auth:** member
- **Request body:** `{ slots: Array<{ slot_no, certificate_number }> }`

##### `getLeaderboard(setCode)` → `LeaderboardEntry[]`
- **Method + path:** `GET /api/v1/registry/leaderboard/{set_code}`
- **Auth:** public
- **Caching:** `public, max-age=300` — rankings update frequently.

##### `getMyEligibleCertificates(slotDescription?)` → `MyOwnedCertificate[]`
- **Method + path:** `GET /api/v1/customer/certificates?slot={urlencoded}`
- **Auth:** member
- **Notes:** the path lives under `/customer/...`, not `/registry/...`. Backend should filter server-side by slot description (denomination/year/grade match). Source: `lib/api/registry.ts:150-156`.

##### `getAllSets(filters?)` → `MemberSetSummary[]` *(v2)*
- **Method + path:** `GET /api/v1/registry/sets?category={code}&type={master|custom}`
- **Auth:** public
- **Notes:** overlaps with `getRegistrySets()` (v1). Backend should return either `SetDefinition` (master) or `MemberSetSummary` (custom) — the frontend selects which list it calls based on the screen.

##### `getSetById(id)` → `MemberSetDetail | undefined` *(v2)*
- **Method + path:** `GET /api/v1/registry/sets/{id}`
- **Auth:** public

##### `getSetsByCategory(category)` → `MemberSetSummary[]` *(v2)*
- **Method + path:** `GET /api/v1/registry/sets?category={category}`
- **Auth:** public

##### `getMyMemberSets()` → `MemberSetSummary[]` *(v2)*
- **Method + path:** `GET /api/v1/registry/my-sets`
- **Auth:** member
- **Notes:** v2 variant of `getMySets()`; backend can return either shape under the same path if the response is upgraded site-wide.

##### `createCustomSet(input)` → `MemberSetSummary` *(v2)*
- **Method + path:** `POST /api/v1/registry/my-sets` with body `{ ...input, type: "custom" }`
- **Auth:** member

##### `updateMemberSetCover(setId, coverImageUrl)` → `void` *(v2)*
- **Method + path:** `PUT /api/v1/registry/my-sets/{setId}/cover`
- **Auth:** member, owner-only
- **Request body:** `{ cover_image: string }`

##### `updateMemberSetNarrative(setId, narrative)` → `void` *(v2)*
- **Method + path:** `PUT /api/v1/registry/my-sets/{setId}/narrative`
- **Auth:** member, owner-only
- **Request body:** `{ narrative: string }`

##### `updateMemberSetVisibility(setId, visibility)` → `void` *(v2)*
- **Method + path:** `PUT /api/v1/registry/my-sets/{setId}/visibility`
- **Auth:** member, owner-only
- **Request body:** `{ visibility: "public" | "private" | "showcase" }`

##### `getLiveStats()` → `RegistryLiveStats` *(v2)*
- **Method + path:** `GET /api/v1/registry/stats`
- **Auth:** public
- **Caching:** `public, max-age=60`.
- **Notes:** the registry homepage has a TODO at `app/[locale]/(public)/registry/page.tsx:181` suggesting WebSocket subscription for true real-time updates — for now, frontend polls.

##### `getActivityFeed(scope, scopeId?)` → `ActivityEvent[]` *(v2)*
- **Method + path:** `GET /api/v1/registry/activity?scope={global|following|set}&scope_id={id?}`
- **Auth:** public for `global`; member for `following` and `set` (scoped to caller)

##### `getMyAchievements()` → `{ earned: string[], progress: Record<string, number> }` *(v2)*
- **Method + path:** `GET /api/v1/registry/my-achievements`
- **Auth:** member

##### `getTopCollectors(filters)` → `TopCollectorEntry[]` *(v2)*
- **Method + path:** `GET /api/v1/registry/leaderboard/collectors?period={month|year|all_time}&category={code?}&country={ISO?}&page={n}`
- **Auth:** public

##### `getAwards(year=2026)` → `{ categories: AwardCategory[], winners: AwardWinner[], calendar: ... }` *(v2)*
- **Method + path:** `GET /api/v1/registry/awards?year={year}`
- **Auth:** public
- **Notes:** static `categories` and `calendar` are baked into the frontend today (`lib/data/registry-awards.ts`); backend may host only `winners` and let the rest stay client-side, or take ownership of all three.

##### `postSetComment(setId, body)` → `SetComment` *(v2)*
- **Method + path:** `POST /api/v1/registry/sets/{setId}/comments`
- **Auth:** member
- **Request body:** `{ body: string }`

##### `getSetComments(setId)` → `SetComment[]` *(v2)*
- **Method + path:** `GET /api/v1/registry/sets/{setId}/comments`
- **Auth:** public

##### `getTopPop(refCode)` → `TopPopEntry[]` *(v2)*
- **Method + path:** `GET /api/v1/registry/top-pop/{refCode}`
- **Auth:** public
- **Notes:** returns the top-graded certs known for a coin reference.

##### `getMyWatchlist()` → `MemberSetSummary[]` *(v2)*
- **Method + path:** `GET /api/v1/registry/watchlist`
- **Auth:** member

##### `addToWatchlist(setId)` → `void` *(v2)*
- **Method + path:** `POST /api/v1/registry/watchlist/{setId}`
- **Auth:** member
- **Request body:** `{}`

##### `removeFromWatchlist(setId)` → `void` *(v2)*
- **Method + path:** `DELETE /api/v1/registry/watchlist/{setId}` (the current code calls `PUT .../remove`; frontend should be aligned to `DELETE` once the backend is up)
- **Auth:** member
- **Notes:** see TODO(api) at `lib/api/registry.ts:392`.

##### `compareSets(setIdA, setIdB)` → `ComparisonResult | undefined` *(v2)*
- **Method + path:** `GET /api/v1/registry/compare?a={setIdA}&b={setIdB}`
- **Auth:** public

> **Heads-up for the backend lead:** the v2 endpoints have only frontend mocks today. The exact URL paths above are *proposed* by the frontend; confirm/adjust with Eng. Mostafa before locking the gateway routes. All v2 calls fall through to `apiClient.get/post/put` in the source files, so renaming a path is a one-line frontend change once you finalize.

---

### 2.7 support (tickets + messages — contact form, offer/report dialogs, dashboard)

**Source:** `lib/api/support.ts`
**Mock implementation:** `lib/mocks/support.ts`

#### Types

```ts
export type TicketType =
  | "General"
  | "Offer"
  | "Report Certificate"
  | "Guarantee Claim";

export type TicketStatus =
  | "Open"
  | "In Progress"
  | "Awaiting Customer"
  | "Resolved"
  | "Closed";

export type TicketMessage = {
  id: string;
  sender: "customer" | "staff";
  body: string;
  created_at: string;
  attachments?: string[];
};

export type TicketSummary = {
  ticket_no: string;
  subject: string;
  type: TicketType;
  status: TicketStatus;
  related_submission?: string;
  related_certificate?: string;
  last_updated: string;
};

export type TicketDetail = TicketSummary & {
  messages: TicketMessage[];
};

export type CreateTicketInput = {
  subject: string;
  body: string;
  type: TicketType;
  related_submission?: string;
  related_certificate?: string;
  attachments?: string[];
  // Public contact-form submissions (unauthenticated visitors) include these
  // so support can respond by email; ignored when an authenticated session
  // is present.
  guest_name?: string;
  guest_email?: string;
  guest_phone?: string;
};
```

#### Endpoints

##### `createSupportTicket(input)` → `{ ticket_no, status }`
- **Method + path:** `POST /api/v1/support/tickets`
- **Auth:** public (contact form, Offer dialog, Report-Certificate dialog) or member (dashboard)
- **Request body:** `CreateTicketInput`. When the caller is unauthenticated, `guest_name`/`guest_email`/`guest_phone` must be present (and validated).
- **Response:** trimmed payload — only `ticket_no` and `status`. Backend may freely return the full `TicketSummary`; the wrapper picks what it needs.
- **Notes:** `createTicket()` is the underlying function that returns `TicketSummary`. `createSupportTicket()` is the consumer-facing wrapper that the contact form, Offer dialog, Report-Certificate dialog, and Guarantee Claim dialog all use.

##### `createTicket(input)` → `TicketSummary`
- **Method + path:** `POST /api/v1/support/tickets`
- Same as above; returns the full summary.

##### `getTickets()` → `TicketSummary[]`
- **Method + path:** `GET /api/v1/support/tickets`
- **Auth:** member
- **Notes:** scoped to the authenticated customer.

##### `getTicket(ticketNo)` → `TicketDetail`
- **Method + path:** `GET /api/v1/support/tickets/{ticket_no}`
- **Auth:** member (owner-only; 403 otherwise)
- **Response:** `TicketDetail` includes the full `messages` array.

##### `addMessage(ticketNo, input)` → `TicketMessage`
- **Method + path:** `POST /api/v1/support/tickets/{ticket_no}/messages`
- **Auth:** member
- **Request body:** `{ body: string, attachments?: string[] }`
- **Response:** the persisted `TicketMessage` (with server-assigned `id` and `created_at`). Backend sets `sender: "customer"` from the session.

---

### 2.8 tracking (public submission lookup)

**Source:** `lib/api/tracking.ts`
**Mock implementation:** `lib/mocks/tracking.ts`

#### Types

```ts
export type SubmissionStage =
  | "Created" | "Received" | "Grading" | "Slabbing" | "QC"
  | "Imaging" | "Shipped" | "Ready for Pickup" | "Completed" | "On Hold";

export type TrackingResult = {
  tracking_id: string;
  customer_visible_status: SubmissionStage;
  items_count: number;
  items_breakdown: Partial<Record<SubmissionStage, number>>;
  eta: string | null;
  last_event: string;
};
```

#### Endpoints

##### `getTracking(trackingId)` → `TrackingResult`
- **Method + path:** `GET /api/v1/tracking/{tracking_id}`
- **Auth:** public
- **Response:** `TrackingResult`
- **Error states the frontend handles:** `404` (not found), `429` (rate limited). Mock implementation throws both at `lib/mocks/tracking.ts:53-57`.
- **Caching guidance:** `public, max-age=60`. The page polls/refreshes manually.
- **Notes:** `items_breakdown` is a partial map keyed by stage name (e.g. `{ "Received": 1, "Grading": 2 }`). `customer_visible_status` is the "rollup" status — typically the stage furthest along. `eta` is `null` for terminal states (Completed, On Hold).

---

### 2.9 population (public)

**Source:** `lib/api/population.ts`
**Mock implementation:** `lib/mocks/population.ts`

#### Types

```ts
export type PopulationTotals = {
  by_grade: Record<string, number>;
  by_designation: Record<string, number>;
};

export type PopulationByReference = {
  reference_code: string;
  totals: PopulationTotals;
  last_updated: string;  // ISO 8601
  count: number;
};

export type PopulationSearchFilters = {
  q?: string;
  category?: string;
  country?: string;
  year?: number;
  designation?: string;
  type?: string;
  sort?: "yearDesc" | "yearAsc" | "popDesc" | "popAsc";
  page?: number;
  page_size?: number;
};

export type PopulationSearchEntry = {
  reference_code: string;
  coin_name: string;
  country: string;
  country_name_en: string;
  country_name_ar: string;
  country_flag: string;
  year: number;
  category: string;
  type: string;
  totals: PopulationTotals;
  count: number;
};

export type PopulationSearchResult = {
  results: PopulationSearchEntry[];
  total_count: number;
  page: number;
  page_size: number;
};
```

#### Endpoints

##### `getPopulationByReference(refCode)` → `PopulationByReference | null`
- **Method + path:** `GET /api/v1/population/reference/{ref_code}`
- **Auth:** public
- **Caching:** `public, max-age=300, stale-while-revalidate=3600` — population shifts only when new items are graded.
- **Notes:** return `null` (not 404) for unknown refs to keep the page rendering its empty state cleanly; the wrapper passes through whatever the gateway sends. Source: Master Brief §9.4.

##### `searchPopulation(filters)` → `PopulationSearchResult`
- **Method + path:** `GET /api/v1/population/search?q=&category=&country=&year=&designation=&type=&sort=&page=&page_size=`
- **Auth:** public
- **Response:** paginated `PopulationSearchResult` with `total_count` for the UI's pager.

---

### 2.10 price-guide (public, in-repo data today)

**Source:** `lib/api/price-guide.ts`
**Mock implementation:** none — reads from `lib/data/coin-catalog.ts` directly.

#### Types

```ts
export interface PriceGuideListResponse {
  results: CoinReference[];
  total_count: number;
  page: number;
  page_size: number;
}

export interface PriceGuideFilters {
  country?: string;
  category?: string;
  designation?: string;
  has_pricing?: boolean;
  shortcut?: "top_pop" | "registry_star" | "with_pricing";
  query?: string;
  sort?: "newest" | "price_high" | "price_low" | "trending";
  page?: number;
  page_size?: number;
}
```

`CoinReference` is defined in `lib/data/coin-catalog.ts` and is large (refCode, denomination, year, country, category, series, ruler, pricing block with `byGrade` median/low/high, signals block with `trendingScore`, `isTopPopTarget`, `registryActiveSetCount`). Backend should host the catalog and expose the same shape; the frontend's `getBestGradePrice()` / `getPriceRange()` helpers operate on the response client-side.

#### Endpoints

##### `listPriceGuide(filters?)` → `PriceGuideListResponse`
- **Method + path:** `GET /api/v1/price-guide?country=&category=&designation=&has_pricing=&shortcut=&query=&sort=&page=&page_size=`
- **Auth:** public
- **Caching:** `public, max-age=600`.
- **Notes:** default `page_size` is 24. `shortcut` is a discovery-strip convenience that pre-filters to high-interest subsets.

##### `getTrending(limit=6)` → `CoinReference[]`
- **Method + path:** `GET /api/v1/price-guide/trending?limit={n}`
- **Auth:** public

##### `getTopPopTargets(limit=6)` → `CoinReference[]`
- **Method + path:** `GET /api/v1/price-guide/top-pop?limit={n}`
- **Auth:** public

##### `getRegistryStars(limit=6)` → `CoinReference[]`
- **Method + path:** `GET /api/v1/price-guide/registry-stars?limit={n}`
- **Auth:** public

> **Open contract.** `docs/master-brief.docx` flags Price Guide as TBD. The four endpoints above are the frontend's expectation; lock with Eng. Mostafa before implementing.

---

### 2.11 news (public, editorial content)

**Source:** `lib/api/news.ts`
**Mock implementation:** `lib/mocks/news.ts`

#### Types

```ts
export interface NewsArticle {
  slug: string;
  title: string;
  title_ar: string;
  excerpt: string;
  excerpt_ar: string;
  date: string | null;             // ISO date; null = evergreen
  category: string;
  category_ar: string;
}
```

#### Endpoints

##### `getLatestNews(limit=3)` → `NewsArticle[]`
- **Method + path:** `GET /api/v1/news?limit={n}`
- **Auth:** public
- **Caching:** `public, max-age=300`.

##### `getAllNews()` → `NewsArticle[]`
- **Method + path:** `GET /api/v1/news`
- **Auth:** public

##### `getNewsArticle(slug)` → `NewsArticle | null`
- **Method + path:** `GET /api/v1/news/{slug}`
- **Auth:** public

> **Note.** The current article shape is metadata-only (no body). When real editorial content lands, the detail endpoint should add `body` and `body_ar` (long-form markdown or HTML, agreed with the content team).

---

### 2.12 invoices (member)

**Source:** `lib/api/invoices.ts`
**Mock implementation:** `lib/mocks/invoices.ts`

#### Types

```ts
export type InvoiceType =
  | "Proforma Invoice"
  | "Sales Invoice"
  | "Membership Sales Invoice";

export type InvoiceStatus = "Pending" | "Under Review" | "Paid" | "Cancelled";

export type InvoiceLineItem = {
  description: string;
  qty: number;
  unit_price: number;
  total: number;
};

export type Invoice = {
  invoice_no: string;
  type: InvoiceType;
  submission_no: string | null;     // null for Membership Sales Invoices
  date: string;
  subtotal: number;
  vat: number;
  total: number;
  status: InvoiceStatus;
  down_payment_applied: number;
  credits_applied: number;
  balance_due: number;
  pdf_url: string | null;
  line_items: InvoiceLineItem[];
};
```

#### Endpoints

##### `getInvoices()` → `Invoice[]`
- **Method + path:** `GET /api/v1/invoices`
- **Auth:** member
- **Notes:** scoped to the authenticated customer; sorted descending by `date` is what the dashboard expects.

##### `getInvoice(invoiceNo)` → `Invoice | undefined`
- **Method + path:** `GET /api/v1/invoices/{invoice_no}`
- **Auth:** member (must own the invoice)
- **Response:** the full `Invoice` including `line_items`. `pdf_url` is the signed URL for the printable PDF (return `null` if not yet generated).

> **TODO(api):** confirm both routes with Eng. Mostafa (`lib/api/invoices.ts:7`).

---

### 2.13 dealer (Dealer Program members only)

**Source:** `lib/api/dealer.ts`
**Mock implementation:** `lib/mocks/dealer.ts`

#### Types

```ts
export type DealerSubmission = {
  submission_no: string;
  dealer_ref: string;
  collector_name: string;
  submitted_at: string;
  items_count: number;
  status: string;                  // current_visible_status from tracking
  total_egp: number;
};

export type DealerStats = {
  total_submissions: number;
  active_in_flight: number;
  completed_this_month: number;
  total_items_graded: number;
};

export type CollectorVolume = {
  collector_name: string;
  submissions: number;
  total_items: number;
};
```

#### Endpoints

##### `getDealerSubmissions()` → `DealerSubmission[]`
- **Method + path:** `GET /api/v1/dealer/submissions`
- **Auth:** dealer (`plan_code === "DEALER"` or `isDealer === true`)
- **Notes:** scoped to the dealer's own submissions, including those filed on behalf of named collectors.

##### `getDealerStats()` → `DealerStats`
- **Method + path:** `GET /api/v1/dealer/stats`
- **Auth:** dealer
- **Caching:** `private, max-age=60`.

##### `getDealerTopCollectors()` → `CollectorVolume[]`
- **Method + path:** `GET /api/v1/dealer/top-collectors`
- **Auth:** dealer
- **Response:** list of the dealer's most active customers (volume aggregation).

> **TODO(api):** all three dealer endpoints flagged at `lib/api/dealer.ts:6` for confirmation with Eng. Mostafa.

---

### 2.14 services (catalog — static today, ERP-driven later)

**Source:** `lib/api/services.ts`
**Mock implementation:** `lib/mocks/services.ts` (re-exports static data from `lib/data/services.ts`)

#### Types

(Defined in `lib/data/services.ts` — the API re-exports these.)

```ts
export type Category =
  | "modern" | "earlyModern" | "medieval"
  | "medalsTokens" | "highValue" | "unlimited";

export type Tier = "value" | "standard" | "express" | "priority";

export type GradingService = {
  category: Category;
  tier: Tier;
  price: number | null;            // null = contact agent
  priceLabel?: "contactAgent";
  turnaround: string;              // "14–21"
  turnaroundUnit: "days";
  maxValue: number | null;         // null = unlimited
  maxValueLabel?: "unlimited";
};

export type ServiceOptionCode =
  | "GRADING" | "RE-GRADE" | "CROSS-OVER" | "RE-SLAB" | "BULK" | "RESTORATION";

export type ServiceOption = {
  code: ServiceOptionCode;
  name: string;
  nameAr: string;
  description: string;
  descriptionAr: string;
  pricingRule: "tier_full" | "tier_minus_pct" | "contact_agent";
  discountPercent: number | null;
  autoApplied?: boolean;
};

export type AddOnService = {
  key: string;
  name: string;
  price: number | null;
  priceLabel?: "contactAgent";
  descEn: string;
  descAr: string;
};

export type PostageMatrix = {
  valueBreakpoints: number[];      // N breakpoints = N+1 value columns
  pieceBreakpoints: number[];      // N breakpoints = N+1 piece rows
  rates: PostageRow[];
};
```

> **Important — internal vs wire casing.** The frontend uses lowercase keys (`"modern"`, `"value"`) inside the services catalog and uppercase display names (`"Modern"`, `"Value"`) inside the Submission types. The mocks contain mapping tables (`TIER_KEY`, `CATEGORY_KEY` in `lib/mocks/submissions.ts:22-36`). When the gateway implements these endpoints, the **lowercase form is the wire format** for `/services/*` responses. The Submission endpoints (`/submissions`) use the uppercase display names.

#### Endpoints

##### `getGradingServices()` → `GradingService[]`
- **Method + path:** `GET /api/v1/services/grading`
- **Auth:** public
- **Caching:** `public, max-age=3600`.
- **Notes:** 11 rows total. The mock list reflects the IGA Pricing Flyer (Modern × 3 tiers, Early Modern × 3 tiers, Medieval Standard, Medals/Tokens × 2 tiers, High Value Priority, Unlimited Priority).

##### `getServiceOptions()` → `ServiceOption[]`
- **Method + path:** `GET /api/v1/services/options`
- **Auth:** public
- **Notes:** 6 codes total. `BULK` carries `autoApplied: true` and is not displayed in the wizard option picker.

##### `getAddOnServices()` → `AddOnService[]`
- **Method + path:** `GET /api/v1/services/add-ons`
- **Auth:** public
- **Notes:** 9 keys total (`specialLabels`, `firstReleases`, `pedigree`, `varieties`, `mintErrors`, `overSizeSlab`, `proLabAnalysis`, `detailedImaging`, `multiInsertSlab`). One is "contact agent" priced.

##### `getPostageMatrix()` → `PostageMatrix`
- **Method + path:** `GET /api/v1/services/postage`
- **Auth:** public
- **Notes:** 3 piece-range rows × 5 value-column matrix. The 21+ piece row is `perPiece: true`, meaning the cell value is per-piece, not flat. `calculatePostage()` in the frontend handles the computation client-side.

---

### 2.15 promo (new, mock-only today)

**Source:** `lib/api/promo.ts`
**Mock data:** `lib/data/promo-codes.ts`

#### Types

```ts
export type PromoDiscountType = "percent" | "fixed";

export type PromoCode = {
  code: string;                    // uppercase
  type: PromoDiscountType;
  value: number;                   // percent 0-100 OR EGP amount
  description: string;
  expiresAt: string | null;        // ISO date; null = no expiry
  active: boolean;
};

export type PromoValidationReason = "not_found" | "expired" | "inactive";

export type PromoValidation =
  | { valid: true; code: PromoCode }
  | { valid: false; reason: PromoValidationReason };
```

#### Endpoints

##### `validatePromoCode(code)` → `PromoValidation`
- **Method + path:** `POST /api/v1/promo/validate`
- **Auth:** public
- **Request body:** `{ code: string }` — frontend normalizes to uppercase before sending.
- **Response:** `PromoValidation` discriminated-union.
- **Notes:** the server **must** re-validate against the live coupon catalog and never trust the client value. `validatePromoCode` is a UX convenience to surface errors early; the canonical re-validation happens inside `createSubmission`.

---

## 3. ERPNext data model dependencies

These are the doctype additions / new fields the gateway will need so it can satisfy the contracts above. Confirm with Eng. Mostafa — this list is what the frontend implies, not authoritative.

**Customer Master**
- `is_dealer` flag (boolean) — drives the `MockUser.isDealer` field and the `/dealer/*` route gate.
- `rewards_balance` (int, points)
- `plan_code` (`SILVER|GOLD|DIAMOND|DEALER`)
- `plan_status` (`Active|Inactive|Pending|Cancelled`)
- `billing_period` (`monthly|annual`)
- `renewal_date` (date)
- `credits_remaining` (currency, EGP)
- `display_name` / `display_name_ar` separated (currently `name` vs `nameEn`)
- `username` (URL-safe slug for registry leaderboards / public set ownership)

**Coin Master (Reference Master)**
- `description` (compact identifier — Year + Hijri + Country + Denomination + Series)
- `description_ar` (same, Arabic)
- `mintmark` (e.g. "Cairo Mint", "C")
- `notes` (free-form curator notes — flagged in `lib/api/verify.ts` TODOs)
- `signals` block exposed for the Price Guide: `trendingScore`, `isTopPopTarget`, `registryActiveSetCount`
- `pricing.byGrade` block: median/low/high per grade with `lastUpdated`
- Cross-link surface for `/population/reference/{ref_code}` and `/price-guide/{ref_code}`

**Certificate / Grading Result**
- `result_type` (`Encapsulated|Details|Not Encapsulated|Rejected`)
- `population_context` precomputed against `final_grade` (or computed at read time joining the Population endpoint)
- `nfc_signature` payload + verification key for `/verify/nfc`

**Submission Doctype**
- `tracking_id` (`TRK-XXXXXX`) generated server-side
- `submission_source` (`Customer|Dealer|Walk-in|Partner|Migration`)
- `dealer_reference_no`, `submitted_on_behalf_of` for dealer-filed submissions
- `payment_method`, `payment_method_note`
- `promo_code_applied`
- Lifecycle timestamps: `received_on`, `grading_complete_on`, `completed_on`

**Promo Codes / Coupons doctype** *(new)*
- Fields per `PromoCode` type — `code`, `type`, `value`, `description`, `description_ar`, `expires_at`, `active`
- Per-customer usage limits (not yet modeled in frontend; backend's call)

**Registry Set Master**
- v2 fields: `theme_tags[]`, `cover_image`, `narrative` / `narrative_ar`, `scoring_rules`
- Custom-set support: `type` (master|custom), `owner` (customer_id)
- Slot definitions with `required_reference`, `weight`, optional `required_grade`

**Registry Activity Log** *(new)*
- Stores `ActivityEvent` records keyed by actor + timestamp; feeds the public activity stream.

**Registry Watchlist** *(new)*
- Junction table: customer_id × set_id with timestamp.

**Achievements catalog** *(new — content team)*
- Code list shown in `MemberSetSummary.achievements`. Frontend has the badge UI; backend owns the rules engine.

**News / Articles doctype**
- Title + excerpt + body + category — each with `_ar` variant.

**Service Master, Service Options, Add-Ons, Postage Matrix** *(new — admin-editable)*
- Today the catalog is static in `lib/data/services.ts`. Move into ERP so IGA staff can edit prices without a code release.

**Invoices** *(existing in ERP — confirm field exposure)*
- Need `type` to surface `Proforma Invoice | Sales Invoice | Membership Sales Invoice` in the wire format.
- `down_payment_applied`, `credits_applied`, `balance_due` exposed.

---

## 4. Outstanding TODO(api) markers

Grouped by domain. Each entry is `file:line — what it asks for`.

### Verify
- `lib/api/verify.ts:26` — confirm verify response returns `ref_code` so the result page can cross-link to `/population` and `/price-guide`.
- `lib/api/verify.ts:33` — return `mintmark` from coin catalog Master Data.
- `lib/api/verify.ts:47` — return `description` (compact coin identifier) + `description_ar`.
- `lib/api/verify.ts:54` — `population_context` aggregated server-side from `/api/v1/population/{ref_code}` and bucketed against `final_grade`.
- `lib/mocks/verify.ts:33,40` — same as above (markers in the mock).
- `lib/data/glossary.ts:9` — GET `/api/v1/glossary` when the ERP endpoint ships.

### User / Auth
- `lib/api/user.ts:6` — confirm `GET /api/v1/membership/me` endpoint with Eng. Mostafa.
- `lib/mocks/user.ts:29` — replace with server session lookup once auth ships.
- `components/features/auth/AuthForm.tsx:88,162` — real auth login + register endpoints (not yet specified anywhere).
- `components/features/auth/AuthForm.tsx:112` — forgot-password flow + dedicated route.
- `app/[locale]/(public)/forgot-password/page.tsx:23` — wire password-reset flow.

### Submissions
- `lib/api/submissions.ts:140` — `GET /api/v1/submissions/{submissionNo}/activity` confirmation.
- `app/[locale]/(auth)/dashboard/submissions/[id]/page.tsx:120` — `POST /api/v1/submissions/{id}/cancel` confirmation.
- `components/features/submit/types.ts:48` — wire submitter identity to real session.
- `components/features/submit/useSubmitWizard.ts:287` — apply membership grading credits (currently hard-coded `uses_credit: false`).

### Membership / Rewards
- `lib/api/membership.ts:89`, `lib/mocks/membership.ts:70` — `GET /api/v1/membership/rewards/ledger`.
- `app/[locale]/(auth)/dashboard/membership/page.tsx:134` — `POST /api/v1/membership/subscription/auto-renew`.
- `app/[locale]/(auth)/dashboard/membership/page.tsx:150` — `POST /api/v1/membership/subscribe` for renewal.
- `app/[locale]/(auth)/dashboard/membership/page.tsx:164` — `POST /api/v1/membership/subscription/cancel`.
- `components/dashboard/RewardsRedemptionForm.tsx:48-49` — `POST /api/v1/membership/rewards/redeem`.
- `components/dashboard/ProfileForm.tsx:22` — `PATCH /api/v1/membership/me` (profile update).
- `components/dashboard/ProfileForm.tsx:70` — avatar upload endpoint.
- `components/dashboard/ProfileSettings.tsx:44` — `POST /api/v1/membership/me/password`.
- `components/dashboard/ProfileSettings.tsx:50` — `PATCH /api/v1/membership/me/notifications`.
- `components/dashboard/ProfileSettings.tsx:59` — `DELETE /api/v1/membership/me` (account deletion).

### Registry (v2)
- `lib/api/registry.ts:186,196,202` — `/registry/sets` family with `category` + `type` filters.
- `lib/api/registry.ts:208,216` — `GET /registry/my-sets`, `POST /registry/my-sets` (type=custom).
- `lib/api/registry.ts:256,265,274` — `PUT /registry/my-sets/{setId}/{cover|narrative|visibility}`.
- `lib/api/registry.ts:280` — `GET /registry/stats`.
- `lib/api/registry.ts:289` — `GET /registry/activity`.
- `lib/api/registry.ts:300` — `GET /registry/my-achievements`.
- `lib/api/registry.ts:311` — `GET /registry/leaderboard/collectors`.
- `lib/api/registry.ts:335` — `GET /registry/awards`.
- `lib/api/registry.ts:344,357,362` — `POST/GET /registry/sets/{setId}/comments`.
- `lib/api/registry.ts:368` — `GET /registry/top-pop/{ref}`.
- `lib/api/registry.ts:374,383,392` — watchlist CRUD.
- `lib/api/registry.ts:401` — `GET /registry/compare`.
- `lib/mocks/registry.ts:239` — server-side filtering by slot requirement in `/customer/certificates`.
- `lib/mocks/registry-v2.ts:3` — every reader maps to a real endpoint.
- `app/[locale]/(auth)/dashboard/registry/[setId]/page.tsx:26,39,44` — `GET /registry/my-sets/{setId}`, `GET /registry/leaderboard/{setCode}`, `GET /customer/certificates`.
- `app/[locale]/(auth)/dashboard/registry/page.tsx:34` — authenticated `/registry/my-sets` etc.
- `app/[locale]/(public)/registry/page.tsx:181` — swap to WebSocket subscription for live updates.
- `components/dashboard/RegistryTabs.tsx:49` — `POST /api/v1/registry/my-sets`.
- `components/features/registry/CustomSetWizard.tsx:131` — `POST /api/v1/registry/my-sets` (type=custom).
- `components/features/registry/CommentsSection.tsx:47` — `POST /api/v1/registry/sets/{setId}/comments`.
- `components/features/registry/SlotsGrid.tsx:24`, `components/features/registry/SlotFillDialog.tsx:34` — `PUT /api/v1/registry/my-sets/{memberSetNo}/slots`.
- `components/features/registry/WatchButton.tsx:27` — watchlist toggle.
- `components/features/registry/SetOwnerActions.tsx:18` — real auth check stub.
- `components/features/registry/LeaderboardFilters.tsx:28` — server-side leaderboard filtering.
- `components/features/verify/AddToRegistryDialog.tsx:19,46` — `GET /api/v1/registry/my-sets` and `POST /api/v1/registry/my-sets/{selectedSet}/items`. *Note: the `items` add path is the only place this is referenced; confirm with Eng. Mostafa.*

### Support
- `lib/api/support.ts:53` — prefill `guest_*` from session when auth lands.
- `lib/api/support.ts:67,87` — `POST /api/v1/support/tickets` confirmation.
- `components/dashboard/TicketsList.tsx:74` — `POST /api/v1/support/tickets`.
- `components/dashboard/TicketConversation.tsx:55,67` — `POST /api/v1/support/tickets/{ticketNo}/messages` + file upload integration.
- `components/dashboard/TicketReplyForm.tsx:19` — same endpoint.
- `app/[locale]/(auth)/dashboard/support/[ticketId]/page.tsx:36` — `GET /api/v1/support/tickets/{ticketId}`.
- `app/[locale]/(auth)/dashboard/support/page.tsx:16` — `GET /api/v1/support/tickets`.
- `app/[locale]/(public)/contact/actions.ts:18` — same as `createSupportTicket` once wired.

### Population
- `lib/api/population.ts:62,70` — both routes pending confirmation.
- `app/[locale]/(public)/population/page.tsx:66` — `GET /api/v1/population/search`.
- `app/[locale]/(public)/price-guide/[refCode]/page.tsx:54` — `GET /api/v1/population/reference/{refCode}` for cross-link.
- `lib/mocks/population.ts:11` — real population computed dynamically server-side, no manual updates.

### Price Guide
- `lib/api/price-guide.ts:131,153,164,180` — list + trending + top-pop + registry-stars endpoints all pending Eng. Mostafa confirmation.

### Invoices
- `lib/api/invoices.ts:6` — both routes pending confirmation.
- `lib/mocks/invoices.ts:31,173` — same.

### Dealer
- `lib/api/dealer.ts:6` — all three endpoints pending confirmation.
- `components/dashboard/DealerSubmissionsList.tsx:156` — CSV export endpoint (`GET /api/v1/dealer/submissions.csv` would be the natural choice).

### Services
- `lib/api/services.ts:17,23,29,35` — all four catalog routes pending wiring.
- `lib/data/services.ts:8` — same (note in source data).
- `app/[locale]/(public)/services/page.tsx:57` — all four calls will hit ERPNext Service Master once wired.

### Promo
- `lib/api/promo.ts:6` — `POST /api/v1/promo/validate` confirmation.
- `lib/data/promo-codes.ts:8` — `GET /api/v1/promo/{code}` returns same shape (alternative read-only path).

### News
- (no explicit `TODO(api)` markers — the service file simply needs to be backed by ERP when content lands.)

---

## 5. Test fixtures / mock cert + submission numbers

QA can use the same identifiers the frontend uses today.

### Verify — cert number suffix → response

| Cert number | Status | Result Type / Error | Notes |
|---|---|---|---|
| `AA00001-01` | 200 | Encapsulated (`MS 65`, top grade) | links to `ref_code = EGY-1968-1POUND-ASWAN`; `population_context.is_top_grade = true` |
| `AA00001-02` | 200 | Details (`Details — Cleaned`) | second mock; `ref_code = EGY-1916-20PIASTRES-HUSSEIN` |
| `AA00001-03` | 404 | Not Found | UI shows "Certificate not found" |
| `AA00001-04` | 410 | Gone (cert withdrawn) | UI shows "Certificate not available — item was rejected" |
| `AA00001-05` | 425 | Too Early | UI shows "Verification not yet available — submission still in progress" |
| `AA00001-06` | 429 | Rate Limited | UI shows "Too many requests" |
| `AA00001-07` | 200 | Rejected (`Not Genuine`) | distinct from 410 — this is a logged, persistent rejection |
| any other | 200 | Encapsulated (fallback) | returns the standard mock with the requested cert number |

### Verify — NFC

`POST /verify/nfc` with any non-empty payload returns the Encapsulated mock + `nfc_signature_valid: true`.

### Tracking — tracking ID → response

| Tracking ID | Status | State |
|---|---|---|
| `TRK-001` (or anything not below) | 200 | Grading (items_breakdown: Received 1, Grading 2; ETA 2026-05-22) |
| `TRK-002…` (any prefix) | 200 | Completed (5 items, no ETA) |
| `TRK-003…` (any prefix) | 200 | On Hold (2 items, no ETA) |
| `TRK-404` | 404 | Not Found |
| `TRK-429` | 429 | Rate Limited |

### Submissions

| Submission | Status | Tier | Category | Items |
|---|---|---|---|---|
| `AA00001` | Grading | Standard | Modern | 3 |
| `AA00002` | Completed | Express | Early Modern | 5 (mix of Encapsulated, Details, Not Encapsulated) |
| `AA00003` | On Hold | Standard | Medals & Tokens | 2 |
| `AA00004` | Imaging | Priority | High Value | 5 (all Encapsulated, ranging up to EGP 120k declared) |
| `AA00005` | QC | Express | Modern | 1 |
| `AA00006` | Slabbing | Standard | Early Modern | 4 |
| `AA00007` | Completed | Value | Modern | 7 |
| `AA00008` | Created / Ready for Pickup | Standard | Medieval / Modern | (duplicate IDs intentional — testing edge case) |
| `AA00009` | Received | Express | Medals & Tokens | 6 |
| `AA00010` | Shipped | Standard | Modern | 3 |

New submissions created via the wizard get sequential IDs starting at `AA00011`.

### Invoices

| Invoice | Type | Submission | Status |
|---|---|---|---|
| `PI-00001` | Proforma Invoice | `AA00001` | Paid |
| `SI-00001` | Sales Invoice | `AA00001` | Paid |
| `PI-00002` | Proforma Invoice | `AA00002` | Paid |
| `SI-00002` | Sales Invoice | `AA00002` | Paid |
| `PI-00003` | Proforma Invoice | `AA00003` | Under Review |
| `PI-00004` | Proforma Invoice | `AA00004` | Pending |
| `PI-00005` | Proforma Invoice | `AA00005` | Cancelled |
| `MSI-00001` | Membership Sales Invoice | (null) | Paid |

### Tickets

| Ticket | Type | Status | Related |
|---|---|---|---|
| `TKT-00001` | General | Resolved | submission `AA00001` |
| `TKT-00002` | Offer | Open | cert `AA00001-01` |
| `TKT-00003` | Guarantee Claim | In Progress | cert `AA00002-01` |
| `TKT-00004` | Report Certificate | Awaiting Customer | cert `AA00003-02` |
| `TKT-00005` | General | Resolved | — |
| `TKT-00006` | General | Open | — |
| `TKT-00007` | Offer | Closed | cert `AA00002-04` |

### Promo codes

| Code | Type | Value | Notes |
|---|---|---|---|
| `WELCOME10` | percent | 10 | active, no expiry |
| `SAVE500` | fixed | 500 EGP | active, no expiry |
| `AWARDS2026` | percent | 15 | active, expires `2026-06-30` |

Any code not in the list → `{ valid: false, reason: "not_found" }`.

### Mock current user

```
id: USR-001
name (ar): عمر وائل
nameEn:    Omar Wael
email:     omaarwael@gmail.com
plan:      GOLD (Active, annual, renews 2027-05-15)
isDealer:  false
joinedAt:  2025-08-15
rewardsBalance: 1250 points
```

### Coin reference (for verify cross-links)

`EGY-1968-1POUND-ASWAN` — the encapsulated fixture's `ref_code`; used to exercise verify → population → price-guide cross-linking.

---

## 6. Submission lifecycle reference

```
                    ┌────────────┐
                    │  Created   │  ← submission_no, tracking_id, proforma_invoice_no
                    └─────┬──────┘     (set by POST /submissions)
                          │
                          ▼
                    ┌────────────┐
                    │  Received  │  ← received_on (set when items physically arrive)
                    └─────┬──────┘
                          │
                          ▼
                    ┌────────────┐
                    │  Grading   │  ← per-item current_stage starts populating
                    └─────┬──────┘
                          │
                          ▼
                    ┌────────────┐
                    │  Slabbing  │
                    └─────┬──────┘
                          │
                          ▼
                    ┌────────────┐
                    │     QC     │
                    └─────┬──────┘
                          │
                          ▼
                    ┌────────────┐
                    │  Imaging   │  ← per-item result_type populated
                    └─────┬──────┘     ("Encapsulated", "Details", "Not Encapsulated",
                          │              "Rejected") → cert becomes verifiable
                          ▼
                          ├──────────────────────────────┐
                          ▼                              ▼
                    ┌────────────┐                ┌──────────────────┐
                    │  Shipped   │       OR       │ Ready for Pickup │
                    └─────┬──────┘                └─────────┬────────┘
                          │                                 │
                          └────────────┬────────────────────┘
                                       ▼
                                ┌────────────┐
                                │ Completed  │  ← grading_complete_on, completed_on,
                                └────────────┘     sales_invoice_no all populated

                                ┌────────────┐
                                │  On Hold   │  ← branched from any stage when
                                └────────────┘     additional docs / clarification needed.
                                                   Returns to the prior stage on resume.
```

**Field population by stage transition:**

| Transition | Fields set |
|---|---|
| → `Created` | `submission_no`, `tracking_id`, `proforma_invoice_no`, item `certificate_number` (per item) |
| → `Received` | `received_on`, per-item `current_stage: "Received"` |
| → `Grading` | per-item `current_stage: "Grading"` |
| → `Slabbing` | per-item `current_stage: "Slabbing"` |
| → `QC` | per-item `current_stage: "QC"` |
| → `Imaging` | per-item `current_stage: "Imaging"`, **per-item `result_type` populated** (cert verifiable from here) |
| → `Shipped` | per-item `current_stage: "Shipped"` |
| → `Ready for Pickup` | per-item `current_stage: "Ready for Pickup"` |
| → `Completed` | `grading_complete_on`, `completed_on`, `sales_invoice_no` |
| → `On Hold` | rollup status flips; per-item stage unchanged. Original stage restored on resume. |

The rollup `customer_visible_status` is the "highest reached" stage across all items (e.g. if 4 items are at `Imaging` and 1 is at `Slabbing`, the submission's status is `Slabbing` — the lagging item). `On Hold` overrides everything while active.

---

## 7. Open questions for the backend lead

These are points where the frontend has assumed a behavior that needs the backend lead's confirmation before lock-in.

1. **Verify ↔ Population join.** Does `/verify/{cert_no}` return the `population_context` inline (joined server-side against the cert's `final_grade`), or should the frontend make a second call to `/population/reference/{ref_code}` and bucket client-side? The current frontend reads `result.population_context` directly (`lib/api/verify.ts:24-58`), which assumes server-side join.

2. **`ref_code` on verify responses.** The frontend wants `ref_code` on every Verify result so it can cross-link into `/population` and `/price-guide`. Confirm the ERP can resolve this for older certs that pre-date the catalog migration.

3. **`description` / `description_ar` source of truth.** Are these per-cert (stored on the Grading Result) or per-reference (stored on the Coin Master and joined)? Frontend implies the latter.

4. **Bulk discount calculation — server or client?** Today the wizard precomputes the discount with the mock quote endpoint and shows the breakdown to the user. The server must re-compute on `POST /submissions` and reject if the client's `is_bulk: true` doesn't match the actual item count.

5. **VAT — already applied or added at submit time?** The quote endpoint returns `vat` and `total` separately; the submission endpoint expects to charge the `total`. Confirm the proforma invoice line items include VAT as a separate line.

6. **Promo code stacking.** Can a promo code stack on top of the bulk discount and the plan's grading discount? Frontend assumes yes (multiplicative or additive — TBD). Lock the precedence rule.

7. **Membership grading credits.** `uses_credit` is hard-coded `false` in the wizard (`components/features/submit/useSubmitWizard.ts:287`). When credits are wired, does the user select "use credit" in the UI, or is it automatic until the credit balance is exhausted?

8. **Auth mechanism.** Pick one (HttpOnly cookie session vs Bearer JWT). The frontend will need a single decision so `lib/api/client.ts` can either rely on `credentials: "include"` or attach an `Authorization` header.

9. **Forgot-password flow.** Stub at `app/[locale]/(public)/forgot-password/page.tsx:23`. Confirm: request reset link → token verification → set new password. Endpoint paths TBD.

10. **NFC payload format.** `POST /verify/nfc { payload: string }` — the frontend sends an opaque string. Confirm the encoding (base64? hex? raw URL?) and the signature scheme so the gateway can validate before hitting ERP.

11. **Registry v2 set IDs.** The v1 path used `member_set_no` (e.g. `MS-00001`); v2 uses just `id` (e.g. `MS-29384`). Decide whether the same identifier serves both API surfaces or whether v2 needs a separate ID space.

12. **Public registry leaderboards.** Master Brief §9 lists `Phase 2: Public Registry leaderboard marketing surface`. Frontend v2 has `getTopCollectors()` returning public data. Confirm whether the gateway should ship this in Phase 1.

13. **Watchlist remove method.** Frontend currently calls `PUT /api/v1/registry/watchlist/{setId}/remove` (`lib/api/registry.ts:393`). Should be `DELETE /api/v1/registry/watchlist/{setId}` per REST norms. Confirm so the frontend can switch.

14. **Custom set comments — moderation.** `POST /registry/sets/{setId}/comments` accepts any body. Will the gateway moderate (queue → publish) or auto-publish? Frontend renders comments immediately.

15. **Add-to-registry from Verify.** `components/features/verify/AddToRegistryDialog.tsx:46` calls `POST /api/v1/registry/my-sets/{selectedSet}/items` — this is the only reference to that endpoint anywhere. Confirm path + body shape.

16. **Invoice PDF generation.** `pdf_url` is `null` in mocks. Is the PDF generated synchronously on invoice creation, or do we poll? Frontend treats `null` as "not yet available".

17. **Activity log internationalization.** `ActivityEntry` ships both `description` (EN) and `descriptionAr` (AR) pre-resolved. Other endpoints use the `Accept-Language` header or `_ar` paired fields. Decide whether to standardize.

18. **Dealer CSV export.** `components/dashboard/DealerSubmissionsList.tsx:156` has a stub for CSV export. Confirm whether the gateway provides a `.csv` content-type variant or whether the frontend should generate it client-side from the JSON response.

19. **Currency.** Are all monetary fields returned as integer EGP (e.g. `2805` = 2,805.00 EGP), or as decimal? Mocks use whole numbers throughout. Confirm precision.

20. **Date timezones.** Pure-date fields are stored as `YYYY-MM-DD` (Egypt local). Timestamps use ISO `Z` (UTC). Confirm the gateway will normalize to this split.

---

*End of contract document. Backend lead — please raise the open questions in §7 with Eng. Mostafa, and reply with the locked specs so the frontend can flip `NEXT_PUBLIC_USE_MOCKS=false`.*
