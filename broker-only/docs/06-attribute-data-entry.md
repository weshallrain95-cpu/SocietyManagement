# 06 — Making the Attribute Dictionary Manageable

The Unit Attribute Dictionary (draft v0.1, 200 attributes) is deliberately complete. It is the
**vocabulary** of the platform: everything a unit *can* say about itself. It is **not** a form that
anyone fills in. This document explains how 200 attributes turn into a few taps for each of the
three user groups (brokers, owners, customers), without dropping any attribute.

**Target:** a broker adds a rental flat in an already-known building in **under 90 seconds / about
10 taps**. An owner answers **at most 10 questions** from a WhatsApp link. A customer's enquiry
form fits **on one phone screen**.

---

## 1. Seven rules that shrink the list

### Rule 1. Nobody types what the system can compute (33 attributes)
Distances to the station, metro, bus stop, auto stand, schools, hospitals and markets; walk and
auto times; floor band; age band; price per sq ft; deposit in months; photo counts; freshness
signals. These are **system** attributes, calculated from the map pin and other data. No form
ever shows them as inputs.

### Rule 2. Enter once per building, not once per flat (91 attributes)
53 attributes live on the **building** (lift, power backup, water supply, OC, redevelopment
status…) and 38 on the **society** (amenities, pet policy, tenant rules, loan-approved banks…).
They are captured **once**, by the first broker or admin who knows them. After that every flat in
that building shows them already filled. The broker only confirms or corrects ("still true?").

In a Thane West complex with 400 flats, the gym, pool, lifts and society rules are entered one
time, not 400 times.

### Rule 3. Three tiers, and only the first is ever required

| Tier | How it's derived from the dictionary | Count (v0.1) | Behaviour |
|------|--------------------------------------|--------------|-----------|
| **Essential** | MVP = Y **and** Matching = Hard | 17 | Asked when the listing is created. Can't be skipped, but "Don't know yet" is a valid answer for house rules (the owner is asked instead, rule 4) |
| **Recommended** | MVP = Y, not Hard | 43 | Shown as a short "improve this listing" checklist after saving; nudged by the completeness score |
| **Detailed** | MVP = N | 107 | Never asked. Available under "More details" in each category, plus Excel upload and owner edits |
| **System** | Authority = computed | 33 | Never asked (rule 1) |

The tier is **derived from columns you already approve** in the spreadsheet (MVP, Matching,
Authority), so the approved list directly decides the forms, with no separate configuration.
After launch the admin console can move an attribute between tiers (rule 7).

For a **rental** listing, the broker's essential questions are: property type, BHK, furnishing
level, covered parking, rent, available-from date, plus unit number and floor. The lift and the
society pet policy come from the building (rule 2). The house rules (pets, non-veg cooking,
bachelors/family, maximum occupants, company lease, smoking) are asked of the **owner** (rule 4)
unless the broker already knows them.

### Rule 4. Ask the person who actually knows

| Who | What they are asked | What they are never asked |
|-----|---------------------|---------------------------|
| **Broker** (listing) | Core configuration, rent/price and terms, parking, key custody | Computed facts; building facts already on file |
| **Owner** (WhatsApp link or app) | House rules, furnishing preset, expected rent/deposit, available-from, maintenance | Anything about the building that is already known; broker terms |
| **Field staff** (at a visit) | A **5-item verification checklist** for the flat they are standing in (e.g. "Gas stove present? Kitchen cabinets? Lift working? Photos taken?"), chosen from attributes that are missing or disputed | Anything already verified recently |
| **Customer** (after a visit) | "Was anything different from the listing?" One tap; details only if they say yes | Everything else |
| **Admin / data team** | Building and society facts in bulk (seed data), disputes | — |

The house-rule questions go to the owner first because the owner is **authoritative** for them
(Authority = owner). A broker's answer is used until the owner confirms.

### Rule 5. Defaults, presets and copying beat blank forms
- **Copy from a sibling flat:** "Same as 1103?" In Indian towers, flats in the same stack (x03 on
  every floor) almost always share configuration, carpet area and facing. Copying one flat fills
  about 15 attributes in one tap. Only floor-specific things (floor number, view) stay open.
- **Project templates:** for new-sale inventory, builders define unit types once (e.g. "2 BHK Type
  A, 680 sq ft carpet") and units inherit them.
- **Furnishing presets:** choosing *Semi-furnished* pre-ticks the usual items (fans, lights,
  wardrobes, kitchen cabinets, geysers). The 27 furnishing items become an **edit-the-exceptions**
  checklist, not 27 questions.
- **Smart defaults for the micro-market:** licence period 11 months, escalation 5%, notice 1 month,
  agreement cost 50-50. They are shown pre-filled and editable, never silently assumed in matching.

### Rule 6. Capture in the way people already work
- **Chips and toggles, not text boxes.** Every enum and yes/no is a tap. Numbers use steppers.
  There is no free text except notes.
- **One screen per category** with a progress ring. The broker can stop at any time; nothing is lost.
- **Excel upload uses only the columns the broker already has.** The mapping wizard recognises
  common headers ("Rent", "Dep", "Furn", "Pets"); unmapped columns go into notes. An upload never
  needs 200 columns. The template ships with the essentials plus about 10 popular optional columns.
- **Voice note → structured fields (Phase 2):** the broker speaks "2 BHK, semi-furnished, 28
  thousand, pets okay, available 1st November". The app proposes the fields and the broker
  confirms them with a tap.
- **Photos first:** the app asks for photos in a guided order (hall, kitchen, bedrooms, bathrooms,
  view, building). From Phase 2, image recognition *suggests* furnishing items for a human to
  confirm.

### Rule 7. "Unknown" is a valid answer, and the system handles it
- Every attribute can be *unknown*. Unknown **never excludes** a flat in matching. It lowers the
  match score slightly and appears in the match explanation as "≈ not confirmed" (MATCH-02/03).
- A **listing completeness score** (weighted by how often customers ask for each attribute) is shown
  to the broker with the top 3 missing items. Better-completed listings rank higher in matches and
  on shared shortlists, so completing them is in the broker's own interest.
- **Usage analytics drive the tiers:** every month the admin dashboard shows which attributes
  customers use as must-haves and which are never used. Attributes customers use often move up to
  Recommended; ones nobody uses move down. The dictionary stays complete, and the forms stay small.

## 2. What each user actually sees

### Broker: "Add flat" (rental, known building)
1. Search society → pick building/wing (auto-suggested from the society search).
2. Flat number → floor auto-derived ("1203" → 12th floor). **"Same as 1103?"** offered if a
   sibling exists.
3. BHK chips · Property type (pre-selected *Apartment*) · Furnishing chips (preset ticks items).
4. Rent · Deposit (pre-filled at 3 months, editable) · Available from (date chips: *Now*, *1st of
   next month*, *Pick date*).
5. Covered parking stepper · Keys: *with me / with owner / at office / society office*.
6. House rules: **"Ask owner"** (default: sends the owner link) or answer now.
7. Save → "Improve this listing" checklist (Recommended tier) + photo capture.

### Owner: WhatsApp link (no app needed)
A single page with at most 10 questions, each a tap: pets, non-veg cooking, bachelors or family,
maximum occupants, company lease, smoking, furnishing preset (edit exceptions), expected rent,
deposit, available from. Every answer is recorded as an *owner-verified* observation, which wins
over broker reports (Data Model §6).

### Customer: enquiry and results
- **Enquiry form:** transaction type, BHK, budget, area on the map, move-in date, and then **"Must
  haves"** as a chip picker showing the **12 most-requested chips** for that micro-market (pets,
  lift, covered parking, gas pipeline, furnished, near station, near school, gym, 24-hour water,
  power backup, non-veg cooking, family/bachelors). A search box reaches all other attributes whose
  Matching is Hard or Soft. The customer never scrolls a list of 200.
- **Unit card:** 5–6 **highlights** chosen automatically (the attributes this customer asked for
  first, then the unit's strongest features), computed distances ("650 m · 8 min walk to Thane
  station"), and a collapsed "All details" section grouped by the 13 categories. Empty and unknown
  attributes are hidden, not shown as blanks.

## 3. How this maps to the build

| Mechanism | Where it lives |
|-----------|----------------|
| Tier derived from MVP / Matching / Authority | `AttributeDef.entry_tier` (set by the dictionary loader), overridable by admin |
| Who is asked | `AttributeDef.asked_of` (derived: owner-authority → owner; building/society scope → building form; computed → nobody) |
| Enter once per building | `scope = building / society` observations, inherited by units at read time |
| Sibling copy | `POST /listings/{id}/copy-attributes?from_unit=` (Sprint S2) |
| Presets & defaults | `AttributeDef.presets` / micro-market config (Sprint S2) |
| Unknown handling & explanations | Matching engine (Sprint S4) |
| Completeness score | Computed on listing save; weights from enquiry must-have frequency |
| Usage analytics | `enquiry_created` must-have counts per attribute (PRD §8) → admin dashboard |

## 4. What this means for your review of the spreadsheet

- You don't need to trim the list for usability. Usability comes from the tiers and the rules
  above.
- What matters most in your review is the **MVP** column (it decides the Essential and Recommended
  tiers) and the **Matching** column (Hard attributes can exclude flats and become customer
  must-have chips).
- Following the platform vocabulary rule (BRD §10.2), the *Bachelors / singles* rule will offer only
  **allowed / not allowed**, and occupancy conditions are expressed only through the conduct-based
  house rules. This change is applied in dictionary v0.2 together with your decisions.
