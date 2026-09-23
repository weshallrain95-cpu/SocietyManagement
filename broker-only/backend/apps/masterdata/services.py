import re

from django.contrib.gis.geos import Point
from django.db import transaction

from apps.audit.services import audit
from common.notify import queue_for_admin

from . import dedupe
from .models import Building, Locality, Society, SocietyAlias, Unit
from .normalise import normalise_building, normalise_unit_no


class MasterDataError(Exception):
    pass


_MAPS_PATTERNS = (
    re.compile(r"@(-?\d+\.\d+),(-?\d+\.\d+)"),
    re.compile(r"[?&](?:q|query|ll|destination)=(-?\d+\.\d+),\s*(-?\d+\.\d+)"),
    re.compile(r"^\s*(-?\d{1,2}\.\d+)\s*,\s*(-?\d{1,3}\.\d+)\s*$"),
)


def parse_maps_link(text: str):
    """Coordinates from a Google Maps URL or a pasted "19.26, 72.96"; None for short links (resolved by ops)."""
    for pat in _MAPS_PATTERNS:
        m = pat.search(text or "")
        if m:
            lat, lng = float(m.group(1)), float(m.group(2))
            if 18.5 <= lat <= 20.5 and 72.5 <= lng <= 73.6:  # MMR bounds: rejects swapped or foreign coordinates
                return Point(lng, lat, srid=4326)
    return None


@transaction.atomic
def move_society_pin(society: Society, point, *, user, reason: str) -> dict:
    """Move a society (and its buildings still on the old pin) and recompute distance facts."""
    from .location import compute_for_building

    old = society.location
    society.location = point
    society.save(update_fields=["location"])
    moved = 0
    for b in society.buildings.filter(merged_into__isnull=True):
        if b.location.equals_exact(old, tolerance=1e-7):
            b.location = point
            b.save(update_fields=["location"])
            moved += 1
        compute_for_building(b)
    audit(user, "society.pin_moved", society, {"from": [old.y, old.x], "to": [point.y, point.x], "reason": reason[:200]})
    return {"buildings_moved": moved}


def propose_society(
    *, name: str, locality: Locality, location, org, address: str = "", pincode: str = "", user=None, candidates=None
) -> Society:
    """MD-04: unknown names never create an active society; they become a provisional proposal."""
    s = Society.objects.create(
        canonical_name=name.strip(),
        locality=locality,
        location=location,
        address_line=address,
        pincode=pincode,
        status=Society.Status.PROVISIONAL,
        proposed_by_org=org,
        provenance={"source": "broker_proposal"},
    )
    audit(user, "society.proposed", s, {"name": name, "org": str(org.pk) if org else None})
    queue_for_admin("provisional_society", s, f"New society proposed: {s.canonical_name}", {"candidates": candidates or []})
    return s


def get_or_create_building(society: Society, name: str | None) -> Building:
    key = normalise_building(name or "Main")
    b = Building.objects.filter(society=society, name_normalised=key, merged_into__isnull=True).first()
    if b:
        return b
    b = Building.objects.create(society=society, name=(name or "Main").strip() or "Main", location=society.location)
    from .location import compute_for_building

    compute_for_building(b)  # MD-07: distances exist from the first listing onwards
    return b


def get_or_create_unit(building: Building, unit_no: str, *, bhk, property_type="apartment", floor=None) -> tuple[Unit, bool]:
    parsed = normalise_unit_no(unit_no)
    u = Unit.objects.filter(building=building, unit_no_normalised=parsed.unit_no, merged_into__isnull=True).first()
    if u:
        return u, False
    u = Unit.objects.create(
        building=building,
        unit_no=unit_no.strip(),
        floor=floor if floor is not None else parsed.floor,
        bhk=bhk,
        property_type=property_type,
    )
    return u, True


@transaction.atomic
def merge_societies(source: Society, target: Society, *, user) -> dict:
    """MD-05: fold `source` into `target`, re-pointing buildings, units and aliases."""
    if source.pk == target.pk:
        raise MasterDataError("Cannot merge a society into itself")
    if target.status == Society.Status.MERGED:
        raise MasterDataError("Target is itself merged; merge into its successor")
    moved_buildings = merged_buildings = merged_units = 0
    for b in Building.objects.filter(society=source, merged_into__isnull=True):
        twin = Building.objects.filter(society=target, name_normalised=b.name_normalised, merged_into__isnull=True).first()
        if twin is None:
            b.society = target
            b.save(update_fields=["society"])
            moved_buildings += 1
            continue
        merged_units += _merge_building_units(b, twin)
        b.merged_into = twin
        b.save(update_fields=["merged_into"])
        merged_buildings += 1
    for alias in SocietyAlias.objects.filter(society=source):
        if not SocietyAlias.objects.filter(society=target, alias_normalised=alias.alias_normalised).exists():
            alias.society = target
            alias.save(update_fields=["society"])
    dedupe.learn_alias(target, source.canonical_name, SocietyAlias.Source.MERGE)
    source.status = Society.Status.MERGED
    source.merged_into = target
    source.save(update_fields=["status", "merged_into"])
    if target.status == Society.Status.PROVISIONAL:
        target.status = Society.Status.ACTIVE
        target.save(update_fields=["status"])
    result = {"moved_buildings": moved_buildings, "merged_buildings": merged_buildings, "merged_units": merged_units}
    audit(user, "society.merged", source, {"into": str(target.pk), **result})
    return result


def _merge_building_units(src: Building, dst: Building) -> int:
    from apps.inventory.services import repoint_unit

    n = 0
    for u in Unit.objects.filter(building=src, merged_into__isnull=True):
        twin = Unit.objects.filter(building=dst, unit_no_normalised=u.unit_no_normalised, merged_into__isnull=True).first()
        if twin is None:
            u.building = dst
            u.save(update_fields=["building"])
        else:
            repoint_unit(u, twin)
            u.merged_into = twin
            u.save(update_fields=["merged_into"])
            n += 1
    return n


@transaction.atomic
def approve_provisional(society: Society, *, user) -> Society:
    society.status = Society.Status.ACTIVE
    society.save(update_fields=["status"])
    audit(user, "society.approved", society)
    return society
