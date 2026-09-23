"""Matching (MATCH-01..05): a requirement against ONE broker's own listings, with reasons.

Rules
  * Hard criteria exclude a flat only when we *know* it fails. Unknown or disputed
    values never exclude; they cost score and show as "≈ not confirmed" (docs/06 rule 7).
  * Every criterion produces an explanation chip: ok (✔), fail (✖) or unknown (≈).
"""
from dataclasses import dataclass, field
from decimal import Decimal

from django.contrib.gis.geos import Point

from apps.inventory.models import Listing
from apps.masterdata.models import AttributeDef, LocationFact, ResolvedAttribute
from apps.status.models import State, UnitStatus

BUDGET_TOLERANCE = 0.10
FURNISHING_ORDER = {"unfurnished": 0, "semi-furnished": 1, "fully furnished": 2}
LIVE_STATES = {State.AVAILABLE, State.AVAILABLE_UNCONFIRMED}


@dataclass
class Facts:
    """Everything the matcher knows about one listing's unit, flattened across unit/building/society."""

    listing: Listing
    bhk: float
    price: int | None
    location: Point
    locality_id: object
    status: str
    attrs: dict = field(default_factory=dict)  # key -> (value, disputed)
    distances: dict = field(default_factory=dict)  # poi_type -> metres


@dataclass
class Result:
    listing: Listing
    score: int
    excluded: bool
    explanation: list

    def as_dict(self):
        return {"listing_id": str(self.listing.pk), "score": self.score, "excluded": self.excluded, "explanation": self.explanation}


def _chip(key, label, result, detail=""):
    return {"key": key, "label": label, "result": result, "detail": detail}


def evaluate(req, f: Facts, labels: dict) -> Result:
    chips, excluded, penalty = [], False, 0.0

    def hard_fail(chip):
        nonlocal excluded
        excluded = True
        chips.append(chip)

    # Configuration
    if float(req.bhk_min) <= f.bhk <= float(req.bhk_max):
        chips.append(_chip("bhk", "BHK", "ok", f"{f.bhk:g} BHK"))
    else:
        hard_fail(_chip("bhk", "BHK", "fail", f"{f.bhk:g} BHK"))

    # Budget
    if f.price is None:
        chips.append(_chip("budget", "Budget", "unknown", "price not set"))
        penalty += 10
    else:
        ceiling = req.budget_max * (1 + BUDGET_TOLERANCE)
        floor = (req.budget_min or 0) * (1 - BUDGET_TOLERANCE)
        if f.price > ceiling or f.price < floor:
            hard_fail(_chip("budget", "Budget", "fail", f"₹{f.price:,}"))
        else:
            chips.append(_chip("budget", "Budget", "ok", f"₹{f.price:,}"))
            if f.price > req.budget_max:  # within tolerance, but over
                penalty += 10 * (f.price - req.budget_max) / (req.budget_max * BUDGET_TOLERANCE)

    # Area
    in_area = None
    if req.search_area is not None:
        in_area = req.search_area.contains(f.location)
    locality_ids = getattr(req, "_locality_ids", None)
    if locality_ids:
        in_area = bool(in_area) or f.locality_id in locality_ids
    if in_area is False:
        hard_fail(_chip("area", "Area", "fail", "outside the chosen area"))
    elif in_area:
        chips.append(_chip("area", "Area", "ok"))

    # Status
    if f.status == State.AVAILABLE:
        chips.append(_chip("status", "Availability", "ok", "confirmed"))
    elif f.status == State.AVAILABLE_UNCONFIRMED:
        chips.append(_chip("status", "Availability", "unknown", "not yet confirmed by owner"))
        penalty += 8
    else:
        hard_fail(_chip("status", "Availability", "fail", f.status))

    # Station distance (computed fact)
    if req.max_station_distance_m:
        d = f.distances.get("rail_station")
        if d is None:
            chips.append(_chip("dist_rail_station", "Near station", "unknown"))
            penalty += 5
        elif d <= req.max_station_distance_m:
            chips.append(_chip("dist_rail_station", "Near station", "ok", f"{d} m"))
        else:
            hard_fail(_chip("dist_rail_station", "Near station", "fail", f"{d} m"))

    # Must-haves from the dictionary
    for key, wanted in (req.must_haves or {}).items():
        label = labels.get(key, (key, "soft"))[0]
        matching = labels.get(key, (key, "soft"))[1]
        value, disputed = f.attrs.get(key, (None, False))
        verdict = _satisfies(key, value, wanted)
        if verdict is None or disputed:
            chips.append(_chip(key, label, "unknown", "disputed" if disputed else "not confirmed"))
            penalty += 4
        elif verdict:
            chips.append(_chip(key, label, "ok"))
        elif matching == "hard":
            hard_fail(_chip(key, label, "fail", str(value)))
        else:
            chips.append(_chip(key, label, "fail", str(value)))
            penalty += 8

    # Nice-to-haves only move the score.
    for key, wanted in (getattr(req, "nice_to_haves", None) or {}).items():
        value, _ = f.attrs.get(key, (None, False))
        if _satisfies(key, value, wanted) is False:
            penalty += 3

    # House rules: the customer's own needs against the flat's conduct-based rules.
    for chip, clash, unknown in _house_rules(req.house_rule_needs or {}, f.attrs, getattr(req, "occupants", None)):
        if clash:
            hard_fail(chip)
        else:
            chips.append(chip)
            if unknown:
                penalty += 4

    # Closeness to station as a general quality signal even when not required.
    d = f.distances.get("rail_station")
    if d is not None and not req.max_station_distance_m:
        penalty += min(8, d / 500)

    score = max(0, min(100, round(100 - penalty)))
    return Result(f.listing, 0 if excluded else score, excluded, chips)


def _satisfies(key, value, wanted):
    if value is None:
        return None
    if key == "furnishing":
        return FURNISHING_ORDER.get(value, -1) >= FURNISHING_ORDER.get(wanted, 99)
    if isinstance(wanted, bool):
        return bool(value) is wanted
    if isinstance(wanted, (int, float)) and not isinstance(wanted, bool) and isinstance(value, (int, float)):
        return value >= wanted
    if isinstance(value, list):
        return wanted in value
    return value == wanted


def _house_rules(needs: dict, attrs: dict, occupants):
    def val(k):
        return attrs.get(k, (None, False))[0]

    if needs.get("pets"):
        pet = str(needs["pets"]).lower()
        rule, society = val("pets_allowed"), val("society_pet_policy")
        blocked = rule == "no" or society == "not allowed" or (rule == "cats only" and pet != "cat") or (
            rule == "small dogs" and pet not in ("dog", "small dog", "small_dog")
        )
        yield _chip("pets_allowed", "Pets", "fail" if blocked else ("unknown" if rule is None else "ok"), rule or ""), blocked, rule is None
    if needs.get("nonveg_cooking"):
        rule = val("nonveg_cooking")
        yield _chip("nonveg_cooking", "Non-veg cooking", "fail" if rule == "not allowed" else ("unknown" if rule is None else "ok")), rule == "not allowed", rule is None
    if needs.get("bachelors"):
        rule, fam = val("bachelors_allowed"), val("family_only")
        blocked = rule == "not allowed" or fam is True
        yield _chip("bachelors_allowed", "Bachelors", "fail" if blocked else ("unknown" if rule is None else "ok")), blocked, rule is None
    if needs.get("smoking"):
        rule = val("smoking")
        yield _chip("smoking", "Smoking", "fail" if rule == "not allowed" else ("unknown" if rule is None else "ok")), rule == "not allowed", rule is None
    if needs.get("company_lease"):
        rule = val("company_lease")
        yield _chip("company_lease", "Company lease", "ok" if rule else "unknown"), False, rule is None
    if occupants:
        cap = val("max_occupants")
        blocked = cap is not None and occupants > cap
        yield _chip("max_occupants", "Occupants", "fail" if blocked else ("unknown" if cap is None else "ok"), str(cap or "")), blocked, cap is None


def load_facts(listings: list[Listing], txn_type: str) -> list[Facts]:
    """Bulk-load resolved attributes (unit + building + society), statuses and distances."""
    units = {l.unit_id: l.unit for l in listings}
    buildings = {u.building_id for u in units.values()}
    societies = {u.building.society_id for u in units.values()}
    resolved = ResolvedAttribute.objects.filter(
        subject_id__in=list(units) + list(buildings) + list(societies)
    ).values_list("subject_id", "attr_id", "value", "disputed")
    by_subject: dict = {}
    for sid, key, value, disputed in resolved:
        by_subject.setdefault(sid, {})[key] = (value, disputed)
    statuses = dict(UnitStatus.objects.filter(unit_id__in=units, txn_type=txn_type).values_list("unit_id", "state"))
    dists: dict = {}
    for bid, poi_type, d in LocationFact.objects.filter(building_id__in=buildings).values_list("building_id", "poi_type", "distance_m"):
        dists.setdefault(bid, {})[poi_type] = d
    out = []
    for l in listings:
        u = l.unit
        attrs = {}
        for sid in (u.building.society_id, u.building_id, u.pk):  # most specific wins
            attrs.update(by_subject.get(sid, {}))
        out.append(
            Facts(
                listing=l,
                bhk=float(u.bhk),
                price=l.price,
                location=u.location or u.building.location,
                locality_id=u.building.society.locality_id,
                status=statuses.get(u.pk, State.UNKNOWN),
                attrs=attrs,
                distances=dists.get(u.building_id, {}),
            )
        )
    return out


def run(req, *, org_id, include_unconfirmed=True, include_excluded=False) -> list[Result]:
    """Match against the org's own listings. Caller must be in that org's RLS context."""
    qs = (
        Listing.objects.filter(org_id=org_id, txn_type=req.txn_type, archived_at__isnull=True, withdrawn_by_owner=False)
        .select_related("unit__building__society")
    )
    live = [State.AVAILABLE] + ([State.AVAILABLE_UNCONFIRMED] if include_unconfirmed else [])
    qs = qs.filter(unit__statuses__txn_type=req.txn_type, unit__statuses__state__in=live)
    if req.bhk_min is not None:
        qs = qs.filter(unit__bhk__gte=Decimal(req.bhk_min) - Decimal("0.5"), unit__bhk__lte=Decimal(req.bhk_max) + Decimal("0.5"))
    listings = list(qs)
    labels = {a.key: (a.label, a.matching) for a in AttributeDef.objects.filter(key__in=list((req.must_haves or {}).keys()))}
    if hasattr(req, "localities") and req.pk and not hasattr(req, "_locality_ids"):
        req._locality_ids = set(req.localities.values_list("id", flat=True))
    results = [evaluate(req, f, labels) for f in load_facts(listings, req.txn_type)]
    if not include_excluded:
        results = [r for r in results if not r.excluded]
    results.sort(key=lambda r: (r.excluded, -r.score))
    return results


def count_matches(req, org_id) -> int:
    return len(run(req, org_id=org_id))
