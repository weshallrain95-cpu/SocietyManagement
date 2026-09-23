# Only Broker — product workspace

**Only Broker** is a broker-first real-estate marketplace for India's metro markets, starting with the
Mumbai Metropolitan Region (MMR). Most portals (99acres, MagicBricks, Housing, NoBroker) are built
around listings, or around cutting the broker out. This one does the opposite. It works like a
ride-hailing app with **the broker as the driver**:

- **Customers** (tenants or buyers) see nearby inventory and online brokers on a map. They send one
  enquiry and every relevant broker gets it at once.
- **Brokers** answer with their terms and ratings, auto-match the enquiry against *their own* inventory,
  plan and assign site visits, and keep their customer book.
- **Owners and builders** find and invite brokers, confirm availability, and rate the brokers who
  worked on their unit.

The first focus is **rentals** (leave & licence). **Sales**, both new and resale, are in the data
model from day one.

> This folder is a **new, standalone product**. It is unrelated to the Society Management app in
> the rest of this repository and does not import from or change it. It lives on its own branch so
> existing branches stay clean.

## Documents

| # | Document | What it answers |
|---|----------|-----------------|
| 01 | [Business Requirements (BRD)](docs/01-BRD.md) | Why build it, for whom, how it makes money, how we'll know it works, risks and compliance |
| 02 | [Product Requirements (PRD)](docs/02-PRD.md) | Personas, journeys, numbered functional requirements with acceptance criteria, NFRs, MVP cut |
| 03 | [Data Model](docs/03-data-model.md) | Entities, ERD, table specs, unit status state machine, society de-duplication, one-unit-one-truth resolution |
| 04 | [Architecture & Infrastructure](docs/04-architecture.md) | Stack, components, real-time broadcast, APIs, security, laptop dev server, production deployment |
| 05 | [Roadmap & Delivery Plan](docs/05-roadmap.md) | Phases, sprint plan, open decisions needing the founder's call |
| 06 | [Making the Attribute Dictionary Manageable](docs/06-attribute-data-entry.md) | How 200 attributes become ~10 taps for brokers, ≤ 10 questions for owners and one screen for customers |
| 07 | [Laptop Dev Server: Setup & Runbook](docs/07-dev-setup.md) | How to run everything on your laptop, connect phones, and what has been verified |

## Code

| Path | What |
|------|------|
| `backend/` | Django 5 + GeoDjango/PostGIS API, Channels (WebSocket), Celery. Apps: identity, orgs, audit, masterdata, status, inventory, crm, matching, visits, marketplace, reviews |
| `backend/tests/` | 109 tests: isolation between brokers (RLS), de-duplication, resolver, status rules, matching, visits and offline sync, marketplace, uploads, HTTP journeys, WebSocket |
| `mobile/` | Expo (React Native) broker + field-staff app for Android, iOS and web, with an offline mode and an in-app demo |
| `infra/` | Database bootstrap SQL, Dockerfile, Docker Compose for the laptop |
| `Makefile` | `make up`, `make seed`, `make test`, … (see docs/07) |

Quick start: `cd broker-only && make up && make seed`, then open <http://localhost:8000/v1/docs>.

## Source

The documents above build on the founder's brief *"Only Broker — Scope and Detailing"*. Each point
in that brief traces to at least one requirement ID in the PRD (see PRD §9, *Traceability*).
