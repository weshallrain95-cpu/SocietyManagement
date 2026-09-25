# 05 — Roadmap & Delivery Plan

## 1. Phases

| Phase | Name | Duration (indicative) | Outcome |
|-------|------|----------------------|---------|
| 0 | **Foundations** | 2 weeks | Repo scaffold, Docker dev stack on the laptop, CI, auth, RLS framework, audit chain, seed data for Thane West |
| 1a | **Broker OS** | 6 weeks | Brokers can run their business alone: master data + dedupe, listings + upload, status engine, CRM, matching, visit plans, staff |
| 1b | **Marketplace pilot** | 4 weeks | Customer map, enquiry broadcast, proposals, reviews (C↔B), owner confirmation links; pilot with ~100 Thane West brokers on staging |
| 2 | **Public launch (MMR phase 1)** | 8–10 weeks | Owner app, payments + credits, masked calling, chat, public unit cards, dispatch board, Hindi/Marathi, production hardening (99.9%); add micro-markets: Navi Mumbai (Kharghar, Ulwe, Panvel), Powai/Andheri, Kalyan-Dombivli |
| 3 | **Scale & ecosystem** | ongoing | Builder module, society integration, value-added services (agreements, e-registration, loans), ML ranking, Pune expansion |

Building the Broker OS before the marketplace is deliberate. The broker tool is useful **without
any customers**, which solves the cold-start problem (BRD R1). Brokers load inventory for their
own benefit, and that inventory later feeds the marketplace.

## 2. Sprint plan (2-week sprints)

| Sprint | Backend | Mobile / Web | Exit demo |
|--------|---------|--------------|-----------|
| S0 (Phase 0) | Compose stack, Django project, identity + OTP (console provider in dev), RLS middleware + test harness, outbox, audit chain, CI | Expo shell with role switcher; Next.js admin shell with login | Log in on phone against the laptop; cross-tenant test suite green |
| S1 | Master data models, seed import (localities, societies, POIs), `normalise_name`, society search, location-fact computation | Society search + map picker; admin master-data workbench v1 | Search "hira nandani" → correct society; unit shows "650 m to station" |
| S2 | Listings, keys, attribute dictionary + observations + resolver, status engine + ledger + owner confirmation link | Add-listing flow, inventory list/map, owner confirmation web page | Broker adds 10 units; LET → AVAILABLE needs owner YES via link |
| S3 | Excel upload pipeline + resolution queue, provisional societies, merge | Upload wizard (desktop), resolution UI, admin merge | Upload of 500 messy rows ≥ 80% auto-matched; admin merges duplicates |
| S4 | CRM, requirements, **offline customers (quick capture, consent without app, interaction log)**, matching engine with explanations | Customer book, requirement form, match results | Riya's requirement → ranked matches with ✔/✖ reasons |
| S5 | Visit plans, **shortlist/visit share links**, **offline sync API**, route optimisation, staff assignment, owner visit notice, live updates (WS), outcomes | Plan builder, share link, staff itinerary, check-in/outcome | Full tour: plan → share → assign → live reorder → outcomes |
| S6 | Presence, map aggregates (H3), enquiry + broadcast + proposals, entitlements | Customer map, enquiry composer, broker alert + proposal, customer proposal list | Enquiry "beeps" on 5 broker phones in < 3 s |
| S7 | Reviews + reputation, notifications (FCM, WhatsApp, SMS), anti-spam, DPDP desk | Reviews UI, notification preferences, admin queues | End-to-end pilot script passes on staging |
| S8 | Hardening: load test (k6), security review, pen-test fixes, runbooks, staging → pilot | Polish, crash-free ≥ 99.5% | Pilot go-live in Thane West |

## 2a. Progress (2026-09-23)

The **backend** for S0–S7 is built and tested (105 automated tests), ahead of the sprint plan
because it was built in one push:

| Area | Status |
|------|--------|
| Foundations: OTP auth, roles, RLS isolation, outbox, hash-chained audit, CI workflow, laptop Docker stack | ✅ Done |
| Master data: Thane West seed, normalisation, de-duplication, aliases, merge, location facts, attribute resolver | ✅ Done (seed coordinates approximate, to be verified with the pilot broker) |
| Inventory: listings, keys, status engine with owner links, Excel/CSV upload with review | ✅ Done |
| CRM incl. **offline customers** (consent without app, shortlist/visit links, interaction log, profile claim) | ✅ Done |
| Matching with explanations; visit plans, routing, staff dispatch, offline sync | ✅ Done |
| Marketplace: enquiry broadcast, proposals, presence, anonymous map, WebSocket; reviews (incl. offline) | ✅ Done |
| Real SMS/WhatsApp providers, Google Routes API, payments | ⏳ Needs accounts (DLT, WhatsApp Business, Google Cloud, Razorpay) |
| **Broker mobile app (Expo)**: Today, Leads, Customers (incl. offline), Flats, Add flat, Match, Visit plans, Field staff offline mode, live alerts, demo mode | ✅ Done — tested end to end against the real server |
| **Owner/customer link pages**: availability check, visit notice, shortlist, visit plan, consent, review | ✅ Done — server-rendered, tested in a real browser |
| **Ops (admin) console** at `/ops/`: broker verification, review queue (new societies: approve / merge / reject), society pins (paste a Google Maps link or drag the pin) and names, whole-area pin map, tamper check | ✅ Done |
| **Pin-check page for the pilot broker** (online link; answers applied with `apply_pin_review`) | ✅ Done |
| **Building layouts and flat-number checks** (MD-13): wing picker in the app, live check as the broker types, uploads refuse impossible flats, ops edits layouts, spreadsheet import + template for MahaRERA / field-survey data | ✅ Done |
| **Pick flats yourself** (VISIT-01a): society + flat-number search on visit plans, matching and customer pages, so staff can plan tours their usual way while they learn to trust matching | ✅ Done |
| **Owners module**: owner mode in the app — add my flat with proof, photos & walkthrough videos, preferred terms and house rules, brokers near my flat, invite with the "Allow this broker to handle my property" tick, read-only status "currently serviced by … · number · review", untick to remove a broker; broker side: invitation inbox, owner-appointed badge, owner photos, "owner removed you" with ask-to-be-added-back | ✅ Done |
| **Shared flat media with owner approval** (D15) and **broadcasts to own customers** (D16): brokers add photos/video from the flat page, owners approve; "Update my customers" composer with reach and WhatsApp invites for customers not on the app; customer mode with an Updates inbox and per-broker "stop updates" | ✅ Done |
| **Co-broking** (D17): each broker's private list of fellow brokers (import from Excel / phone contacts / paste), blast ready flats or a customer's requirement to fellow brokers in and around the flat (distance widened, everyone, or ticked names), trade inbox with "I have a customer / I have a flat" replies, WhatsApp for brokers not on the app | ✅ Done |
| **Customer list import** (CRM-11) and **several flats in one customer update** | ✅ Done |
| **Official flat registers** (D18): TMC property-tax / MahaRERA / IGR flat lists → wing layouts worked out automatically, flats outside a complete list refused, owner names never stored; ops upload page and template; **building picture** floor by floor in the app and ops console | ✅ Done — waiting on the data itself (docs/08) |
| **Flats at scale + new flat page** (INV-10/11, approved design): one search box (society, flat no., owner name or phone), filters, quick views, browse by society; the full flat page with a customer view | ✅ Done |
| **Customer marketplace screens** (MKT-01/03/07/08/09): "Find a flat" (flats available now and price ranges per area, brokers online — counts only), post a requirement, offers from brokers best first, accept up to 3, found a flat / cancel | ✅ Done 2026-09-25 — design not yet reviewed by the founder |
| **Broker team roles** (founder decisions 2026-09-25): entry screen "I'm a broker / I own a flat / I'm looking for a flat"; one Admin per agency; managers run the day, with uploads, blasts and adding field staff only when the Admin switches them on (off by default); trip allocation never waits (the Admin is told and can reassign); field staff see their trips and add walk-in customers; one phone number = one agency; switch mode from Account | ✅ Done 2026-09-25 |
| Broker desktop (Next.js) | Later — the app's web build covers it for now |
| Attribute dictionary v1.0 | ✅ Approved and committed |


## 2b. Development notes for the next cycle

- **Second Admin and Admin handover** (founder, 2026-09-25: next cycle). Today each agency has exactly one
  Admin (the person who registered it) and the Admin cannot be removed. Next: an optional co-Admin, and
  handing the Admin role to another member with an OTP confirmation from both phones; if the Admin's phone
  is lost with no co-Admin, ops restores access after checking RERA / ID documents. Touches
  `orgs.Membership`, `StaffRemoveView`, the Team section, the ops console and audit.
- **"Admin must approve trips first"** as an optional agency setting (today trip allocation never waits; the
  Admin is told and can reassign).
- **Flat Excel upload in the app** (today uploads run through the API; the app has the customer-list import).
- **Pricing model** (decision D2): per agency with unlimited logins, or by number of logins — see the
  founder discussion of 2026-09-25.

## 3. Definition of done (every story)

- Acceptance criteria from the PRD met, with automated tests (unit + API; RLS tests for private data).
- OpenAPI updated; generated TypeScript client regenerated.
- Audit/ledger entries for state-changing domain actions.
- No PII in logs or analytics; new PII fields encrypted.
- Feature flag per micro-market where relevant.
- Docs updated (this folder).

## 4. Team (suggested minimum)

| Role | Count | Notes |
|------|-------|-------|
| Founder / product owner | 1 | Owns priorities, broker relationships, pilot |
| Full-stack backend (Django/PostGIS) | 1–2 | Claude Code can pair on implementation |
| Mobile (React Native) | 1 | |
| Web (Next.js) | 0.5–1 | Can be shared with mobile via TypeScript skills |
| Ops / master-data associate | 1 | Verification, society merges, broker onboarding in the pilot |
| Legal counsel (fractional) | — | DPDP, RERA, T&Cs, broker agreement |

## 5. Decisions needed from the founder

| # | Decision | Recommendation | Why it matters |
|---|----------|----------------|----------------|
| D1 | Final product name and domain | Keep "Only Broker" as the working name; check the trademark before public launch | Branding, app-store listing, DLT sender ID |
| D2 | Monetisation at pilot | Free for the pilot; introduce plans and credits at public launch | Adoption vs. early revenue signal |
| D3 | Pilot micro-market | ✅ **Decided 2026-09-23: Thane West**; a pilot broker is already engaged | Seeding effort is per micro-market |
| D4 | Number of proposals a customer can accept | 3 | Balance between customer choice and broker lead value |
| D5 | Rules for broker consensus without an owner | 2 independent brokers within 7 days | Status accuracy vs. speed |
| D11 | Unit Attribute Dictionary | ✅ **Approved 2026-09-23 as v1.0** (200 attributes, tiers per docs/06); committed as `attribute_dictionary.yaml` | Drives forms, uploads, matching |
| D6 | House-rule catalogue content | Conduct-based only (BRD §10.2) | Legal and platform-policy exposure |
| D7 | Mobile stack | React Native (Expo) | One team for mobile + web |
| D8 | Hosting | AWS ap-south-1 | Data residency; managed PostGIS |
| D9 | Master-data sources and licences | MahaRERA + OSM first; evaluate paid data vendors | Data quality and legal use |
| D12 | Who may create buildings | ✅ **Decided 2026-09-24: closed universe.** Brokers and owners pick from our wings; a new name is only a request that ops approves (MD-04, MD-13) | Upload quality: typos become matches, not duplicates |
| D13 | Who puts flats into a broker's inventory | ✅ **Decided 2026-09-24.** (A) Only the broker, manually, in any scenario; the platform never offers a flat outside the broker's inventory. When an owner chooses a broker, the owner first ticks "Allow this broker to handle my property". (B) Owners don't police who lists their flat; they see a read-only status: "Currently serviced by XYZ · contact number · review". (C) When one broker reports a flat rented/sold, other brokers holding it get an anonymous alert (STAT-02) | Keeps each broker's inventory theirs alone; protects owners without extra work for them |
| D14 | Owner rules | ✅ **Decided 2026-09-24.** Owners upload a proof document when registering; nobody checks it (a deterrent, not a gate). Owner photos/videos go to every broker holding the flat and, as an available feature, on customer links. An owner can untick any broker (invited or self-added); that broker loses the flat and can ask to be added back — the owner's decision is final | Keeps owners in control without adding ops work |
| D15 | Flat photos & videos | ✅ **Decided 2026-09-24.** Shared per flat: max 5 photos + 1 video live; owner and the flat's brokers upload, customers never; the owner approves every broker upload before it goes live | One good set of media per flat, owner in control |
| D16 | Broadcasts | ✅ **Decided 2026-09-24.** Brokers message their own customers (new flat, price drop, news); in-app first; all of the broker's customers; free in the pilot, credits later | The customer list is the broker's second asset; broadcasts pull offline customers onto the platform |
| D17 | Co-broking (selling ready inventory through fellow brokers) | ✅ **Decided 2026-09-24.** Each broker keeps their own list of fellow brokers (with office areas) and keeps adding to it. Blasts go to brokers in and around the selected flat's location; the broker can widen the distance, send to everyone, or tick names. No commission terms in the message. No owner permission needed (a trade agreement between brokers). "Ask fellow brokers for a flat" (requirement blast) included as a good-to-have. Trade-level details only; the platform never moves a flat into another broker's inventory | Covers the two ways of moving ready inventory the pilot lacked: fellow brokers (A) and a blast to the whole customer list (C) |
| D18 | Where building structure comes from | ✅ **Decided 2026-09-24.** Only from our own sources — official records (TMC property-tax register, MahaRERA, IGR) — never from brokers (fragmentary). Online sources first; field surveys only to fill gaps. TMC has no public API: request the register formally (RTI / data-sharing letter), see docs/08 | One correct list of flats per wing; nothing to clean up later |
| D19 | Paid building-data company if TMC is slow | Open — founder to decide after the RTI reply | Coverage vs cost |
| D10 | Repository | Keep `broker-only/` in this repo on its own branch for now; move to a **dedicated repository** before Phase 1 code grows | Clean history and permissions; CI separation |

## 6. Immediate next steps

1. Founder: answer D1, D2, D4, D5, D7–D10 when convenient (none of them block engineering today).
2. Founder + pilot broker: run the laptop stack (docs/07), check the Thane West society list and pins,
   and add the broker's real society names and nicknames (they become aliases).
3. Start the account registrations with long lead times: DLT sender ID + templates, WhatsApp Business,
   Google Cloud (Maps/Places/Routes), MahaRERA agent verification process.
4. Data (D18): send the TMC RTI / data-sharing request for the pilot wards (drafts in docs/08); load
   MahaRERA details for newer towers; load each official flat list at `/ops/registers`.
5. Engineering next: put the backend on a staging server so the pilot broker can use the real app
   (not just the demo); then real SMS/WhatsApp once the accounts exist.
