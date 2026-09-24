"""Everything the broker's flat page shows (approved design, 2026-09-24).

Sections: key facts, house rules, what's in the flat, society amenities, distances, the building,
customers of this firm who fit, activity, and the private block (owner, keys, brokerage, notes,
how many other brokers hold the flat — never who). The "what customers see" view is the same data
with the private parts left out; the app decides what to hide.
"""

from apps.masterdata.models import AttributeDef, OwnershipClaim, ResolvedAttribute
from common import rls

from .models import Listing

FACT_KEYS = [
    "carpet_area_sqft",
    "furnishing",
    "facing",
    "bathrooms",
    "balconies",
    "car_parking_covered",
    "car_parking_open",
    "year_built",
    "flooring",
    "view",
    "kitchen_type",
    "layout_type",
]
RULE_CATEGORY = "10"
IN_FLAT_CATEGORIES = ("02", "03", "04")
SOCIETY_CATEGORIES = ("06",)
PLACES = [
    ("rail_station", "Railway station"),
    ("metro_station", "Metro station"),
    ("auto_stand", "Auto stand"),
    ("bus_stop", "Bus stop"),
    ("school", "School"),
    ("hospital", "Hospital"),
    ("market", "Market"),
    ("mall", "Mall"),
    ("park", "Park"),
]


def _fmt(value, a: AttributeDef) -> str:
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    if a.key == "carpet_area_sqft":
        return f"{float(value):,.0f} sq ft"
    if isinstance(value, str):
        return value[:1].upper() + value[1:]
    unit = f" {a.unit_label}" if a.unit_label and a.unit_label not in ("count",) else ""
    return f"{value}{unit}"


def _distance(m: int) -> str:
    return f"{m} m" if m < 1000 else f"{m / 1000:.1f} km"


def attributes_by_key(unit) -> dict:
    b = unit.building
    ras = ResolvedAttribute.objects.filter(subject_id__in=[unit.pk, b.pk, b.society_id]).select_related("attr")
    return {ra.attr_id: ra for ra in ras}


def sections(listing: Listing) -> dict:
    u = listing.unit
    b = u.building
    attrs = attributes_by_key(u)

    facts = [{"label": "Configuration", "value": "1 RK" if float(u.bhk) == 0.5 else f"{float(u.bhk):g} BHK"}]
    if u.carpet_sqft and "carpet_area_sqft" not in attrs:
        facts.append({"label": "Carpet area", "value": f"{float(u.carpet_sqft):,.0f} sq ft"})
    if u.floor is not None:
        facts.append(
            {"label": "Floor", "value": ("Ground" if u.floor == 0 else str(u.floor)) + (f" of {b.floors_total}" if b.floors_total else "")}
        )
    for key in FACT_KEYS:
        ra = attrs.get(key)
        if ra is not None and ra.value not in (None, "", []):
            label = {
                "carpet_area_sqft": "Carpet area",
                "year_built": "Built in",
                "car_parking_covered": "Covered parking",
                "car_parking_open": "Open parking",
                "facing": "Facing",
            }.get(key, ra.attr.label)
            facts.append({"label": label, "value": _fmt(ra.value, ra.attr), "disputed": ra.disputed})
    if listing.available_from:
        facts.append({"label": "Available from", "value": listing.available_from.strftime("%-d %b %Y")})

    def cat(ra):
        return ra.attr.category[:2]

    ordered = sorted(attrs.values(), key=lambda ra: (ra.attr.display_order, ra.attr.label))
    rules = [
        {"label": ra.attr.label, "value": _fmt(ra.value, ra.attr), "tone": _rule_tone(ra.value)}
        for ra in ordered
        if cat(ra) == RULE_CATEGORY and ra.value not in (None, "", [])
    ]
    in_flat = [ra.attr.label for ra in ordered if cat(ra) in IN_FLAT_CATEGORIES and ra.value is True]
    society = [ra.attr.label for ra in ordered if cat(ra) in SOCIETY_CATEGORIES and ra.value is True]
    facts_by_type = {f.poi_type: f for f in b.location_facts.all()}
    places = []
    for key, label in PLACES:
        f = facts_by_type.get(key)
        if f:
            places.append(
                {
                    "label": f"{label}: {f.poi_name}" if f.poi_name else label,
                    "value": f"{_distance(f.distance_m)} · {f.drive_min} min drive",
                }
            )
    loc = u.effective_location
    return {
        "facts": facts,
        "house_rules": rules,
        "in_flat": in_flat,
        "society_amenities": society,
        "places": places,
        "location": {"lat": loc.y, "lng": loc.x} if loc is not None else None,
        "locality": b.society.locality.name if b.society.locality_id else "",
        "building": {
            "id": str(b.pk),
            "name": b.name,
            "floors_total": b.floors_total,
            "units_per_floor": b.units_per_floor,
            "source": b.layout_source,
            "official_list": b.register_complete,
        },
    }


def _rule_tone(value) -> str:
    v = str(value).lower()
    if v in ("no", "not allowed", "false") or v.startswith("not "):
        return "bad"
    if "case" in v or "only" in v or "ask" in v:
        return "warn"
    return "ok"


def fitting_customers(listing: Listing, limit: int = 3) -> dict:
    """This firm's active requirements the flat roughly fits: same deal, BHK in range, price within budget
    (+10%), and in the area they asked for (when they named areas). A pointer, not the full matching run."""
    from apps.crm.models import Requirement

    u = listing.unit
    price = listing.price
    qs = Requirement.objects.filter(org_id=listing.org_id, active=True, txn_type=listing.txn_type, bhk_min__lte=u.bhk, bhk_max__gte=u.bhk)
    qs = qs.exclude(customer__stage__in=["closed_won", "closed_lost"]).select_related("customer").prefetch_related("localities")
    locality_id = u.building.society.locality_id
    hits = []
    for r in qs[:500]:
        if price and r.budget_max and price > r.budget_max * 1.1:
            continue
        locs = [loc.pk for loc in r.localities.all()]
        if locs and locality_id not in locs:
            continue
        hits.append(r)
    return {
        "count": len(hits),
        "customers": [
            {"customer_id": str(r.customer_id), "requirement_id": str(r.pk), "name": r.customer.name or "Customer"} for r in hits[:limit]
        ],
    }


def activity(listing: Listing, limit: int = 12) -> list[dict]:
    from apps.crm.models import ShortlistItem
    from apps.status.models import StatusEvent
    from apps.visits.models import VisitStop

    items = []
    for s in VisitStop.objects.filter(listing=listing, removed=False).select_related("plan__customer", "assigned_staff")[:20]:
        who = s.plan.customer.name or "a customer"
        staff = f" (field staff: {s.assigned_staff.display_name})" if s.assigned_staff_id and s.assigned_staff.display_name else ""
        outcome = f" · {s.get_outcome_display().lower()}" if s.outcome else ""
        at = s.checkin_at or s.slot_start or s.created_at
        items.append({"at": at.isoformat(), "text": f"Visit with {who}{staff}{outcome}"})
    for it in ShortlistItem.objects.filter(listing=listing).select_related("shortlist__customer")[:20]:
        if it.shortlist.shared_at:
            resp = {"interested": " · interested", "not_for_me": " · not for them"}.get(it.customer_response, "")
            items.append(
                {"at": it.shortlist.shared_at.isoformat(), "text": f"Shared with {it.shortlist.customer.name or 'a customer'}{resp}"}
            )
    for e in StatusEvent.objects.filter(unit_id=listing.unit_id, txn_type=listing.txn_type).order_by("-seq")[:10]:
        who = {"owner": "Owner", "broker": "A broker", "system": "System"}.get(e.actor_type.split("_")[0], "Update")
        if e.actor_org_id == listing.org_id:
            who = "You"
        items.append(
            {"at": e.at.isoformat(), "text": f"{who}: {e.to_state.replace('_', ' ').lower()}" + (f" ({e.reason})" if e.reason else "")}
        )
    items.append({"at": listing.created_at.isoformat(), "text": f"Added to your flats ({listing.get_origin_display().lower()})"})
    items.sort(key=lambda x: x["at"], reverse=True)
    return items[:limit]


def other_brokers(listing: Listing) -> int:
    """How many other firms hold this flat (a number only, never who)."""
    with rls.platform_context():
        return (
            Listing.objects.filter(unit_id=listing.unit_id, archived_at__isnull=True)
            .exclude(org_id=listing.org_id)
            .values("org_id")
            .distinct()
            .count()
        )


def owner_on_platform(listing: Listing) -> bool:
    return OwnershipClaim.objects.filter(
        unit_id=listing.unit_id, status__in=[OwnershipClaim.Status.DECLARED, OwnershipClaim.Status.VERIFIED]
    ).exists()
