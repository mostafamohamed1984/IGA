# Backend Adjustments Required for Frontend Integration

> **For:** Eng. Mostafa
> **From:** Frontend integration
> **Date:** 2026-05-20
>
> **Companion docs:**
> - `docs/backend-api-contract.md` — full TypeScript-level contract the frontend expects (~1,755 lines, 15 domains)
> - `docs/backend-vs-frontend-comparison.md` — line-by-line gap analysis between your Master Brief + Workbook and the contract above
>
> **Source files cited throughout:**
> - `IGA_Developer_Master_Brief (3).docx` (sections §1–§14)
> - `IGA_Developer_Master_Workbook (4).xlsx` (sheets 03–44)
> - `lib/api/*.ts` — the frontend's wire types

---

## TL;DR

Your spec covers **~80% of what the frontend needs verbatim**. The remaining work breaks into three buckets:

1. **One blocker** (§1) — the per-item state vocabulary. Must agree before gateway starts.
2. **~20 new endpoints / fields** (§2–§4) — additive. Won't break what you've already designed.
3. **~15 small decisions** (§5) — naming, defaults, scope of Registry v2. A 90-minute call resolves all of them.

**No part of your spec needs to be torn down.** Everything below is *add*, not *rework*. Integration estimate: **2–3 sprints** end-to-end if Registry v2 is post-launch; 3–4 if v2 ships at launch.

---

## 1. The one blocker — `SubmissionItem.current_stage`

| Your spec | Frontend expects |
|---|---|
| Per-item `item_status` (internal, e.g. `Ready for Grading`, `In Grading`, `QC Passed`, etc.) computed into a 6-bucket `customer_status` (`Under Review / In Progress / Finalizing / Action Required / On Hold / Cancelled`). `sheet_04` rows 22–24, `sheet_07` row 33. | The same 10-value `SubmissionStage` union used at submission level: `Created · Received · Grading · Slabbing · QC · Imaging · Shipped · Ready for Pickup · Completed · On Hold` — surfaced per item so each row in the dashboard timeline shows where THIS coin is right now (`lib/api/submissions.ts:42`). |

**Decision needed:** does each item report its *own rollup* of the submission's 10 stages, OR does the frontend switch to your 6-bucket `customer_status` vocabulary?

**Recommendation (frontend side):** keep the 10-stage names per item. The mock fixtures already render them per item (e.g. one item at "Imaging" while another is "Slabbing"), and the dashboard timeline is built around them. The gateway can compute a per-item rollup from `item_status` using the same mapping you've already drafted in `sheet_07` row 33 — just expose it as `current_stage` instead of `customer_status`.

> If you'd rather keep `customer_status` as-is, we re-shape the frontend timeline. Either choice works; needs to be decided before either side wires real data.

---

## 2. New endpoints to add (additive — your spec is silent on these)

All paths follow the existing `/api/v1/...` prefix. Auth columns: 🌐 public · 👤 member · 💼 dealer · 🛡️ admin.

### 2.1 Promo / Coupon (new domain)

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `POST` | `/api/v1/promo/validate` | 🌐 | Validates a customer-entered promo code against a Coupon DocType. Returns the code + discount type + value, or an error reason (`not_found / expired / inactive`). |

**Wire types (frontend `lib/api/promo.ts`):**
```ts
Request:  { code: string }
Response (success): { valid: true, code: { code, type: 'percent'|'fixed', value, description, expiresAt, active } }
Response (failure): { valid: false, reason: 'not_found' | 'expired' | 'inactive' }
```

Frontend uses three mock codes for QA: `WELCOME10` (10% off), `SAVE500` (500 EGP off), `AWARDS2026` (15% off, expires 2026-06-30). See `lib/data/promo-codes.ts`.

The submission payload also carries `promo_code: string` (optional) so the gateway can re-validate server-side and apply the discount on the Proforma Invoice. **The frontend's `promo_code` value is untrusted** — always re-validate and recompute on the server.

### 2.2 Submission activity log

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/api/v1/submissions/{submission_no}/activity` | 👤 | Returns the customer-visible timeline events for a submission (intake, grading complete, sales invoice issued, shipped, etc.). |

**Response:**
```ts
Array<{ id, date (ISO with Z), description (EN), descriptionAr (AR) }>
```

Two locale strings are pre-resolved by the gateway — the frontend won't run translations on these.

### 2.3 Current user (session) endpoints

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/api/v1/membership/me` | 👤 | Returns the active session user. Powers the dashboard sidebar, avatar dropdown, and profile page. |
| `PATCH` | `/api/v1/membership/me` | 👤 | Updates profile fields (name, phone, language preference). |
| `POST` | `/api/v1/membership/me/password` | 👤 | Changes password. |
| `PATCH` | `/api/v1/membership/me/notifications` | 👤 | Updates notification preferences. |
| `DELETE` | `/api/v1/membership/me` | 👤 | Account deletion request. |
| (TBD) | Forgot-password flow | 🌐 | Email reset link → token-based password change. |

**`/membership/me` response shape:**
```ts
{
  id, name, nameAr, email, avatarUrl: string | null,
  plan: 'SILVER' | 'GOLD' | 'DIAMOND' | 'DEALER',
  planStatus: 'Active' | 'Inactive' | 'Pending' | 'Expired' | 'Grace' | 'Cancelled',
  isDealer: boolean,
  joinedAt: ISO date,
  rewardsBalance: number
}
```

Note: `isDealer` is derived (`plan === 'DEALER' || customer.is_dealer`). The frontend uses it to gate the Dealer dashboard tab.

### 2.4 Rewards ledger

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/api/v1/membership/rewards/ledger` | 👤 | Full transaction history (earn / redeem / expire / adjust). |

Already implied in your `sheet_23 — Rewards Ledger` doctype; just needs a read endpoint. Response = `RewardsLedgerEntry[]`.

### 2.5 Invoices (read API)

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/api/v1/invoices` | 👤 | List all invoices for the session user. |
| `GET` | `/api/v1/invoices/{invoice_no}` | 👤 | Single invoice. |

**Response shape requires:** `invoice_no`, `type` (Proforma / Sales / Membership Sales), `submission_no` (nullable), `date`, `subtotal`, `vat`, `total`, `status`, `down_payment_applied`, `credits_applied`, `balance_due`, `pdf_url`, `line_items: Array<{ description, qty, unit_price, total }>`.

**Customize ERPNext Sales Invoice status options to:** `Pending | Under Review | Paid | Cancelled`. The native Frappe set is different.

### 2.6 Dealer dashboard (DEALER plan only)

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/api/v1/dealer/submissions` | 💼 | List submissions made on behalf of collectors. |
| `GET` | `/api/v1/dealer/stats` | 💼 | `{ total_submissions, active_in_flight, completed_this_month, total_items_graded }`. |
| `GET` | `/api/v1/dealer/top-collectors` | 💼 | Per-dealer top collector list (`collector_name, submissions, total_items`). |

### 2.7 Services catalog (read API)

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/api/v1/services/grading` | 🌐 | All grading services from Service Master (`sheet_40`). |
| `GET` | `/api/v1/services/options` | 🌐 | Service options (Re-Grade, Cross-Over, Re-Slab, Bulk, Restoration). |
| `GET` | `/api/v1/services/add-ons` | 🌐 | Add-on services with prices. |
| `GET` | `/api/v1/services/postage` | 🌐 | Postage matrix (per piece-count × declared value). |

The wizard (`/submit`) reads these to render live pricing. Today they're served from `lib/data/services.ts` in-repo. Postage Matrix is new — it's not in `sheet_03` and needs a small DocType.

### 2.8 Price Guide

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/api/v1/price-guide` | 🌐 | Paginated list. Filter by `country`, `category`, `designation`, `has_pricing`, `shortcut` (top_pop / registry_star / with_pricing), `query`, `sort` (newest / price_high / price_low / trending). |
| `GET` | `/api/v1/price-guide/{ref_code}` | 🌐 | Single coin reference with full pricing block. |
| `GET` | `/api/v1/price-guide/trending` | 🌐 | Trending coins. |
| `GET` | `/api/v1/price-guide/top-pop` | 🌐 | Top-pop highlights. |
| `GET` | `/api/v1/price-guide/registry-stars` | 🌐 | Coins frequently in active sets. |

Requires `pricing.byGrade` and `signals` blocks on **Item Reference Catalog** (`sheet_34`) — currently in `lib/data/coin-catalog.ts` in-repo. Pricing object is keyed by grade label (`MS65`, `XF40`, etc.) with `{ low, median, high }` per grade.

### 2.9 News / Articles

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/api/v1/news` | 🌐 | Latest articles list. |
| `GET` | `/api/v1/news/{slug}` | 🌐 | Single article. |

**New DocType needed** — not in `sheet_03`. Fields: `slug`, `title`, `title_ar`, `excerpt`, `excerpt_ar`, `body`, `body_ar`, `category`, `category_ar`, `date`, `cover_image`.

### 2.10 Public catalog search (new — once catalog grows past 100 entries)

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/api/v1/catalog/coins?q={text}&limit=20` | 🌐 | Fuzzy search across Item Reference Catalog for the wizard's coin picker. |
| `GET` | `/api/v1/catalog/coins/{ref_code}` | 🌐 | Single coin record. |

The wizard's `CatalogSearchInput` currently bundles 75 entries client-side. Once the catalog exceeds 100–200, fetching client-side stops being viable.

### 2.11 Registry — slot fulfillment helper

| Method | Path | Auth | Purpose |
|---|---|---|---|
| `GET` | `/api/v1/customer/certificates?slot={slot_description}` | 👤 | Returns the session user's owned certificates that are eligible to fill a given registry slot. |

Used by the slot-fill dialog in `/dashboard/registry/{setId}`. Filter is server-side (matches `slot_description` against ref_code / category).

### 2.12 Registry v2 (large block — needed only if v2 ships at launch; otherwise post-launch)

If you accept Registry v2 as additive to brief §9.8, the following endpoints are needed. See `lib/api/registry.ts` for the full type definitions.

| Method | Path | Purpose |
|---|---|---|
| `GET` | `/api/v1/registry/sets` | List all sets (filter by category / type=master\|custom). |
| `GET` | `/api/v1/registry/sets/{id}` | Single set with slots, narrative, achievements. |
| `GET` | `/api/v1/registry/my-sets` | Current user's sets. |
| `POST` | `/api/v1/registry/my-sets` | Create a custom set. |
| `PUT` | `/api/v1/registry/my-sets/{id}/cover` | Update cover image. |
| `PUT` | `/api/v1/registry/my-sets/{id}/narrative` | Update narrative text. |
| `PUT` | `/api/v1/registry/my-sets/{id}/visibility` | `private / public / showcase`. |
| `GET` | `/api/v1/registry/stats` | Site-wide live stats (collectors, sets, coins, awards). |
| `GET` | `/api/v1/registry/activity` | Activity feed (`scope=global / following / set`, `scope_id`). |
| `GET` | `/api/v1/registry/leaderboard/collectors` | Top collectors (period / category / country / page). |
| `GET` | `/api/v1/registry/my-achievements` | Earned achievements + progress. |
| `GET` | `/api/v1/registry/awards?year={n}` | Awards categories + past winners + calendar. |
| `GET` | `/api/v1/registry/sets/{id}/comments` | Comments on a set. |
| `POST` | `/api/v1/registry/sets/{id}/comments` | Post a comment. |
| `GET` | `/api/v1/registry/top-pop/{ref_code}` | Top-pop entries per reference. |
| `GET` | `/api/v1/registry/watchlist` | User's watched sets. |
| `POST` | `/api/v1/registry/watchlist/{set_id}` | Add to watchlist. |
| `DELETE` | `/api/v1/registry/watchlist/{set_id}` | Remove. |
| `GET` | `/api/v1/registry/compare?a={id}&b={id}` | Side-by-side comparison. |

**New DocTypes for v2:** Registry Activity Log, Registry Watchlist, Set Comment, Award Winner, Achievement Catalog, Achievement Progress.

---

## 3. Adjustments to existing endpoint shapes

### 3.1 `GET /api/v1/verify/{cert_no}` — add these response fields

Current spec (brief §9.3, `sheet_16` row 6): `certificate_number, result_type, label_country_denom, label_year_line, label_series_line, final_grade, designations[], holder_type, images, graded_on, nfc_signature_valid`.

**Add:**
- `ref_code` — links to Item Reference Catalog so the frontend can cross-link to `/price-guide/{ref_code}`. Source: Submission Item → Item Reference.
- `mintmark` — short code (e.g. `H`, `BP`, `C`). Source: Coin Master.
- `description` + `description_ar` — compact coin identifier (e.g. *"1968 (AH 1387) Egypt 1 Pound — Aswan Dam Commemorative"*). Source: Coin Master.
- `population_context` — denormalized snapshot computed against `final_grade`:
  ```ts
  { at_grade: number, higher: number, lower: number, is_top_grade: boolean }
  ```
  where `is_top_grade ⇔ higher === 0`. Source: aggregate from Submission Items by `ref_code`. Returning this avoids a separate population fetch on the verify page.

All four are joinable from existing data — no new DocType needed.

### 3.2 `POST /api/v1/submissions/quote` — adopt richer breakdown

Current spec (`sheet_16` row 18): `{ subtotal, discount_pct, vat_amount, grand_total }`.

**Replace with:**
```ts
{
  base_subtotal: number,            // tier price × billable item count
  addons_subtotal: number,          // sum of add-ons across items
  subtotal_before_discount: number, // base + addons
  bulk_discount: number,            // = subtotal_before_discount × 10% when is_bulk && count >= 5
  subtotal: number,                 // subtotal_before_discount - bulk_discount (pre-VAT)
  vat: number,                      // 14%
  total: number,                    // subtotal + vat
  currency: 'EGP'
}
```

Reason: the submit wizard's sticky pricing sidebar renders each of these as separate lines. Collapsing them into a single `subtotal` loses the visual breakdown customers see.

### 3.3 `POST /api/v1/verify/nfc` — confirm signature handling

Brief §9.3 says body is `{ payload, signature }`. Frontend currently sends only `{ payload: string }`.

**Decision required:** either gateway extracts the signature from inside the payload, or the frontend needs to send it separately. Also confirm:
- Wire encoding (base64 / hex / raw URL)
- Signature scheme (HMAC-SHA256? ECDSA? Which key?)

### 3.4 `GET /api/v1/population/search` — add filter params

Add to the query params:
- `mint` — filter by Coin Master `mintmark`
- `variety` — filter by `is_variety` flag

And in results, expose:
- `country_name_en` — display name (Country Master)
- `country_name_ar` — Arabic display name
- `country_flag` — flag asset URL or ISO code for client-side flag rendering

### 3.5 Registry `DELETE` semantics

Switch watchlist removal from `PUT /watchlist/{setId}/remove` to `DELETE /api/v1/registry/watchlist/{setId}`. Standard REST verb.

---

## 4. New DocTypes / field additions

### 4.1 New DocType — **Coupon / Promo Code**

```
DocType: IGA Promo Code
Naming: code (e.g. WELCOME10)

Fields:
- code              (Data, unique, primary, uppercase)
- type              (Select: percent | fixed)
- value             (Float — % for percent, EGP amount for fixed)
- description       (Data — short label shown when applied)
- description_ar    (Data)
- expires_at        (Date, nullable)
- active            (Check)
- usage_limit       (Int, nullable — max total uses)
- usage_count       (Int, auto-incremented on each use)
- usage_per_customer (Int, nullable — max uses per customer)
- created_by        (Link → User, audit)
```

### 4.2 New DocType — **News Article**

```
DocType: IGA News Article
Naming: slug

Fields:
- slug              (Data, unique, primary)
- title             (Data, EN)
- title_ar          (Data)
- excerpt           (Small Text, EN)
- excerpt_ar        (Small Text)
- body              (Long Text / Markdown, EN)
- body_ar           (Long Text)
- category          (Link → News Category, EN-keyed)
- category_ar       (computed from Category.name_ar)
- date              (Date — publication date)
- cover_image       (Attach)
- author            (Link → User)
- published         (Check)
```

### 4.3 Additions to existing DocTypes

**Submission (`sheet_25`):**
- Add `payment_method` (Select: `CASH | BANK_TRANSFER | INSTAPAY | OTHER`)
- Add `payment_method_note` (Small Text — required only when `payment_method === 'OTHER'`)
- Add `promo_code` (Data — references Coupon, re-validated server-side)

**Submission Item (`sheet_04`):**
- Add `declared_grade` (Data, optional — customer's self-assessed grade, free text like `MS65` or `AU58`)

**Coin Master / Item Reference Catalog (`sheet_34`):**
- Add `mintmark` (Data, optional — `H`, `BP`, `C`)
- Add `description` (Long Text, EN)
- Add `description_ar` (Long Text)
- Add `pricing` block (Table — `grade`, `low`, `median`, `high`, `currency`, `confidence`, `last_updated`)
- Add `signals` block (`trending_score: int`, `registry_active_set_count: int`)

**Customer (native Frappe DocType):**
- Add `username` (Data, unique — used in URLs like `/registry/u/{username}`)
- Add `display_name` (Data — falls back to `customer_name`)
- Add `display_name_ar` (Data)
- Add `is_dealer` (Check — independent from membership plan; some manual dealers)
- Add `avatar_url` (Data — points to uploaded image)
- Add `rewards_balance` (Float — denormalized for fast reads)
- Add `plan_code`, `plan_status` (denormalized from active Subscription)

**Issue (native Frappe DocType, used for support tickets):**
- Add `type` (Select: `General | Offer | Report Certificate | Guarantee Claim`)
- Add `guest_name`, `guest_email`, `guest_phone` (Data — for unauthenticated contact form submissions)
- Customize `status` options to: `Open | In Progress | Awaiting Customer | Resolved | Closed`

**Membership Plan (`sheet_21`):**
- Confirm `max_redeem_pct` belongs per-plan (frontend assumption) vs global (your `sheet_24` row 11). If per-plan, hoist; if global, frontend drops.
- Confirm `monthly_fee` is a stored field OR compute as `annual_fee / 12` server-side and expose in API response.

**Subscription (`sheet_22`):**
- Confirm the status set. Frontend types `Active | Inactive | Pending | Cancelled`. Your spec implies five values (Active / Pending / Expired / Cancelled / Grace). If five is correct, frontend adopts.

---

## 5. Decisions needed from you (the C-list)

| # | Question | Why it matters |
|---|---|---|
| **C1** | Per-item state vocabulary — adopt 10-stage rollup (frontend recommendation) or push 6-bucket `customer_status` to UI? | Blocker. See §1. |
| **C2** | Bulk threshold — `min_items_for_bulk` on Service Master has no published default. Pick a value (recommend 5) and seed the row. | Frontend will read it from `/services/grading`. |
| **C3** | Service-option semantics — `RE-GRADE / CROSS-OVER / RE-SLAB / BULK / RESTORATION` are per-item modifiers in the wizard. Your Service Master is per-tier-per-category (`STD-MOD`, `EXP-EM`, etc.). Reconcile: are these their own enum or rows in Service Master? | Affects how `service_option` is validated and priced. |
| **C4** | Promo code stacking with bulk discount and plan grading discount — additive or multiplicative? Cap at subtotal? | Frontend currently applies promo *after* bulk + membership, capped at the pre-VAT subtotal. Confirm. |
| **C5** | Quote endpoint shape — adopt frontend's richer breakdown (§3.2) or your simpler shape? | Affects what the wizard renders. Frontend recommendation: adopt the richer one. |
| **C6** | `max_redeem_pct` scope — per-plan or global? | Determines if it lives on Plan or Settings. |
| **C7** | Subscription status set — 4-value (`Active / Inactive / Pending / Cancelled`) or 5-value (add `Expired / Grace`)? | Frontend will adopt whatever you pick. |
| **C8** | Set ID space — confirm `member_set_no` (v1, `MS-{YYYY}-{####}`) and the `id` field in v2 are the same identifier, and the gateway accepts both. | Avoids breakage when switching API versions. |
| **C9** | **Auth mechanism** — HttpOnly cookie session or Bearer JWT? | Frontend's `lib/api/client.ts` will be wired accordingly. Pick one. |
| **C10** | NFC payload — wire encoding (base64 / hex / raw) and signature scheme. | See §3.3. |
| **C11** | Locale field-suffix convention — your sheets use `name_arabic`, frontend uses `_ar`. Pick one. (Frontend recommends `_ar` — already in 20+ endpoints.) | Single rename pass on either side resolves it. |
| **C12** | Currency precision — whole integer EGP or decimal? Mocks use whole numbers; Frappe `Currency` type is float. | Affects rounding behavior everywhere. |
| **C13** | Date timezones — gateway returns Egypt-local for `YYYY-MM-DD` dates and UTC `Z` for timestamps? | Frontend assumes this; confirm. |
| **C14** | **Registry v2 — Phase 1 or Phase 2?** If at launch, §2.12 is in scope and the v2 DocTypes are needed. If post-launch, frontend keeps mocks and we add the endpoints later. | Big scope decision. |
| **C15** | `internal_review_status` (Pending Review / Approved / Returned / Cancelled, `sheet_25` row 19) — should the customer see "Pending Approval" before "Received", or stay at "Created"? | Brief §11 implies invisible to customer; frontend doesn't model it. Confirm. |

---

## 6. Naming standardizations

These are minor — backend or frontend can adapt. Listed so we settle them in one pass:

| Frontend field | Backend field | Suggested resolution |
|---|---|---|
| `code` (on MembershipPlan) | `plan_code` | Backend uses `plan_code`; frontend renames internally. |
| `items_count` | `item_count` | Pick one — recommend `item_count` (matches Frappe naming). |
| `proforma_invoice_no`, `sales_invoice_no` | `proforma_invoice`, `sales_invoice` | Drop `_no` suffix — frontend renames. |
| `refCode` | `reference_code` | Decision: ref_code is short and used in URL paths; recommend `ref_code` snake_case on the wire. |
| `_ar` suffix | `_arabic` suffix | Adopt `_ar` — already in 20+ places. Backend renames DocType labels. |
| Add-on keys (`firstReleases`, etc.) | `addon_first_releases` bools | Wire format: backend's `addon_*` bool fields. Frontend transforms in/out. |

---

## 7. Suggested order of operations

**Sprint 1 — foundation**
- Settle the C-list decisions in one call (90 min).
- Add the new fields to existing DocTypes (§4.3 — Submission, Submission Item, Customer, Coin Master, Issue).
- Create Coupon DocType (§4.1).
- Wire `payment_method`, `promo_code` into Submission creation flow.
- Add `mintmark`, `description`, `description_ar` to Coin Master + verify response (§3.1).

**Sprint 2 — read endpoints**
- Build `GET /membership/me`, `/invoices`, `/services/*`, `/news`, `/price-guide`, `/dealer/*`.
- Build `/submissions/{no}/activity`.
- Adopt the richer quote response (§3.2).

**Sprint 3 — registry v1 + optional v2 start**
- Confirm v1 endpoints (sets, slots, leaderboards) are returning the frontend's shape.
- Build `/customer/certificates?slot=`.
- If v2 is in scope: start the v2 DocTypes and endpoints (§2.12).

**Sprint 4 — polish**
- Catalog search endpoint (`/catalog/coins?q=`) once catalog exceeds ~200 entries.
- News Article DocType + admin UI for editorial team.
- E2E with the frontend flipping `NEXT_PUBLIC_USE_MOCKS=false`.

---

## Quick reference — files in the repo

| File | Purpose |
|---|---|
| `docs/backend-api-contract.md` | Full TypeScript-level contract per domain. The source of truth for wire shapes. |
| `docs/backend-vs-frontend-comparison.md` | Full gap analysis (this doc is the actionable subset). |
| `lib/api/*.ts` | The frontend's wire types. **Implementing the function signatures here exactly is the integration goal.** |
| `lib/mocks/*.ts` | Sample fixtures with realistic data. Useful for QA seeding. |
| `lib/data/*.ts` | Static catalogues (coin catalog, plans, services, postage matrix) the frontend bundles today — most will become API-backed. |

---

*End of adjustments. Suggest a 90-minute call to walk the C-list and the Sprint 1 scope before any gateway code is written.*
