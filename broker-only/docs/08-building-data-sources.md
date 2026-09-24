# 08 — Building data from official sources (TMC, MahaRERA, IGR)

_Researched 2026-09-24 for founder decision D18: "whatever we need to build has to come from our own
source", as much as possible online, not from brokers and not mainly from field surveys._

## What we need

For every wing in the pilot area: its **flat numbers**, the **floor** of each, and ideally the
**carpet area**. From a complete list of a wing's flats the system works out the rest: top floor, first
floor with flats, flats per floor, refuge floors and odd flats such as 2001A. After that, brokers can
only add flats that exist.

## Thane Municipal Corporation (TMC), property tax

| Question | Answer |
|---|---|
| Is there a public API? | **No.** TMC publishes no API or open data for the property register. The only open TMC data we found is ward boundaries (data.gov.in and OpenCity), not properties. |
| What is online? | Two payment portals, [propertytax.thanecity.gov.in](https://propertytax.thanecity.gov.in/) (desktop) and [myptax.thanecity.gov.in](https://myptax.thanecity.gov.in/) (mobile). You search **one property at a time**, by property number or by owner name plus ward, and see that property's bill. There is also a login-only survey site (`ptaxsurvey.thanecity.gov.in`) for TMC's own staff. |
| What does one bill show? | Property number, ward committee (prabhag samiti), block, building name, owner name, address, and taxes due. Area and usage are usually shown as well (to be confirmed on a real bill, founder to-do 3). |
| Can we download it all automatically? | **Not recommended.** It would mean scraping a payment site one property at a time, against its terms of use and probably behind captchas. It would also collect owner names, which is personal data under India's data-protection law (the DPDP Act). One complaint could shut the company's data pipeline and reputation down. |
| Could we check the portal ourselves? | Not from our build servers, whose network doesn't reach Indian government sites. The founder can open it from any phone in India. |

**The right way to get TMC's data** is to ask TMC for it formally. TMC already holds a register of
every assessed flat, and what we need from it is **not personal**: building, wing, flat number, floor,
carpet area, ward and property number, without owner names.

1. **A data-sharing request** to the Property Tax Department (Deputy Commissioner, Property Tax) with a
   copy to TMC's IT cell / Smart City office. Pitch: we help keep the register's building records clean,
   and we can report flats we find that are missing from the tax roll. A draft is below.
2. **A Right to Information (RTI) application** under Section 6 of the RTI Act 2005, ₹10 fee, to TMC's
   Public Information Officer (Property Tax). The information must be supplied within 30 days. By asking
   **without owner names**, we stay clear of the personal-information exemption in Section 8(1)(j).
   Start with one or two ward committees covering the pilot, for example Majiwada–Manpada, then extend
   ward by ward.

Whichever route works, the file goes straight into the system (see "What is built" below).

### Draft RTI application (edit the wards and dates before sending)

> To: The Public Information Officer, Property Tax Department, Thane Municipal Corporation,
> Panchpakhadi, Thane (W) 400602 _(check the current address on thanecity.gov.in)_
>
> Subject: Information under Section 6(1) of the Right to Information Act, 2005
>
> Please provide, in electronic form (Excel or CSV) if available, the following information for all
> residential properties assessed in the **Majiwada–Manpada** ward committee (prabhag samiti):
>
> 1. Property number, 2. Building / society name, 3. Wing, 4. Flat number, 5. Floor,
> 6. Carpet or assessed area, 7. Ward / block.
>
> **Owner names and any other personal details are not requested.** If the information is
> held in a different format, please provide it as held. The application fee of ₹10 is paid by
> [IPO / online / court-fee stamp].
>
> Name, address, phone, date, signature.

### Draft data-sharing letter (short version)

> Only Broker is a Thane-based platform that helps registered real-estate brokers keep accurate records
> of the flats they handle. We request a periodic extract of the property-tax register for residential
> buildings in Thane West, limited to building name, wing, flat number, floor, carpet area, ward and
> property number (no owner names or other personal data). We will use it only to validate building and
> flat records, and we are glad to share back any discrepancies we find (for example flats in use that
> do not appear in the register). We can meet at your convenience.

## MahaRERA

- Every project registered since 2017 has a public page at
  [maharera.maharashtra.gov.in](https://maharera.maharashtra.gov.in/) with **building / wing names,
  number of floors and number of apartments** (sometimes by type), plus the RERA number.
- There is no official bulk download or API. Pages can be read one project at a time. Third-party
  sites and datasets (e.g. on Kaggle) re-publish parts of it. Check the licence before using any of them.
- **Coverage gap:** buildings finished before 2017, which is most of Thane West's rental stock, are not
  on MahaRERA unless a later phase was registered.
- Use: newer towers. Load them with `import_building_layouts` (floors and flats per floor), or with
  `import_flat_register --source rera` when a flat list is available.

## IGR Maharashtra (property registrations)

- Every registered sale or leave-and-licence agreement has an "Index-II" entry: the property's
  building, flat number and area. Free e-search is **one record at a time, behind a captcha**.
- It gives only flats that were ever registered, so a partial list. Useful to fill gaps in a wing.
  Load it with `--source igr --partial`.
- Paid data companies aggregate IGR records at scale. That is an option if the TMC route is slow.
  Budget and licence terms need a decision.

## What is built (ready for any of the above)

| Piece | Where |
|---|---|
| Official flat list per wing (`RegisterFlat`): flat number, floor, carpet area, source (TMC / MahaRERA / IGR / ops), source reference, ward. **Owner names are never stored**: other columns in the file are ignored. | `apps/masterdata/models.py`, `registers.py` |
| The layout of each wing is worked out from its list (top floor, first floor with flats, flats per floor, refuge floors, odd flats) | `registers.derive_layout` |
| A **complete** list is the last word: a broker (or owner) cannot add a flat number that isn't on it | `layout.check_unit` → "Flat 705 is not in the TMC property tax list of flats in Rodas A." |
| Upload from the ops console (check first, then save), or from the command line | `/ops/registers`, `python manage.py import_flat_register file.xlsx --source tmc` |
| Spreadsheet template (English or Marathi headings accepted) | `tools/building-layouts/flat-register-template.xlsx` |
| **The building as a picture**: every wing, floor by floor, in the app (from any flat page: "See the building, floor by floor") and in the ops console. The broker's own flats are marked; no other broker's inventory is ever shown | App `society/[id]`, API `GET /v1/societies/<id>/structure` |

## Founder to-dos

1. Send the RTI application for one pilot ward. It costs ₹10 and the reply is due within 30 days.
2. In parallel, send the data-sharing letter (or ask a contact at TMC).
3. Share one real TMC property-tax bill (any flat, owner name hidden) so we can match the exact field
   names and property-number format.
4. Decide whether to spend on a paid IGR/RERA data company if TMC is slow (decision D19, open).
