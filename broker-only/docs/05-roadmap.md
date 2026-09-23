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
| D11 | Unit Attribute Dictionary v0.1 | Pending founder approval (spreadsheet circulated 2026-09-23) | Drives forms, uploads, matching |
| D6 | House-rule catalogue content | Conduct-based only (BRD §10.2) | Legal and platform-policy exposure |
| D7 | Mobile stack | React Native (Expo) | One team for mobile + web |
| D8 | Hosting | AWS ap-south-1 | Data residency; managed PostGIS |
| D9 | Master-data sources and licences | MahaRERA + OSM first; evaluate paid data vendors | Data quality and legal use |
| D10 | Repository | Keep `broker-only/` in this repo on its own branch for now; move to a **dedicated repository** before Phase 1 code grows | Clean history and permissions; CI separation |

## 6. Immediate next steps

1. Founder reviews docs 01–05 and answers D1–D10.
2. Phase 0 scaffold: `broker-only/backend`, `broker-only/web`, `broker-only/mobile`,
   `broker-only/infra/compose/docker-compose.dev.yml`, `Makefile` (`make up`, `make seed`,
   `make test`), CI workflow with path filters.
3. Compile the Thane West seed list (societies + aliases) with the pilot brokers.
4. Register DLT sender ID/templates and the WhatsApp Business account (lead time 1–3 weeks).
