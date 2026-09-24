"""Building structure from official flat lists (founder decision D18).

Wings, floors and flat numbers come from our own sources: the TMC property-tax register (one entry per
assessed flat), MahaRERA building details and IGR registrations. Never from brokers, whose lists are
fragmentary. From a complete list of a wing's flats we work out the layout: top floor, first floor with
flats, flats per floor, refuge floors with none, and the odd flats outside the pattern.

Owner names and other personal columns in a source file are never read, let alone stored.
"""

from collections import Counter
from dataclasses import dataclass, field
from decimal import Decimal, InvalidOperation

from django.db import transaction

from apps.audit.services import audit

from . import dedupe
from .layout import layout_dict
from .models import Building, RegisterFlat, Society
from .normalise import normalise_unit_no
from .services import get_or_create_building

COLUMNS = {
    "society": ("society", "society name", "building name", "project", "project name", "sosayati", "इमारतीचे नाव"),
    "wing": ("wing", "building", "tower", "wing / building", "bldg", "wing no"),
    "unit_no": ("flat", "flat no", "flat number", "unit", "unit no", "unit number", "sadnika kr", "सदनिका क्र", "room no"),
    "floor": ("floor", "floor no", "majla", "मजला"),
    "carpet_sqft": ("carpet area", "carpet", "area", "area sqft", "carpet area sqft", "built up area"),
    "source_ref": ("property no", "property number", "property code", "ptn", "malmatta kr", "मालमत्ता क्र", "rera no"),
    "ward": ("ward", "prabhag", "prabhag samiti", "zone", "block"),
}


@dataclass
class DerivedLayout:
    floors_total: int | None
    lowest_floor: int
    units_per_floor: int | None
    skip_floors: list[int]
    extra_unit_nos: list[str]
    flats: int


def _position(no: str) -> int | None:
    return int(no[-2:]) if no.isdigit() and len(no) >= 3 else None


def derive_layout(flats: list[tuple[str, int | None]]) -> DerivedLayout:
    """Work out a wing's layout from its complete list of (flat no, floor)."""
    per_floor: dict[int, list[str]] = {}
    odd: list[str] = []
    for raw, floor in flats:
        p = normalise_unit_no(raw)
        fl = floor if floor is not None else p.floor
        if fl is None:
            odd.append(p.unit_no)
            continue
        per_floor.setdefault(fl, []).append(p.unit_no)
    if not per_floor:
        return DerivedLayout(None, 1, None, [], sorted(set(odd)), len(odd))
    lowest, top = min(per_floor), max(per_floor)
    typical = Counter(len(v) for v in per_floor.values()).most_common(1)[0][0]
    positions = [_position(n) for fl, ns in per_floor.items() if len(ns) == typical for n in ns]
    per = max((p for p in positions if p), default=None) or typical
    extra = list(odd)
    for ns in per_floor.values():
        for n in ns:
            pos = _position(n)
            if pos is None or pos == 0 or pos > per:
                extra.append(n)
    skip = [f for f in range(lowest, top + 1) if f not in per_floor]
    return DerivedLayout(top, lowest, per, skip, sorted(set(extra)), sum(len(v) for v in per_floor.values()) + len(odd))


@dataclass
class ImportResult:
    wings: int = 0
    flats_new: int = 0
    flats_known: int = 0
    unmatched: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    ignored_columns: list[str] = field(default_factory=list)
    layouts: list[dict] = field(default_factory=list)


def _decimal(v):
    try:
        return Decimal(str(v).replace(",", "").strip()) if v not in (None, "") else None
    except InvalidOperation:
        return None


def _int(v):
    if v in (None, ""):
        return None
    s = str(v).strip().lower()
    if s in ("g", "ground", "gr", "tal", "तळ"):
        return 0
    try:
        return int(float(s))
    except ValueError:
        return None


def import_register(
    filename: str, content: bytes, *, source: str, complete: bool = True, dry_run: bool = False, society: Society | None = None
) -> ImportResult:
    """Load an official flat list. `complete`: the file lists every flat of each wing it mentions, so a flat
    number outside it cannot exist. `society`: every row belongs to this society (no society column needed)."""
    from apps.inventory.upload import read_table

    if source not in RegisterFlat.Source.values:
        raise ValueError(f"source must be one of {', '.join(RegisterFlat.Source.values)}")
    headers, rows = read_table(filename, content)
    lower = {h: str(h).strip().lower() for h in headers}
    lookup = {h: key for key, names in COLUMNS.items() for h in headers if lower[h] in names}
    res = ImportResult(ignored_columns=[h for h in headers if h not in lookup])
    if "unit_no" not in lookup.values() or ("society" not in lookup.values() and society is None):
        raise ValueError("The file needs a flat number column, and a society column (or pick the society)")
    groups: dict[Building, list[dict]] = {}
    cache: dict[str, Society | None] = {}
    with transaction.atomic():
        for i, raw in enumerate(rows, start=2):
            r = {lookup[h]: v for h, v in raw.items() if h in lookup}  # owner/phone columns never leave `raw`
            no = str(r.get("unit_no") or "").strip()
            if not no or str(r.get("society") or "").strip().lower().startswith("example"):
                continue
            soc = society
            if soc is None:
                name = str(r.get("society") or "").strip()
                if name not in cache:
                    decision = dedupe.decide(dedupe.find_candidates(name)) if name else None
                    cache[name] = decision.best.society if decision and decision.action == "auto" else None
                    if cache[name] is None and name:
                        res.unmatched.append(f"row {i}: {name}")
                soc = cache[name]
                if soc is None:
                    continue
            b = get_or_create_building(soc, str(r.get("wing") or "").strip() or None)
            groups.setdefault(b, []).append({"row": i, **r, "unit_no": no})
        for b, items in groups.items():
            before = layout_dict(b)
            for it in items:
                parsed = normalise_unit_no(it["unit_no"])
                obj, created = RegisterFlat.objects.get_or_create(
                    building=b,
                    unit_no_normalised=parsed.unit_no,
                    defaults={"unit_no": it["unit_no"][:30], "source": source},
                )
                obj.floor = _int(it.get("floor")) if _int(it.get("floor")) is not None else parsed.floor
                obj.carpet_sqft = _decimal(it.get("carpet_sqft")) or obj.carpet_sqft
                obj.source_ref = str(it.get("source_ref") or obj.source_ref or "").strip()[:40]
                obj.ward = str(it.get("ward") or obj.ward or "").strip()[:40]
                obj.save()
                res.flats_new += created
                res.flats_known += not created
            all_flats = list(b.register_flats.values_list("unit_no", "floor"))
            d = derive_layout(all_flats)
            b.floors_total, b.lowest_floor, b.units_per_floor = d.floors_total, d.lowest_floor, d.units_per_floor
            b.skip_floors, b.extra_unit_nos = d.skip_floors, d.extra_unit_nos
            b.layout_source, b.layout_verified = source, bool(d.floors_total and d.units_per_floor)
            b.register_complete = complete or b.register_complete
            b.save()
            audit(
                None,
                "building.register_imported",
                b,
                {"from": before, "to": layout_dict(b), "file": filename, "flats": d.flats},
                actor_label="import",
            )
            res.wings += 1
            res.layouts.append({"society": b.society.canonical_name, "wing": b.name, **layout_dict(b), "flats": d.flats})
        if dry_run:
            transaction.set_rollback(True)
    return res


# --- the building as a picture: floors x flats ----------------------------------------------------


def wing_grid(b: Building, mine: set[str] = frozenset()) -> dict:
    """Floors top-down, each with its flats. From the official list when we have it, else from the layout."""
    floors: dict[int, list[str]] = {}
    official = list(b.register_flats.values_list("unit_no_normalised", "floor"))
    if official:
        odd = []
        for no, fl in official:
            (floors.setdefault(fl, []) if fl is not None else odd).append(no)
        if odd:
            floors.setdefault(-99, []).extend(odd)
    elif b.floors_total and b.units_per_floor:
        for fl in range(b.lowest_floor, b.floors_total + 1):
            if fl in b.skip_floors:
                floors[fl] = []
                continue
            floors[fl] = [f"{'G' if fl == 0 else fl}{p:02d}" for p in range(1, b.units_per_floor + 1)]
        for x in b.extra_unit_nos:
            p = normalise_unit_no(x)
            floors.setdefault(p.floor if p.floor is not None else -99, []).append(p.unit_no)
    if b.floors_total and official:
        for fl in b.skip_floors:
            floors.setdefault(fl, [])

    def key(no):
        return (len(no), no)

    rows = [
        {
            "floor": fl if fl != -99 else None,
            "label": "Other" if fl == -99 else ("Ground" if fl == 0 else str(fl)),
            "no_flats": not ns,
            "flats": [{"no": n, "mine": n in mine} for n in sorted(set(ns), key=key)],
        }
        for fl, ns in sorted(floors.items(), key=lambda kv: -kv[0] if kv[0] != -99 else 10_000)
    ]
    return {
        "id": str(b.pk),
        "name": b.name,
        "layout": layout_dict(b) | {"register_complete": b.register_complete},
        "flats_total": sum(len(r["flats"]) for r in rows),
        "known": bool(rows),
        "floors": rows,
    }


def society_structure(society: Society, org=None) -> dict:
    """All wings of a society. `mine` marks the asking firm's own flats (RLS: nobody else's)."""
    mine: dict = {}
    if org is not None:
        from apps.inventory.models import Listing

        for bid, no in Listing.objects.filter(org=org, archived_at__isnull=True, unit__building__society=society).values_list(
            "unit__building_id", "unit__unit_no_normalised"
        ):
            mine.setdefault(bid, set()).add(no)
    wings = [wing_grid(b, mine.get(b.pk, set())) for b in society.buildings.filter(merged_into__isnull=True).order_by("name")]
    sources = sorted({w["layout"]["source"] for w in wings if w["layout"]["source"]})
    return {
        "society": {
            "id": str(society.pk),
            "name": society.canonical_name,
            "locality": society.locality.name,
            "wings_complete": society.wings_complete,
        },
        "sources": sources,
        "wings": wings,
    }
