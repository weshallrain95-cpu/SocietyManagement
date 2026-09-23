# 01 — Business Requirements Document (BRD)

| Field | Value |
|-------|-------|
| Product | Only Broker (working name) |
| Version | 0.1 (draft for founder review) |
| Date | 2026-09-23 |
| Status | Draft |
| Launch geography | Mumbai Metropolitan Region (MMR) |
| Launch segment | Residential rentals (leave & licence); sales (new + resale) modelled from day one |

---

## 1. Executive summary

Residential real estate in Indian metros runs through brokers. In MMR most rental and resale
deals involve a local broker who holds three things:

- **inventory**: which flats are free, and on what terms
- **access**: keys, the owner's trust, society contacts
- **judgement**: which flat suits which customer

Their tools are memory, a phone contact list, WhatsApp groups and an Excel sheet.

Listing portals treat the broker as a paying advertiser at best and as a middleman to cut out at
worst. None of them give the broker an **operating system for the job**: capture the requirement,
match it to inventory, plan the site visits, dispatch staff, coordinate with owners and keep the
customer relationship.

**Only Broker** is that operating system. On top of it sits a marketplace that works like
ride-hailing:

1. A customer sends **one enquiry**, and it reaches **every relevant broker in that area** in real time.
2. Brokers **bid for the customer** with their terms, ratings and reviews.
3. The chosen broker runs the whole deal in the app, from matching and visits to owner confirmation
   and closure.
4. Everyone rates everyone (**360° reviews**).

As in ride-hailing, the customer is served but the **supply side (brokers) is the product**.

## 2. Problem statement

### 2.1 Worked example (from the founder's brief)

A broker has 500 flats in their records. A customer wants a **2 BHK on rent, at most ₹20k/month,
pets allowed, with a lift, near the station, with an auto stand nearby and a school close by**.

Today:

| Step | How it's done today | What goes wrong |
|------|---------------------|-----------------|
| Take the requirement | Phone call, memory | Details are lost; nothing is recorded |
| Shortlist | Memory + Excel | Misses good matches; relies on stale status |
| Share options | WhatsApp list of names and addresses | No map, photos or consistent details |
| Plan visits | In the broker's head: who goes, which keys, what order | Wasted trips, missing keys, owner not told |
| At the site | Customer reveals a constraint that rules out flats | Tour falls apart on the spot. The flats' house rules were never stated up front |
| After the deal | Status updated (maybe) in Excel | The same flat is offered again as available |

### 2.2 Problems by stakeholder

| Stakeholder | Core pain |
|-------------|-----------|
| **Customer** (tenant/buyer) | Has to call many brokers one by one; can't see what's available; can't compare brokers; tours are wasted on flats that were never suitable |
| **Broker** | No system of record; manual matching; visit logistics in their head; customer history lost; stale status; no way to show a good track record |
| **Owner / builder** | Can't find good local brokers; can't see what brokers do with the unit; status of the unit is misrepresented; no feedback loop |
| **Market as a whole** | No trusted master record of societies and units; duplicate and misspelled building names; conflicting claims about the same unit |

## 3. Vision and objectives

**Vision.** Every residential unit in urban India that is available to rent or buy is reachable
through a trusted local broker within minutes, backed by one accurate master record.

### 3.1 Business objectives (first 12 months after public launch)

| ID | Objective | Measure | Target (proposed; founder to confirm) |
|----|-----------|---------|------------------------------|
| BO-1 | Build broker supply in launch micro-markets | Verified brokers active weekly | 1,500 across the first 3 clusters |
| BO-2 | Build a trusted inventory base | Units with a confirmed status in the last 30 days | 60,000 |
| BO-3 | Fast marketplace response | Median time from enquiry to first broker response | < 5 minutes (07:00–22:00) |
| BO-4 | Conversion | Enquiries that lead to at least one completed site visit | ≥ 35% |
| BO-5 | Data quality | Duplicate society records in live data | < 0.5% |
| BO-6 | Status accuracy | "Available" units found already let when a visit happens | < 5% |
| BO-7 | Revenue | Paying brokers ÷ active brokers | ≥ 25% by month 12 |

## 4. Scope

### 4.1 In scope (programme)

- **Transaction types:** Rent (leave & licence), Sale – New (builder / under construction / ready),
  Sale – Resale.
- **Property types:** Apartments, row houses, independent houses and villas. Phase 1 is residential only.
- **Three role apps inside one mobile app**: Customer, Broker (including broker staff), Owner/Builder.
- **Desktop admin console** for platform operations, plus a desktop console for brokers who run
  offices with staff.
- **Master data**: societies, buildings and projects for MMR, from Badlapur to Vasai-Virar to
  Kalamboli/Ulwe to Panvel/Uran and all of Mumbai city and suburbs.
- **Bulk inventory upload** (Excel/CSV) with de-duplication and review.
- **Real-time enquiry broadcast**, broker responses (proposals), site-visit planning and assignment,
  owner notifications, customer book (CRM), 360° reviews.

### 4.2 Out of scope (programme, for now)

- Commercial and industrial property, plots and PGs/co-living. These are candidates for later phases.
- Payment of rent, deposits or brokerage through the platform (Phase 3 candidate).
- Home loans, legal due diligence and agreement registration. Partner integrations are Phase 3 candidates.
- Cities outside MMR (Pune is the first expansion candidate).

## 5. Stakeholders and user classes

| Class | Description | Primary surface |
|-------|-------------|-----------------|
| Customer | Individual looking to rent or buy | Mobile app (customer mode) |
| Broker (principal) | Licensed or registered agent or agency owner who holds inventory and customers | Mobile app (broker mode) + broker desktop console |
| Broker staff | Field executives employed by a broker; run site visits, hold keys | Mobile app (staff mode, limited permissions) |
| Owner | Individual owner of one or more units | Mobile app (owner mode) |
| Builder / developer | Sells new units in projects; may appoint channel-partner brokers | Owner mode (builder profile) + desktop console |
| Platform admin | Only Broker operations: verification, master data, disputes, moderation | Admin desktop console |
| Society office-bearer (later) | Confirms building data, may list society rules | Phase 3 |

## 6. Business model (proposal for founder decision)

The brief says the brokers are "the real deal". The model below therefore **charges brokers for
growth and tools** and keeps the platform **free for customers and owners**, so demand grows without
friction.

| Stream | Who pays | Mechanism | Phase |
|--------|----------|-----------|-------|
| Broker subscription (tiers) | Broker | Free: capped inventory, 1 user, limited leads/month. Pro: unlimited inventory, staff seats, visit planner, analytics. Agency: multiple offices | 1 |
| Lead credits | Broker | Credits to respond to enquiries above the free allowance. Priced by transaction type and budget band | 1 |
| Boosts | Broker | Priority placement in a micro-market's broker list for a time window. Clearly labelled "Promoted" | 2 |
| Builder campaigns | Builder | Project launch campaigns pushed to brokers active in that micro-market (channel-partner recruitment) | 2 |
| Value-added services | Any party | Agreement drafting, police-verification help, e-registration assistance, movers, home loans (referral fees) | 3 |

**Principle:** the platform **never charges brokerage** and never competes with brokers for the
deal. Brokerage stays between broker and client, off-platform. This is the clearest way to show
"broker-first".

## 7. Competitive positioning

| Player type | Examples | Their stance | Our difference |
|-------------|----------|--------------|----------------|
| Listing portals | 99acres, MagicBricks, Housing.com | Brokers pay to advertise listings; customers call many brokers | Enquiry goes to all local brokers at once; broker runs their whole business in the app |
| "No broker" platforms | NoBroker | Cut the broker out | The broker *is* the service |
| WhatsApp broker groups | Informal | Fast, but no structure, trust or privacy | Structured, private-by-default inventory with reputation |
| Broker CRMs | Various SaaS | Single-broker tool with no demand side | Tool + marketplace + shared master data |

## 8. Key business rules (non-negotiable)

1. **Inventory privacy.** A broker's inventory (their claim on a unit, their price, owner contact,
   keys, notes) is **never visible to another broker**. The customer-facing map shows only
   aggregate availability: counts, clusters and price bands.
2. **Many brokers, one unit.** Several brokers may claim the same physical unit. Each claim is separate
   and private; the unit's master record is shared.
3. **One unit, one master record.** Facts about a unit (BHK, carpet area, floor, amenities, location)
   are stored once and resolved from sources ranked by trust (see Data Model §6).
4. **Status is key.** A unit's status (Available / Under negotiation / Let / Sold / Off market) is
   the most valuable field. Some status changes need **owner confirmation**. Until the owner confirms,
   the status shows as *"Available — not yet confirmed by owner"*.
5. **Every unit has an exact map location** (a pin), inherited from its building and adjustable
   within limits.
6. **360° reviews.** Customer ↔ Broker ↔ Owner can review each other, but only after a verified
   interaction such as a completed visit or a closed deal.
7. **Conduct-based house rules only (see §10.2).** The platform never records or filters on who a
   person *is*, only on how a home will be *used*. Owner **house rules** based on conduct (pets, smoking, non-veg cooking on the premises, bachelors/family,
   occupancy limits) are recorded as **unit attributes shown up front**, so a tour doesn't fall apart
   when a mismatch surfaces at the site.

## 9. Success metrics (north star + guardrails)

- **North-star metric:** *Completed site visits per week* in live micro-markets. It captures real
  broker work being done through the platform.
- **Supply health:** weekly active brokers; median broker response time; share of enquiries with at
  least 3 broker responses.
- **Data health:** duplicate society rate; units with a confirmed status in the last 30 days; share
  of master fields with a verified or computed source.
- **Trust:** average rating by role; dispute rate; share of "available" units found unavailable at
  the visit.
- **Economics:** paid conversion; lead-credit burn per closed deal; churn of paying brokers.

## 10. Legal, regulatory and ethical considerations

> Not legal advice. Every item below needs review by Indian counsel before public launch.

### 10.1 Regulatory

| Area | Requirement | Product impact |
|------|-------------|----------------|
| **RERA (MahaRERA)** | Real estate agents dealing in RERA-registered projects must be registered with MahaRERA; builder projects carry RERA registration numbers | Capture and verify MahaRERA agent registration numbers; show a "RERA-registered" badge; store the project RERA number for new-sale inventory; restrict new-project sales listings to RERA-registered agents |
| **DPDP Act 2023 & DPDP Rules** | Consent, purpose limitation, data-principal rights, breach notification, children's data | Consent capture per purpose; privacy notice; export and delete flows; retention schedule; grievance officer; breach runbook |
| **IT Act 2000 / Intermediary Rules 2021** | Intermediary due diligence and grievance redressal | Terms of use, content takedown, grievance officer with published SLA |
| **Maharashtra Rent Control Act 1999 / Registration Act** | Leave & licence agreements must be registered in Maharashtra; stamp duty applies | Phase 3 e-registration partner; reminders in the deal-closure flow |
| **TRAI DLT (SMS)** | Registered sender IDs and templates for transactional SMS | OTP and notification templates registered via the SMS provider |
| **WhatsApp Business Policy** | Opt-in and approved templates | Opt-in at signup; template catalogue |
| **Consumer Protection (E-Commerce) Rules 2020** | Clear disclosures, no misleading claims | "Promoted" labels; truthful status labels; review integrity |
| **Data localisation (prudent)** | Keep personal data in India | Host in an India region (e.g. AWS ap-south-1 Mumbai) |

### 10.2 Conduct-based house rules (founder decision, 2026-09-23)

The brief describes a real situation: a tour falls apart at the site because something that
matters to the owner surfaces only then. The platform prevents this by **making every unit's house
rules explicit up front**:

- Owners (or brokers on their behalf) declare **conduct-based house rules** from an admin-curated
  catalogue: pets, smoking, non-veg cooking on premises, bachelors or families, maximum occupants,
  company lease, guests, home-office use.
- Customers state their **own needs** in the same terms, e.g. "I have a dog" or "we cook non-veg".
- Matching excludes clashes **before** the visit, so the tour is stable.
- **Platform vocabulary rule:** the product describes homes and how they are used, never the
  personal identity of the people using them. No form, filter, label, template or report uses
  identity terms. The house-rule catalogue is the only place occupancy conditions can be expressed,
  and moderation removes free-text remarks that try to set identity-based conditions.

This protects the platform legally (anti-discrimination principles, app-store content policies)
and reputationally, and still solves the broker's operational problem.

## 11. Assumptions

1. Brokers will upload inventory if (a) it stays private, (b) upload is painless (Excel as they
   already keep it), and (c) they get leads back.
2. Owners will confirm status via a one-tap WhatsApp/SMS link without installing the app.
3. Customers will send enquiries without calling if brokers respond within minutes.
4. Master data for societies can be seeded from public sources (MahaRERA project registry, municipal
   and planning-authority data where legally usable, OpenStreetMap, Google Places) plus broker uploads.
   Licensing terms must be checked for each source.

## 12. Risks and mitigations

| # | Risk | Likelihood | Impact | Mitigation |
|---|------|-----------|--------|-----------|
| R1 | Cold start: no brokers means no customers, and vice versa | High | High | Launch one micro-market at a time; the broker tool is useful alone (CRM + visit planner) before demand arrives; seed with broker associations |
| R2 | Brokers fear inventory leakage | High | High | Privacy by design (row-level security); visible privacy guarantees; aggregate-only public map |
| R3 | Low-quality or duplicate master data | High | High | Canonical registry, alias learning, admin review queue, computed facts (Data Model §5–6) |
| R4 | Stale statuses | High | High | Owner confirmation, automatic decay/re-confirmation, visit feedback loop |
| R5 | Spam enquiries and fake customers | Med | Med | OTP login, rate limits, customer trust score, lead-quality refunds |
| R6 | Brokers take customers off-platform | High | Med | Acceptable by design, since brokerage is off-platform anyway. Value comes from tools and reputation, not from gatekeeping |
| R7 | Rating manipulation | Med | Med | Reviews only after verified interactions; anomaly detection; one review per interaction |
| R8 | Discriminatory house-rule abuse | Med | High | Curated rule list, free-text moderation, reporting, policy enforcement (§10.2) |
| R9 | Map API costs grow with usage | Med | Med | Server-side caching; clustering; self-hosted OSM tiles for the admin console; budget alerts |
| R10 | Regulatory change (DPDP rules, RERA) | Med | Med | Compliance owner; configurable consent and retention |

## 13. Glossary

| Term | Meaning |
|------|---------|
| Leave & licence (L&L) | Standard Maharashtra residential rental instrument (typically 11 months) |
| Society / CHS | Co-operative housing society; the legal entity of a residential building/complex |
| Project | Builder development (may become one or more societies) |
| Micro-market | A locality cluster such as Thane-Dhokali, Powai or Kharghar |
| Unit | A single flat/house (the physical thing) |
| Listing / claim | One broker's private record of representing a unit |
| Enquiry | A customer's requirement broadcast to brokers |
| Proposal | A broker's response to an enquiry (terms, fee, ratings) |
| Visit plan | An ordered set of unit visits for a customer, with time slots, staff, keys |
| Master data | Canonical societies, buildings, units and their resolved attributes |
