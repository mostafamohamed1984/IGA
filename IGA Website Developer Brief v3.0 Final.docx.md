**IGA**  
**INTERNATIONAL GRADING AGENCY**

**Website Developer Brief**

*Version 3.0 — Final Scope*

IGA Official Website & Verification Platform

*Companion to: IGA Developer Master Brief v1.0 and IGA Developer Master Workbook*

| Field | Value |
| :---- | :---- |
| Project Title | IGA Official Website & Verification Platform |
| Brand Name | International Grading Agency (IGA) |
| Prepared For | Website Developer / Development Team |
| Prepared By | Omar Wael |
| Document Type | Website Structure, Functional Requirements, and Development Brief |
| Version | 3.0 — Final Scope |
| Date | May 2026 |
| Supersedes | IGA Website Developer Brief v1.0 (April 2026\) and v2.0 (May 2026\) |
| Aligned With | IGA Developer Master Brief v1.0 (May 2026\) and Companion Workbook |
| ERP Integration Lead | Eng. Mostafa Nazeer |

# **Change Log — What Is New in v3.0**

v1.0 was the original website brief written before the ERP architecture was finalized. v2.0 brought the website specification into alignment with the IGA Developer Master Brief and its Public API Layer. v3.0 finalizes Phase 1 scope after a competitive review of NGC and PCGS and explicit phasing decisions from IGA leadership.

## **Phase 1 Promotions (was Phase 2 in v2.0)**

* Price Guide — promoted to Phase 1\. Data is entered manually through the ERP; the website reads and renders.

* Registry / My Collection — promoted to Phase 1 with full member-facing UI: sets, slots, leaderboards, scoring.

* Marketplace via Make an Offer — promoted to Phase 1 using existing Support API (creates a ticket of type "Offer" linked to the certificate). Full marketplace flow remains Phase 2\.

## **New Additions from NGC and PCGS Competitive Review**

* Grade Guarantee page — IGA offers a grade guarantee; this is a content-only page documenting the policy and claims process.

* Authorized Dealer Program landing page — marketing page distinct from the public dealer directory.

* Security & Counterfeit Awareness center — content-only educational hub.

* Numismatic Glossary — alphabetical reference; supports SEO and onboarding for new users.

* Holders & Labels reference page — elevated from a Services subsection to a dedicated reference page.

## **Confirmed Phase 2 Items**

* Mobile application

* Banknotes and Trading Cards as live grading categories (Coming Soon on Services)

* Verify warning flags (counterfeit holder reported, reported stolen, mechanical error, removed from population)

* Photograde — visual grading reference library

* Coin Explorer / CoinFacts-depth public catalog

* Cross-service stolen items database

* Public Registry leaderboard as marketing surface (internal leaderboards in member dashboard remain Phase 1\)

## **Other Refinements**

* Brand identity (logo, colors, typography, imagery, components) is provided separately by IGA — the developer does not make design decisions. See §4.

* No inbound shipment carrier tracking. Public Tracking handles IGA submission status only.

| Reading note This document is the website-facing specification. The Master Brief and Workbook own authoritative API contracts, field lists, workflow rules, and validation logic. Whenever this document references a field name, response shape, or state code, the Master Brief is the source. If you find a conflict, follow the Master Brief and flag it for correction here. |
| :---- |

# **Table of Contents**

1\. Introduction

2\. Website Strategy Overview

3\. Content

    Home

    About Us

    Services

    Pricing & Turnaround

    Membership

    Submit

    Verify

    Tracking

    Resources

    Price Guide

    Registry / My Collection

    News & Updates

    Contact Us

    Authorized Dealers (Directory \+ Program landing)

    Grade Guarantee

    Security & Counterfeit Awareness

    Glossary

    Holders & Labels Reference

    Login / My Account

    Dashboard

    Support (authenticated)

    Footer

4\. Design Direction & Brand Identity

5\. Functional Requirements

6\. ERP / API Integration

7\. SEO & Performance Requirements

8\. Content Guidelines

9\. Phase 2 — Deferred Features

10\. Deliverables Required from Developer

11\. Final Notes

Appendix A — Page-to-API Cross-Reference

Appendix B — Result Type and State Code Reference

# **1\. Introduction**

## **1.1 Purpose of This Document**

This document provides a clear and structured brief for development of the official IGA website. It outlines objectives, structure, content, functional requirements, and technical expectations, with explicit alignment to the IGA Developer Master Brief and the Public API Layer it defines.

## **1.2 Project Overview**

The IGA website is the public-facing surface of the IGA platform. It is a functional system interface, not a marketing site. The website communicates with ERPNext exclusively through the versioned Public API Layer (/api/v1/...). ERPNext is never reached directly from any browser or mobile client.

Core functions the website must support:

* Submission of collectibles for grading (authenticated, member-only)

* Certification verification by certificate number or NFC tap (public)

* Submission tracking by tracking ID (public)

* Membership signup, renewal, and rewards management (authenticated)

* Population reporting and Price Guide (public)

* Registry / My Collection (authenticated member feature)

* Support ticketing including offers on certificates (authenticated)

* Access to grading-related resources, glossary, and security education

## **1.3 Website Objectives**

* Present IGA as a trusted and professional grading authority

* Clearly communicate services, grading standards, and pricing

* Enable submission, verification, and tracking through a controlled API layer

* Support member account management end-to-end

* Build credibility through transparency, real verification, and a published grade guarantee

## **1.4 Target Audience**

* Collectibles collectors

* Authorized dealers and professional traders (Dealer Program members)

* Investors in numismatic and collectible assets

* First-time users seeking grading, verification, or education

## **1.5 Scope of Work**

* Website structure and navigation

* Page-level content and layout expectations

* Functional and system requirements

* Integration with the Public API Layer (seven APIs)

* User flows including authenticated, public, and dealer scenarios

* Future scalability considerations

Phase 2 features (see §9) are planned but excluded from this build.

## **1.6 Key Principles**

* Clarity — easy-to-understand, well-structured information

* Trust — design and content reinforce credibility

* Simplicity — user actions (submit, verify, track) are direct

* Consistency — unified design, terminology, and user experience

* Performance — fast loading and responsive across all devices

* Security — proper handling of user data and API credentials

* Bilingual — English (default) and Arabic (full RTL parity)

# **2\. Website Strategy Overview**

## **2.1 Core Purpose of the Website**

The IGA website is both a conversion platform and a functional system interface. It presents IGA as a trusted grading authority and allows users to interact with core services through the Public API Layer. Customers never access ERPNext; every read or write passes through the versioned, rate-limited, audit-logged gateway.

## **2.2 Primary User Journeys**

### **Journey 1 — Verification (Public Trust Journey)**

* Visitor enters a certificate number, or taps the NFC chip embedded in the holder.

* Verify API returns the certified item record, with images and designations, when eligible.

* Outcome: trust established without any account required.

### **Journey 2 — Tracking (Public Operational Journey)**

* Visitor enters a tracking ID printed on submission confirmation.

* Tracking API returns customer-visible status and item-level breakdown.

* Outcome: visibility into in-flight submissions without login.

### **Journey 3 — Service Exploration to Submission**

* Visitor explores services, pricing, grading standards, and Grade Guarantee.

* Signs up; activates a Silver, Gold, Diamond, or Dealer Program membership.

* Submits items through the authenticated Submission API.

* Outcome: submission created, proforma invoice issued, tracking ID returned.

### **Journey 4 — Member Engagement**

* Member logs in via OAuth2.

* Dashboard shows membership, submissions, invoices, rewards, tickets, and Registry sets.

* Member builds Registry sets, redeems rewards, opens support tickets, makes offers on certificates.

### **Journey 5 — Dealer Program Flow**

* Dealer Program member submits on behalf of an end collector.

* Dealer reference number captured; end collector’s email notified on completion.

* Dealer dashboard view aggregates dealer-submitted items.

## **2.3 Conversion Objectives**

* Membership signup (Silver, Gold, Diamond, or Dealer Program)

* Submission creation

* Repeat engagement through the dashboard, Registry, and verification (NFC tap on every slab)

* Trust-building through transparent process, live data, and Grade Guarantee

## **2.4 Trust & Credibility Strategy**

Grading is a trust-based business. Trust is reinforced through:

* A real Verify API that returns live data from the ERP

* NFC tap verification on every IGA holder

* A live Population Report computed from the actual certified population

* A published Grade Guarantee with clear terms

* A Security & Counterfeit Awareness center

* Transparent grading process and standards

## **2.5 Public vs Authenticated Areas**

| Area | Pages |
| :---- | :---- |
| Public | Home, About, Services, Pricing & Turnaround, Membership (browse plans), Submit (info), Verify, Tracking, Resources, Price Guide, News, Contact, Authorized Dealers Directory, Authorized Dealer Program landing, Grade Guarantee, Security & Counterfeit Awareness, Glossary, Holders & Labels Reference |
| Authenticated | Dashboard, Submissions list, Submission detail, Membership detail, Invoices, Rewards, Registry / My Collection, Support tickets, Profile, Dealer view (Dealer Program members only) |

## **2.6 Key Success Factors**

* Clear navigation across public and authenticated areas

* Fast, responsive performance — Verify and Tracking are the most-hit endpoints

* Accurate API integration with strict respect for response field names

* Strong trust signals through design, functional proof, and Grade Guarantee

* Smooth submission flow from landing through proforma invoice

# **3\. Content**

Each page below specifies content, layout intent, and the API endpoints it consumes. Field names follow the Master Brief Appendix B and Workbook tabs 04 (Submission Item Fields) and 16 (API Map).

## **Home**

### **1\. Hero Section**

* Headline: Where Accuracy Defines Value

* Subtext: Professional grading and authentication services

* Primary buttons: Submit, Verify

### **2\. How It Works**

Customer-visible stages, exactly as defined in Master Brief §4.1:

*Created → Received → Grading → Slabbing → QC → Imaging → Shipped or Ready for Pickup → Completed*

| Important — stage naming "Packing" and "Delivery" are not customer-visible stages in the ERP. Use "Shipped or Ready for Pickup" instead. "On Hold" is a reversible state that may appear at any stage and must be supported in the UI. |
| :---- |

### **3\. Certification Lookup**

* Single input: Enter Certificate Number

* Button: Verify

* Secondary CTA: Tap NFC chip (mobile only, where Web NFC is supported)

### **4\. Quick Links**

* What We Grade → Services

* Grading Process → Services

* Grading Standards → Resources / Grading Scale

* Grade Guarantee → Grade Guarantee page

### **5\. News**

* 3 latest items with Title and Date

### **6\. Final CTA**

* Text: Ready to submit your items?

* Buttons: Become a member, Submit

### **API Touchpoints**

* Certification Lookup routes to Verify (GET /api/v1/verify/{cert\_no})

* News list via CMS read or fixture

## **About Us**

### **1\. Company Overview**

International Grading Agency (IGA) is a modern grading and authentication authority specializing in collectible items, including coins, banknotes, medals, and related collectibles.

IGA was established to provide a reliable, locally accessible grading solution aligned with international standards. It reduces dependence on external markets, shortens turnaround times, and provides collectors and dealers with consistent, verifiable results through a structured and controlled system.

### **2\. Why IGA**

* Structured and controlled evaluation standards

* Consistent grading methodology — six approved scoring components, weighted per Master Brief §7

* Transparent and verifiable results — public Verify and Population APIs

* Secure certification — tamper-evident holders and NFC chips on every slab

* Backed by the IGA Grade Guarantee

### **3\. What We Do**

IGA provides professional grading, authentication, and Conservation services. The full workflow is detailed in Services.

### **4\. Our Standards**

IGA follows a structured grading methodology based on recognized industry principles (NGC, PCGS) and evidence-based evaluation. The full grading manual is referenced in the Master Brief Appendix D.

* Button: View Grading Standards (PDF)

## **Services**

### **1\. Introduction**

IGA delivers structured workflows, strict grading standards, and controlled processes — consistent, accurate, and fully verifiable. Every submission is graded, professionally documented, and protected in tamper-evident holders.

### **2\. What We Grade**

* Coins — ancient to modern, including commemoratives, bullion, and mint-error attributions

* Medals & Tokens — historical and modern pieces, privately issued items, non-circulating collectibles

* Banknotes (Coming Soon) — Phase 2

* Trading Cards (Coming Soon) — Phase 2

### **3\. Grading Process**

*Created → Received → Grading → Slabbing → QC → Imaging → Shipped or Ready for Pickup → Completed*

Step descriptions:

* Created — submission registered; certificate numbers allocated atomically per item; proforma invoice issued; tracking ID returned

* Received — physical intake scanned; internal barcodes assigned; photographs taken

* Grading — six approved scoring components evaluated per item

* Slabbing — NFC chip encoded; item encapsulated; label printed

* QC — senior grader confirms or overrides; final result locked

* Imaging — obverse and reverse uploaded to CDN; linked to the certificate

* Shipped or Ready for Pickup — carrier tracking link issued, or held at counter

* Completed — delivery confirmed; sales invoice finalized; reward points awarded

| Result Types Every item ends with one of four Result Types: Encapsulated, Details, Not Encapsulated, or Rejected. See Appendix B for how each Result Type is presented on Verify. |
| :---- |

### **4\. Holders & Labels**

Summary here; full reference on the dedicated Holders & Labels page.

* Standard Holders (13–40 mm)

* Oversized Holders (41–65 mm)

* Multi-item Holders (configurations on request)

* Labels: Standard, Early Releases, First Day of Issue, Signed, Pedigree, Event

### **5\. Conservation Service**

Conservation stabilizes and protects collectibles using controlled, non-destructive techniques. Each item is individually assessed; not all pieces qualify. Pricing is "Contact agent" per the Service Master.

### **6\. Fees & Turnaround**

* Button: View Pricing & Turnaround

### **7\. Grade Guarantee**

All IGA-certified items are backed by the IGA Grade Guarantee. See the Grade Guarantee page for full terms.

## **Pricing & Turnaround**

### **1\. Introduction**

IGA pricing is structured by item category and service tier. Tiers determine both price and turnaround. All prices are per piece, in Egyptian Pounds (EGP), and exclude 14% VAT. Pricing data is sourced from the Service Master DocType.

### **2\. Service Tiers**

| Service | Tier | Price (EGP) | Turnaround | Max Declared Value (EGP) |
| :---- | :---- | :---- | :---- | :---- |
| Modern Coins (1951–Date) | Value | 599 | 14–21 days | 25,000 |
| Modern Coins (1951–Date) | Standard | 935 | 7–10 days | 75,000 |
| Modern Coins (1951–Date) | Express | 999 | 3–5 days | 150,000 |
| Early Modern (1801–1950) | Value | 799 | 14–21 days | 50,000 |
| Early Modern (1801–1950) | Standard | 1,045 | 7–10 days | 100,000 |
| Early Modern (1801–1950) | Express | 1,199 | 3–5 days | 250,000 |
| Medieval Coins (501–1800) | Standard | 1,925 | 14–21 days | 150,000 |
| Medals & Tokens (1700–Date) | Standard | 935 | 14–21 days | 100,000 |
| Medals & Tokens (1700–Date) | Express | 1,650 | 7–10 days | 150,000 |
| High Value Items | Priority | 2,750 | 1–2 days | 500,000 |
| Unlimited Value Items | Priority | Contact agent | 1–2 days | Unlimited |

### **3\. Add-On Services**

| Service | Pricing Rule | Notes |
| :---- | :---- | :---- |
| Re-Grade | Selected tier \+ 25% | Aim for a higher grade; piece remains in original holder |
| Cross-Over | Selected tier | Review pieces from other companies; graded only if equal or higher |
| Re-Slab | Selected tier \+ 50% | Re-encapsulate IGA-graded pieces in new holders |
| Bulk Grading | Selected tier − 10% | Same submission, same tier; minimum item count enforced |
| Restoration | Contact agent | Specialist conservation |

### **4\. Membership Requirement**

Active membership is required to submit. See the Membership page for plan details.

### **5\. VAT**

All prices exclude 14% VAT. VAT is added at invoice generation.

### **API Touchpoints**

* Plans rendered from GET /api/v1/membership/plans (public)

* Service tiers from Service Master fixture

* Optional quote preview via POST /api/v1/submissions/quote

## **Membership**

### **1\. Introduction**

IGA membership is required to submit items for grading. Membership also unlocks Registry access, rewards, and tier-specific benefits. Four plans are available: Silver, Gold, Diamond, and Dealer Program.

### **2\. Plans**

| Plan | Plan Code | Audience | Notes |
| :---- | :---- | :---- | :---- |
| Silver | SILVER | Entry tier | Basic registry access; standard reward multiplier |
| Gold | GOLD | Active collectors | Larger credit bundle; higher reward multiplier; service discount |
| Diamond | DIAMOND | Premium / high-volume | Maximum entitlements; priority queue access where applicable |
| Dealer Program | DEALER | Authorized dealers | Enables the Authorized Dealer flow; dedicated invoicing rules |

### **3\. How to Subscribe**

* Create a standard account or log in

* Select a plan and billing period (monthly or annual)

* A Membership Sales Invoice is issued (separate from any submission invoice)

* Pay via cash, bank transfer, or future online methods

* Membership activates upon payment confirmation

### **4\. Rewards**

Reward points accrue on submission payment confirmation — never on membership fees. Points may be redeemed against future submission invoices, subject to per-plan max redemption percentage rules.

### **API Touchpoints**

* GET /api/v1/membership/plans (public)

* POST /api/v1/membership/subscribe (member token)

* GET /api/v1/membership/subscription (member token)

* POST /api/v1/membership/subscription/cancel

* GET /api/v1/membership/rewards

* POST /api/v1/membership/rewards/redeem

## **Submit**

### **1\. Introduction**

Submit your collectible items to IGA for professional grading and authentication. An active Silver, Gold, Diamond, or Dealer Program membership is required.

### **2\. Membership Required**

Before the submission form opens, the system validates the customer’s active membership via the Membership API. Without an active subscription, the form is blocked and the customer is routed to the Membership page.

### **3\. How to Submit**

* Register or activate membership

* Complete the online submission form

* Prepare and package items per submission guidelines

* Deliver via an Authorized Dealer or ship directly to IGA

* Track your submission via the public Tracking page or your dashboard

### **4\. Online Submission Form**

Fields aligned to POST /api/v1/submissions:

Submission-level:

* service\_tier (link to Service Master)

* category (Modern / Early Modern / Medieval / Medals & Tokens / High Value / Unlimited)

* is\_bulk (checkbox)

* uses\_credit (checkbox)

* submission\_source (Customer / Dealer / Walk-in / Partner / Migration)

* dealer (Dealer Program members only)

* submitted\_on\_behalf\_of (optional)

* dealer\_reference\_no (optional)

Per item:

* item\_reference (link to Item Reference Catalog)

* declared\_value (currency, EGP)

* declared\_grade (optional)

On success the API returns:

* submission\_no, tracking\_id, proforma\_invoice\_no, status, items\[\]{certificate\_number}

### **5\. PDF Submission Form (offline)**

A downloadable PDF remains available for offline submissions through Authorized Dealers.

### **Error Handling**

| Code | Meaning | UI Behavior |
| :---- | :---- | :---- |
| 400 ValidationError | Field validation failed | Inline error per field |
| 401 Unauthorized | Not logged in or token expired | Redirect to login |
| 402 PaymentRequired | Membership inactive or unpaid | Route to Membership page |
| 403 NotEntitled | Service tier not allowed for this plan | Show plan upgrade prompt |
| 409 SubscriptionInactive | Subscription not currently active | Route to renewal |

## **Verify**

### **1\. Introduction**

Verify the authenticity and details of IGA-certified items. Lookup is available by certificate number or by NFC tap. Each certified item is linked to a unique record in the IGA system, exposed publicly only after the submission reaches Shipped or Ready for Pickup and the item’s Result Type is Encapsulated or Details.

### **2\. Certification Lookup**

* Input: Certificate Number (only)

* Button: Verify

* Secondary: Tap NFC (mobile, where Web NFC is supported)

### **3\. Verification Result — Displayed Fields**

| Field (API) | UI Label | Notes |
| :---- | :---- | :---- |
| certificate\_number | Certificate Number | Prominent, monospaced |
| result\_type | Result Type | Encapsulated / Details — drives result presentation |
| label\_country\_denom | Country & Denomination | Line 1 of the slab label |
| label\_year\_line | Year | AH/AD format where applicable |
| label\_series\_line | Series | Series or pedigree line |
| final\_grade | Grade | Prominent — large display |
| designations\[\] | Designations | Canonical IGA designation codes |
| holder\_type | Holder Type | From Holder Types Master |
| images.obverse | Obverse Image | High-res from CDN |
| images.reverse | Reverse Image | High-res from CDN |
| graded\_on | Graded On | Date QC stage was completed |
| nfc\_signature\_valid | NFC Signature Valid | Relevant on NFC tap only |

### **4\. Actions on a Valid Result**

* Make an Offer — opens a form that creates a Support ticket of type "Offer" linked to the certificate

* Report Certificate — opens a Support ticket pre-filled with the cert number

| Make an Offer behavior In Phase 1, "Make an Offer" routes through the Support API. The form captures offer amount, message, and contact details; on submit, a Support ticket of type "Offer" is created with related\_certificate set to the certificate number. IGA staff relay the offer to the certificate owner manually. A full peer-to-peer marketplace flow remains Phase 2\. |
| :---- |

### **5\. Response States**

| HTTP | State | Cause | UI |
| :---- | :---- | :---- | :---- |
| 200 | Verified | Encapsulated or Details; submission Shipped/Ready | Full result card |
| 404 | Not Found | Certificate does not exist | Status: No Record Found |
| 410 | Gone (Rejected) | Item was Rejected | Status: Certificate Not Available |
| 425 | Too Early | Submission not yet Shipped or Ready for Pickup | Status: Verification Not Yet Available |
| 429 | Rate Limited | Too many requests | Status: Please wait and try again |
| 401 | Invalid Signature | NFC tap signature failed | Status: NFC tag could not be verified |

### **6\. NFC Tap Verification**

Where the browser supports Web NFC, the Verify page reads the chip embedded in the slab and forwards the signed payload to POST /api/v1/verify/nfc.

### **API Touchpoints**

* GET /api/v1/verify/{cert\_no}

* POST /api/v1/verify/nfc

* POST /api/v1/support/tickets (Make an Offer, Report Certificate)

## **Tracking**

### **1\. Introduction**

Enter your tracking ID to see the current status of a submission. Tracking is public; no account required.

### **2\. Lookup**

* Input: Tracking ID

* Button: Track

### **3\. Result Display**

* tracking\_id

* customer\_visible\_status (Created / Received / Grading / Slabbing / QC / Imaging / Shipped / Ready for Pickup / Completed / On Hold)

* items\_count

* items\_breakdown (per-stage counts)

* eta

* last\_event

### **4\. Visual Direction**

* Stage tracker as a horizontal progress indicator

* On Hold rendered as a non-positional banner above the tracker

### **5\. Response States**

* 200 — render the tracker

* 404 — Tracking ID not recognized

* 429 — rate limited

### **API Touchpoints**

* GET /api/v1/tracking/{tracking\_id}

## **Resources**

### **1\. Introduction**

Direct access to the standards, data, and references behind every IGA-certified item.

### **2\. Grading Scale**

IGA’s grading scale translates condition into a consistent, repeatable standard, referenced from the Grade Scale Master.

* Button: View Grading Scale

### **3\. Population Report**

Live counts of certified items per reference, by grade and designation. Search by reference code, category, country, year, mint, variety, designation.

### **4\. Designations Reference**

Canonical IGA designation codes and their NGC/PCGS equivalents.

### **5\. Quick Links**

* Price Guide

* Glossary

* Holders & Labels Reference

* Grade Guarantee

* Security & Counterfeit Awareness

### **API Touchpoints**

* GET /api/v1/population/reference/{ref\_code}

* GET /api/v1/population/search

## **Price Guide**

| Phase 1 — manual ERP entry Price Guide data is entered and maintained manually in the ERP. The website reads and renders. No marketplace data, no auction integration, no external feed. Updates appear on the website as soon as ERP edits are saved. |
| :---- |

### **1\. Introduction**

The IGA Price Guide provides structured market value reference for certified items, curated by IGA staff. Prices reflect observed market activity and IGA editorial judgment, not automated feeds.

### **2\. Lookup**

* Search by reference code, category, country, year, mint, variety, designation

* Or browse hierarchically (category → country → series → item)

### **3\. Result Display**

* Reference description and image

* Values by grade (table or chart)

* Last updated date

* Editorial notes from IGA (optional, when present)

### **4\. Visual Direction**

* Clean tabular layout; high readability

* Grade columns left to right, ascending

* No advertisements, no third-party affiliate links

### **API Touchpoints**

* Custom Price Guide endpoint (to be confirmed with Eng. Mostafa) reading from a Price Guide DocType in ERPNext

* Optionally: federate population from GET /api/v1/population/reference/{ref\_code} for cross-reference

## **Registry / My Collection**

| Phase 1 — full member-facing UI Members can browse public set definitions, create their own member sets, fill slots with their IGA-certified items, see their score and rank within each set, and view internal leaderboards. Public leaderboard marketing surfaces (curated showcases, top-collector profiles, awards) are Phase 2\. |
| :---- |

### **1\. Public Browse**

* Categories — top-level groupings (e.g., Egyptian Royal Era, World Crowns)

* Set Definitions — IGA-owned set templates with slot requirements

* Set detail — slot list, scoring rules, current top members (member usernames only)

### **2\. Member Sets (authenticated)**

* Create a new member set from a set definition

* Fill slots with owned IGA certificates

* View score, rank, and completion percentage

* Edit slot assignments at any time

### **3\. Slot Fill Validation**

A slot can only be filled by an IGA-certified item the member owns. The system validates the certificate number against live Submission Item data via the Registry API; mismatched grades or ineligible items are rejected with a clear message.

### **4\. Leaderboards (internal)**

* Per set definition, ranked list of member sets by score

* Visible to all logged-in members

* Member usernames only — no real names unless the member opts in

### **5\. Privacy**

* Member sets are private by default

* Members may opt in to leaderboard visibility

* No public-facing collection showcases in Phase 1

### **API Touchpoints**

* GET /api/v1/registry/categories (public)

* GET /api/v1/registry/sets (public)

* GET /api/v1/registry/sets/{code} (public)

* GET /api/v1/registry/my-sets (member)

* POST /api/v1/registry/my-sets (member)

* PUT /api/v1/registry/my-sets/{no}/slots (member)

* GET /api/v1/registry/leaderboard/{code}

## **News & Updates**

### **1\. Introduction**

Latest announcements, developments, and official updates from IGA.

### **2\. News Listing**

* Per item: Title, Date, Brief

* Layout: vertical list or grid (3 per row)

### **3\. Article Page**

* Title, Date, Author, Body

### **Content Source**

News records authored in ERPNext; read through a CMS endpoint or fixtures.

## **Contact Us**

### **1\. Introduction**

Contact IGA directly or visit one of our authorized dealers.

### **2\. Contact Information**

* Email: cs@igaverify.com

* Working Hours: Saturday to Thursday, 10:00 AM – 6:00 PM (closed Friday)

### **3\. Contact Form**

Fields: Name, Email, Subject, Message. CAPTCHA mandatory.

On submit: delivered to IGA support inbox; no ERP ticket created. Authenticated members use the Support page for tickets.

## **Authorized Dealers**

| Two distinct surfaces The public Authorized Dealers Directory is a static or CMS-managed list of approved dealers. The Authorized Dealer Program landing page is a marketing page explaining the Dealer Program membership and benefits. They are separate. |
| :---- |

### **1\. Public Dealer Directory**

* Per dealer: name, location, mobile number

* Optional map for location-based discovery

* Filter by region or country

### **2\. Authorized Dealer Program — Landing Page**

Marketing page explaining the Dealer Program membership: benefits, requirements, application process, dedicated invoicing rules, the ability to submit on behalf of end collectors, and tier comparisons. CTA routes to Membership signup with the DEALER plan code preselected.

* Benefits — priority handling, dedicated invoicing, dealer dashboard, submission-on-behalf flow

* Requirements — published criteria for dealer approval

* Application — link to Membership signup

* Existing dealer list — link to the Directory

### **3\. Dealer Submission Flow**

Detailed on the Submit page.

## **Grade Guarantee**

| Phase 1 — content only IGA offers a Grade Guarantee on all certified items. This page documents the policy in plain language and links to a claims process. Final wording, terms, and limits to be provided by IGA leadership. |
| :---- |

### **1\. Introduction**

Every IGA-certified item is backed by the IGA Grade Guarantee. The guarantee provides protection for both buyers and sellers against grading errors, authentication errors, and tampering.

### **2\. What the Guarantee Covers**

* Authentication — the item is genuine

* Grade accuracy — the grade reflects IGA standards as applied at the time of grading

* Holder integrity — the holder is genuine and untampered

### **3\. What the Guarantee Does Not Cover**

* Mechanical errors (clerical or typographical errors on the label) — handled separately as a label correction

* Coins removed from the holder by the owner

* Holders that show evidence of tampering

* Environmental damage occurring after encapsulation

### **4\. How to File a Claim**

* Open a Support ticket of type "Guarantee Claim" with the certificate number

* IGA staff review and respond

* Resubmission for re-grading may be required at IGA discretion

### **5\. Final Terms**

Final policy text, limits, and turnaround commitments to be provided by IGA. This section is a placeholder for that content.

### **API Touchpoints**

* POST /api/v1/support/tickets (Guarantee Claim)

## **Security & Counterfeit Awareness**

| Phase 1 — content only Educational hub on holder security, counterfeit detection, and scam awareness. Content provided by IGA. No backend dependencies. |
| :---- |

### **1\. Introduction**

IGA holders incorporate tamper-evident features and NFC chips on every slab. This center explains how to verify your holder is genuine, how to recognize counterfeits, and how to protect yourself from common scams.

### **2\. Verify Your Holder**

* Use the Verify page or NFC tap to check every certificate before purchase

* Confirm the image on Verify matches the coin in hand

* Check holder security features (described in detail)

### **3\. Counterfeit Detection**

* Common counterfeit indicators on coins

* Common counterfeit indicators on holders

* Reference images from IGA archives

### **4\. Scam Awareness**

* IGA does not buy or sell coins

* Be cautious of unsolicited contact claiming to be from IGA

* Only buy from Authorized Dealers or trusted sources

### **5\. Report a Suspicious Item**

Link to the Support page with a pre-filled ticket type.

### **Content Source**

All content authored by IGA. Updated periodically by the editorial team.

## **Numismatic Glossary**

| Phase 1 — content only Alphabetical glossary of grading, numismatic, and IGA-specific terms. Strong SEO value; helps first-time submitters understand the language on certificates. Content provided by IGA. |
| :---- |

### **1\. Layout**

* Alphabetical index A–Z

* Term, definition, optional related terms, optional reference image

* Anchor links per letter for fast navigation

### **2\. Coverage**

* Grading terms (Mint State, Proof, About Uncirculated, etc.)

* Designations (PL, DCAM, FBL, Plus, Star, etc.) with NGC/PCGS equivalents

* Mint error terminology (off-center, double-struck, broadstrike, etc.)

* Problem terminology (cleaned, environmental damage, tooled, etc.)

* IGA-specific terms (Result Type, Encapsulated, Details, Not Encapsulated, etc.)

### **3\. SEO**

* Each term gets a unique URL slug

* Schema.org DefinedTerm structured data where applicable

## **Holders & Labels Reference**

| Phase 1 — content \+ reference imagery Dedicated reference page elevated from the Services subsection. Shows every IGA holder type and every label variant with high-resolution images. Useful for collectors and dealers identifying older holders. |
| :---- |

### **1\. Holders**

* Standard Holders (13–40 mm) — image, dimensions, materials

* Oversized Holders (41–65 mm) — image, dimensions, materials

* Multi-item Holders — image, configurations available

All holders include tamper-evident features and an NFC chip.

### **2\. Labels**

* Standard Label — purpose, example image

* Early Releases — qualifying criteria, example

* First Day of Issue — qualifying criteria, example

* Signed Labels — process, eligibility, example

* Pedigree Labels — qualifying provenance, example

* Event Labels — eligible events, example

### **3\. Holder Generations**

As IGA evolves holder designs over time, this page will document each generation. At launch, only the current generation is present.

### **Content Source**

Reference images supplied by IGA along with brand identity assets.

## **Login / My Account**

### **1\. Login**

* Fields: Email, Password

* Buttons: Login, Forgot Password

* Secondary: Sign Up

### **2\. Authentication Flow**

* OAuth2 token issued by the API gateway on successful login

* Token stored in httpOnly cookie where possible

* Forgot Password triggers reset via the gateway

### **3\. Sign Up**

Creates a standard account. Standard accounts cannot submit; the user must activate a membership separately.

## **Dashboard / My Account**

### **1\. Dashboard Overview — Summary Cards**

* Draft Submissions

* Active Submissions

* Completed Submissions

* Membership Status (Active / Inactive / Pending)

* Rewards Balance

* Open Support Tickets

* Registry Sets Count

### **2\. My Membership**

* Status, Plan (Silver / Gold / Diamond / Dealer Program), Plan Code, Billing Period, Renewal Date

* Credits Remaining

* Button: Renew Membership

### **3\. My Submissions**

* Per submission: Submission Number, Date, Items Count, Customer-visible Status

* Action: View Details

### **4\. Submission Details**

* Submission Number, Tracking ID, Status

* Items list — per item: certificate\_number, item\_reference, declared\_value, current item stage, Result Type when concluded

* Linked invoices (Proforma and Sales Invoice)

* Dates: received, grading complete, completed

* Dealer fields when applicable: dealer, submitted\_on\_behalf\_of, dealer\_reference\_no

### **5\. Invoices (read-only from ERP)**

* Invoice Number, Type (Proforma / Sales / Membership), Submission Number

* Date, Total Amount (EGP), VAT (14%), Total with VAT

* Status: Pending / Under Review / Paid / Cancelled

* Down Payment Applied

* Credits Applied

* Itemized breakdown when provided

* PDF Download when provided

Rules: No invoice creation, no editing, no payment processing on the website.

### **6\. Rewards**

* Current balance

* Ledger: earn, redeem, expire entries

* Action: Redeem against an invoice (subject to max\_redeem\_pct)

### **7\. Registry / My Collection**

* My member sets — score, rank, completion percentage

* Action: Create new member set

* Action: Manage slots

* View leaderboards (internal, all logged-in members)

### **8\. Support Tickets**

* List of tickets: ticket\_no, subject, status, last update

* Action: New Ticket

* Action: View Ticket — threaded message view

### **9\. Dealer View (Dealer Program members only)**

* Aggregated list of submissions made on behalf of others

* Filter by end collector, dealer\_reference\_no, date range

* Export to CSV

### **API Touchpoints**

* GET /api/v1/submissions and /submissions/{no}

* GET /api/v1/membership/subscription

* GET /api/v1/membership/rewards; POST /membership/rewards/redeem

* GET /api/v1/registry/my-sets; POST /registry/my-sets; PUT /registry/my-sets/{no}/slots

* GET /api/v1/support/tickets; POST /support/tickets; POST /support/tickets/{no}/messages

## **Support (Authenticated)**

### **1\. Tickets List**

* Per ticket: ticket\_no, subject, status, last update, related submission or certificate

### **2\. New Ticket Form**

* Subject, Body, Type (General / Offer / Report Certificate / Guarantee Claim), Related Submission, Related Certificate, Attachments

### **3\. Ticket Detail**

* Threaded message view

* Action: Add Message (body, attachments)

### **API Touchpoints**

* GET, POST /api/v1/support/tickets

* GET /api/v1/support/tickets/{no}

* POST /api/v1/support/tickets/{no}/messages

## **Footer**

### **1\. Structure**

* Company — About Us, Services, Pricing, Submit

* Tools — Verify, Tracking, Price Guide

* Resources — Grading Scale, Population Report, Designations, Glossary, Holders & Labels

* Membership — Silver, Gold, Diamond, Dealer Program

* Trust — Grade Guarantee, Security & Counterfeit Awareness, Authorized Dealers Directory

* Support — Contact Us, FAQ

* Legal — Privacy Policy, Membership Terms & Conditions, Submission Terms & Conditions

### **2\. Branding**

* IGA Logo

* Tagline: Where Accuracy Defines Value

### **3\. Copyright**

© 2026 International Grading Agency. All rights reserved.

# **4\. Design Direction & Brand Identity**

| Brand identity provided separately Full brand identity — logo, color palette, typography, imagery direction, UI components, and reference styling — is provided separately by IGA. The developer does not make brand or visual design decisions. This section documents design-related functional requirements only. |
| :---- |

## **4.1 What IGA Provides**

* Logo (primary, secondary, monochrome variants)

* Color palette with usage rules

* Typography (display and body fonts) with licensing

* Imagery direction and reference photography

* UI component reference (buttons, cards, forms, tables, navigation)

* Iconography

* Holder and label reference imagery for the Holders & Labels page

## **4.2 What the Developer Implements**

* Faithful translation of brand identity into responsive components

* Bilingual EN/AR variants of every component with proper RTL handling

* Result Type presentations on Verify (distinct visual treatment per Result Type — see Appendix B)

* Stage tracker on Tracking and Dashboard, including On Hold non-positional banner

* NFC tap affordance on mobile

* Plan badges for Silver, Gold, Diamond, and Dealer Program — consistent across pricing, dashboard, membership pages

* Accessible color contrast and readable font sizes

## **4.3 Design Approvals**

* Component-level designs reviewed and approved by IGA before implementation

* Developer may propose enhancements, subject to approval

* Bilingual layouts verified in both LTR (English) and RTL (Arabic)

# **5\. Functional Requirements**

## **5.1 General**

* Fully responsive across desktop, tablet, and mobile

* Clean, consistent UI

* Fast loading; optimized assets

* All user data and API interactions handled securely (HTTPS, no token exposure)

## **5.2 Navigation**

* Clear, consistent navigation across all pages

* Active page highlighted

* Footer includes all key links

* Language switcher visible on every page

## **5.3 Forms**

* Contact Form (public): Name, Email, Subject, Message; CAPTCHA mandatory; confirmation on success

* Submission Form (authenticated): multi-item, dealer-aware; validates membership; confirmation with submission\_no, tracking\_id, proforma\_invoice\_no

* Membership Signup: plan, billing period, auto-renew; confirmation with Sales Invoice number

* Support Ticket: subject, body, type, related submission, related certificate, attachments

* Make an Offer: amount, message, contact details — creates Support ticket of type "Offer"

## **5.4 Authentication**

* Sign Up creates a standard account (no submission rights)

* Login via OAuth2 against the API gateway

* Forgot Password / reset

* Secure session handling; tokens never exposed to client-side JS where avoidable

## **5.5 Membership Logic**

* Standard accounts: public features only

* Active membership required for submission, full dashboard, Registry member sets, and Support tickets

* System enforces membership before any /api/v1/submissions POST

## **5.6 Dashboard**

* User-specific data only

* Membership, submissions, invoices, rewards, Registry sets, tickets

* Dealer Program members see the Dealer view

## **5.7 Verification**

* Manual cert lookup via GET /api/v1/verify/{cert\_no}

* NFC tap via POST /api/v1/verify/nfc

* Six response states with distinct UI treatments (200, 404, 410, 425, 429, 401\)

## **5.8 Tracking**

* Public Tracking page accepting tracking\_id

* Stage tracker with On Hold support

## **5.9 Registry**

* Public browse of categories and set definitions

* Authenticated member set creation and slot management

* Slot fill validation against live certificate data

* Internal leaderboards visible to all logged-in members

## **5.10 Price Guide**

* Reads from a Price Guide DocType in ERPNext (custom endpoint to be confirmed)

* Search by reference, category, country, year, mint, variety, designation

* Hierarchical browse alternative

* No write operations from the website

## **5.11 Marketplace via Support**

* Make an Offer button on Verify result page

* Creates a Support ticket of type "Offer" with related\_certificate populated

* IGA staff relay manually

* No peer-to-peer messaging in Phase 1

## **5.12 Dynamic Content**

* News, Resources, Glossary, Authorized Dealers Directory, FAQs, Grade Guarantee policy, Security center content — editable through the ERP CMS layer or fixtures

## **5.13 File Handling**

* Downloadable PDFs (submission form, grading standards, terms) hosted securely

* Invoice PDFs proxied through the API gateway

## **5.14 Payments & Invoicing**

* Proforma Invoice issued automatically on submission creation

* Sales Invoice issued before submission packing

* Customer pays offline (cash, bank transfer) or via subscription credits

* Membership Sales Invoices separate from submission invoices

* Rewards awarded only after submission payment confirmation

* Website is read-only for invoices; no creation, editing, or payment processing

## **5.15 Rewards**

* Balance and ledger visible in dashboard

* Redemption against open invoices, subject to max\_redeem\_pct

## **5.16 Support Tickets**

* Authenticated UI backed by Support API

* Ticket types: General, Offer, Report Certificate, Guarantee Claim

* Threaded messages, attachments, related submission or certificate linkage

## **5.17 API Integration**

* All integrations go through /api/v1/...

* Public endpoints rate-limited per IP; authenticated endpoints scoped to the token holder

* Response field names follow the API contract exactly

* Errors handled per the response codes defined for each endpoint

## **5.18 Security**

* HTTPS-only

* Tokens in httpOnly cookies where possible; never in localStorage

* No direct database exposure; ERPNext unreachable from any browser

* CAPTCHA on the public Contact form

## **5.19 Error Handling**

* Clear, professional error messages on every API response state

* Network failures surface a Try Again affordance

* No internal field names ever shown to the user

## **5.20 Performance**

* Optimize images (compressed, responsive)

* Minify CSS and JS

* Cache Verify and Population client-side for short TTLs in addition to gateway cache

* Defer non-critical scripts

# **6\. ERP / API Integration**

## **6.1 Architecture**

The website is a thin front-end client of the Public API Layer. ERPNext is internal-only. All endpoints are versioned (/api/v1/...) and either public (rate-limited) or member-authenticated (OAuth2 / JWT).

| Coordinate with Eng. Mostafa Nazeer All ERP / API integration must be coordinated directly with the ERP integration lead. No assumptions about response shapes, field names, or auth flows should be made without confirmation. Master Brief §9 and Workbook tab 16 are the authoritative API references. |
| :---- |

## **6.2 Endpoint Catalog**

| API | Auth | Purpose |
| :---- | :---- | :---- |
| Verify API | Public | Look up a certificate by number or NFC tap |
| Population API | Public | Population matrix per reference, computed live |
| Submission Tracking API | Public | Submission status by tracking ID |
| Submission API | Member token | Create, list, read submissions; quote pricing |
| Support API | Member token | Tickets and messages |
| Registry API | Mixed | Browse public, manage member sets authenticated |
| Membership API | Mixed | Plans browse public; subscription, rewards authenticated |

## **6.3 Verify API**

* GET /api/v1/verify/{cert\_no}

* POST /api/v1/verify/nfc

* Response: certificate\_number, result\_type, label\_country\_denom, label\_year\_line, label\_series\_line, final\_grade, designations\[\], holder\_type, images{obverse,reverse}, graded\_on, nfc\_signature\_valid

* Errors: 404, 410, 425, 429, 401 (NFC)

## **6.4 Population API**

* GET /api/v1/population/reference/{ref\_code}

* GET /api/v1/population/search

* Errors: 400, 404, 429

## **6.5 Submission Tracking API**

* GET /api/v1/tracking/{tracking\_id}

* Errors: 404, 429

## **6.6 Submission API**

* POST /submissions, GET /submissions, GET /submissions/{no}

* POST /submissions/{no}/cancel

* POST /submissions/quote

* Owner-scoped reads

## **6.7 Support API**

* POST /support/tickets, GET /tickets, GET /tickets/{no}

* POST /tickets/{no}/messages

* Ticket types include: General, Offer, Report Certificate, Guarantee Claim

## **6.8 Registry API**

* GET /registry/categories, /sets, /sets/{code} (public)

* GET /registry/my-sets, POST /my-sets, PUT /my-sets/{no}/slots (member)

* GET /registry/leaderboard/{code}

## **6.9 Membership API**

* GET /membership/plans (public)

* POST /membership/subscribe, GET /membership/subscription, POST /membership/subscription/cancel

* GET /membership/rewards, POST /membership/rewards/redeem

## **6.10 Price Guide Endpoint (to be confirmed)**

The Price Guide page requires a read endpoint exposing Price Guide DocType records. Endpoint contract, response fields, and caching strategy to be defined with Eng. Mostafa.

## **6.11 Auth & Session**

* OAuth2 / JWT issued at member login

* Tokens transmitted over HTTPS; stored in httpOnly cookies where possible

## **6.12 Caching & Real-Time**

* Verify and Population cached at the gateway for 30–120s

* Cache invalidates on Submission Item state changes

* Tracking is near real-time

## **6.13 System Separation**

* ERPNext internal-only; no direct ERPNext URLs in the website

* All website traffic flows through the API gateway

* Sensitive internal fields never appear in API responses or website code

# **7\. SEO & Performance Requirements**

## **7.1 SEO Structure**

* Unique title and meta description per page

* Proper heading hierarchy (H1, H2, H3)

* Clean readable URLs: /services, /verify, /tracking, /pricing, /membership, /registry, /price-guide, /glossary, /guarantee, /security, /holders-labels

## **7.2 Content Optimization**

* Clear, structured text; no duplicate content

* Consistent terminology matching the ERP

* Glossary page provides strong internal linking opportunities for SEO

## **7.3 Technical SEO**

* XML sitemap

* robots.txt — disallow /dashboard, /support, /registry/my-sets, all authenticated routes

* Canonical URLs

* Schema.org structured data: Organization on About; DefinedTerm on Glossary; Product on Service tiers; FAQPage on FAQ

## **7.4 Performance**

* Optimized, responsive images

* Minified CSS and JS

* Defer non-critical scripts

* Client-side cache Verify and Population in addition to gateway cache

## **7.5 Mobile & Accessibility**

* Fully responsive

* Readable font sizes; proper contrast

* Keyboard accessible

* Bilingual EN/AR with proper RTL handling

## **7.6 Error Handling & Indexing**

* Proper 404 page

* Authenticated routes excluded from indexing

## **7.7 Performance Monitoring**

* Analytics integration

* Track Verify, Tracking, and Submit funnels

# **8\. Content Guidelines**

## **8.1 Tone of Voice**

* Professional, neutral, clear, direct

## **8.2 Writing Style**

* Simple, structured sentences

* Scannable content; no long paragraphs

## **8.3 Terminology Consistency**

| Category | Terms |
| :---- | :---- |
| Membership plans | Silver, Gold, Diamond, Dealer Program (exact spelling, never variants) |
| Plan codes | SILVER, GOLD, DIAMOND, DEALER |
| Customer-visible stages | Created, Received, Grading, Slabbing, QC, Imaging, Shipped, Ready for Pickup, Completed, On Hold |
| Result Types | Encapsulated, Details, Not Encapsulated, Rejected |
| Service tiers | Value, Standard, Express, Priority |
| Categories | Modern, Early Modern, Medieval, Medals & Tokens, High Value, Unlimited |
| Invoice types | Proforma Invoice, Sales Invoice, Membership Sales Invoice |
| Invoice statuses | Pending, Under Review, Paid, Cancelled |
| Support ticket types | General, Offer, Report Certificate, Guarantee Claim |

## **8.4 Language Requirements**

* Default language: English

* Arabic available as full alternative (RTL)

* Language switcher visible on every page

* Arabic content is a direct and accurate translation

* Terminology matches the ERP in both languages

# **9\. Phase 2 — Deferred Features**

These features are planned but excluded from Phase 1\. They are documented here so the architecture can accommodate them without rework.

## **9.1 Mobile Application**

Native iOS and Android app consuming the same Public API Layer. No separate backend.

* Account access

* Submission tracking

* Certification verification including NFC tap

* Registry management

## **9.2 Banknotes and Trading Cards**

* Listed as "Coming Soon" on Services in Phase 1

* Activation requires loading category-specific master data into the ERP

* Architecture absorbs these without redesign

## **9.3 Verify Warning Flags**

* Adds public\_warnings\[\] field to the Verify API response

* Supports: Possible Counterfeit Holder Reported, Reported Stolen, Mechanical Error on Label, Removed from Population

* Warnings display on top of a valid result card with appropriate severity styling

* Requires ERP-side field addition on Submission Item

## **9.4 Photograde — Visual Grading Reference**

* Curated reference image library across multiple series and grades

* Collectors compare raw coins to reference images to estimate grade

* Deferred until grading operations have produced enough reference imagery

## **9.5 Coin Explorer — Catalog Depth**

* Full catalog of every coin type with mintage, history, varieties, editorial commentary

* Multi-year content project; Population Report and Price Guide cover the basics in Phase 1

## **9.6 Cross-Service Stolen Items Database**

* Industry-wide stolen items database integrated with other grading services

* Relevant at industry scale; not for initial launch

## **9.7 Public Registry Leaderboard Marketing Surface**

Internal leaderboards visible to logged-in members are Phase 1\. The public-facing marketing surface deferred to Phase 2:

* Curated public showcase of top collections

* Top-collector profiles and editorial features

* Awards program (annual recognition, physical awards)

* Per-member opt-in privacy controls for public visibility

## **9.8 Full Peer-to-Peer Marketplace**

* Phase 1 implements Make an Offer through Support tickets

* Phase 2 may introduce a full marketplace with offer DocType, counter-offers, public offers feed per cert, payment handling, dispute resolution

## **9.9 Multi-Language Beyond EN/AR**

Architecture supports adding languages without structural changes.

# **10\. Deliverables Required from Developer**

## **10.1 Front-End Development**

* All website pages per this brief

* Responsive across desktop, tablet, mobile

* Bilingual EN/AR with RTL

## **10.2 Public API Integration**

* Verify (cert and NFC)

* Population (reference and search)

* Tracking

## **10.3 Authenticated API Integration**

* Authentication (OAuth2 / JWT)

* Submission (create, list, detail, cancel, quote)

* Membership (plans, subscribe, subscription, cancel, rewards, redeem)

* Support (tickets, messages) — including Offer, Report Certificate, Guarantee Claim ticket types

* Registry (browse public, manage member sets, leaderboards)

## **10.4 Price Guide Integration**

* Read-only integration with the Price Guide endpoint (contract to be confirmed with Eng. Mostafa)

## **10.5 Dashboard Implementation**

* Submissions, Membership, Invoices, Rewards, Registry, Support Tickets, Dealer View

* Access control

## **10.6 Forms**

* Contact, Submission, Membership signup, Support ticket, Make an Offer

* Validation and error handling

## **10.7 Content Pages**

* Grade Guarantee

* Security & Counterfeit Awareness

* Numismatic Glossary (with anchor index, schema.org markup)

* Holders & Labels Reference (with reference imagery)

* Authorized Dealer Program landing page

## **10.8 Content Management**

* News, Resources, Glossary, Authorized Dealers Directory, FAQs, Grade Guarantee content, Security center content editable through ERP or fixtures

## **10.9 File Management**

* Downloadable PDFs hosted securely

* Invoice PDFs proxied through the gateway

## **10.10 SEO & Performance Setup**

* Sitemap, robots.txt, canonical URLs, structured data

* Page speed optimization

## **10.11 Security**

* Secure auth and session handling

* HTTPS-only

* Secure API communication

## **10.12 Testing & QA**

* Functional testing of all features and all API states

* Cross-device and cross-browser testing

* All Result Types and Verify response codes tested

* Bilingual EN/AR parity testing

## **10.13 Deployment**

* Production deployment

* Domain configuration, SSL

## **10.14 Documentation**

* Website structure

* Admin usage

* API integration points and error handling

## **10.15 Post-Launch Support**

* Bug fixing

* Minor adjustments

# **11\. Final Notes**

* All requirements in this document must be followed accurately

* Suggestions and improvements are welcome and should be communicated before or during implementation

* All ERP/API integration must be coordinated with Eng. Mostafa Nazeer

* Brand identity is provided separately by IGA; the developer does not make brand or visual design decisions (§4)

* Design and UI/UX implementation are flexible — propose enhancements where they align with project direction, subject to approval

* Deliver a stable, functional, complete system

* Code quality and performance must meet professional standards

* All features must be tested before final delivery

* Final product must align with IGA’s positioning as a professional and trusted grading authority

* The Master Brief and Workbook are the authoritative source for any ERP-side question; this document defers to them in case of conflict

# **Appendix A — Page-to-API Cross-Reference**

| Page | Endpoint(s) | Auth |
| :---- | :---- | :---- |
| Home — Cert lookup | Routes to Verify | n/a |
| Home — News | CMS read or fixture | n/a |
| Services | Static \+ Service Master fixture | n/a |
| Pricing & Turnaround | GET /membership/plans; Service Master fixture; POST /submissions/quote (optional) | Mixed |
| Membership | Full Membership API | Mixed |
| Submit | POST /submissions; POST /submissions/quote | Member |
| Verify | GET /verify/{cert\_no}; POST /verify/nfc; POST /support/tickets (Offer, Report) | Public \+ member |
| Tracking | GET /tracking/{tracking\_id} | Public |
| Resources — Population | GET /population/reference/{ref\_code}; GET /population/search | Public |
| Price Guide | Custom Price Guide endpoint (TBD with Eng. Mostafa) | Public |
| Registry — Browse | GET /registry/categories, /sets, /sets/{code} | Public |
| Registry — My Collection | GET, POST, PUT /registry/my-sets; GET /registry/leaderboard/{code} | Member |
| News | CMS read or fixture | n/a |
| Contact | Form-to-email (no API) | n/a |
| Authorized Dealers Directory | CMS read or fixture | n/a |
| Authorized Dealer Program landing | Static \+ links to Membership signup | n/a |
| Grade Guarantee | Static content \+ POST /support/tickets (Guarantee Claim) | Member for claim |
| Security & Counterfeit Awareness | Static content | n/a |
| Numismatic Glossary | Static content (CMS or fixtures) | n/a |
| Holders & Labels Reference | Static content \+ imagery | n/a |
| Login / Sign Up | Auth endpoints (OAuth2) | n/a |
| Dashboard — Submissions | GET /submissions; GET /submissions/{no}; POST /submissions/{no}/cancel | Member |
| Dashboard — Membership | GET /membership/subscription | Member |
| Dashboard — Invoices | GET /submissions/{no}; invoice PDFs via gateway | Member |
| Dashboard — Rewards | GET /membership/rewards; POST /membership/rewards/redeem | Member |
| Dashboard — Registry | GET /registry/my-sets; POST /my-sets; PUT /my-sets/{no}/slots | Member |
| Dashboard — Support | GET, POST /support/tickets; GET /support/tickets/{no}; POST /support/tickets/{no}/messages | Member |
| Dashboard — Dealer View | GET /submissions (filtered) | Member (Dealer Program) |

# **Appendix B — Result Type and State Code Reference**

## **B.1 Result Types**

| Result Type | Public Verify? | Customer Sees |
| :---- | :---- | :---- |
| Encapsulated | Yes (once Shipped or Ready for Pickup) | Full certificate card: grade, designations, holder type, images |
| Details | Yes (once Shipped or Ready for Pickup) | Details certificate card: qualifying problem on label, no numeric grade |
| Not Encapsulated | No | Item returned; certificate kept internally, never on Verify |
| Rejected | No | Item returned with rejection notice; internal cert kept, never on Verify |

## **B.2 Verify API Response States**

| HTTP | State | Cause | UI |
| :---- | :---- | :---- | :---- |
| 200 | Verified | Encapsulated or Details; submission Shipped/Ready | Status: Certification Verified. Full card. |
| 404 | Not Found | Certificate does not exist | Status: No Record Found |
| 410 | Gone (Rejected) | Item was Rejected | Status: Certificate Not Available |
| 425 | Too Early | Submission not yet Shipped or Ready for Pickup | Status: Verification Not Yet Available — suggest Tracking |
| 429 | Rate Limited | Too many requests | Status: Please wait and try again |
| 401 | Invalid Signature | NFC tap signature failed | Status: NFC tag could not be verified |

## **B.3 Customer-Visible Submission Stages**

* Created

* Received

* Grading

* Slabbing

* QC

* Imaging

* Shipped (carrier delivery) — or — Ready for Pickup (counter collection)

* Completed

* On Hold (non-positional banner; reversible)

## **B.4 Invoice Statuses**

* Pending

* Under Review

* Paid

* Cancelled

## **B.5 Support Ticket Types**

* General

* Offer (created from Verify "Make an Offer" button; related\_certificate set)

* Report Certificate (created from Verify "Report Certificate" button)

* Guarantee Claim (created from Grade Guarantee page)