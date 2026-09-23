"""Anonymous supply aggregates for the customer map (MKT-01, Data Model §8).

Only counts, broker counts and price bands leave this module; price bands need at least
K units in the cell so no single flat's price can be read off the map."""

import statistics

import h3
from django.contrib.gis.geos import Point
from django.db.models import F

from apps.inventory.models import Listing
from apps.orgs.models import ServiceArea
from apps.status.models import UnitStatus

from . import presence
from .models import SupplyCell

RESOLUTIONS = (7, 8, 9)
K_ANON = 5
LIVE = ("AVAILABLE", "AVAILABLE_UNCONFIRMED")


def bhk_bucket(bhk) -> str:
    b = float(bhk)
    return "1RK" if b < 1 else ("4+" if b >= 4 else f"{int(b)}")


def rebuild() -> int:
    """Full rebuild (platform context). Incremental refresh per unit is an optimisation for later."""
    live_units = UnitStatus.objects.filter(state__in=LIVE).values_list("unit_id", "txn_type")
    live = set(live_units)
    rows = (
        Listing.objects.filter(archived_at__isnull=True, withdrawn_by_owner=False)
        .annotate(bx=F("unit__building__location"))
        .values_list("unit_id", "txn_type", "unit__bhk", "asking_rent", "asking_price", "unit__building__location")
    )
    cells: dict = {}
    seen = set()
    for unit_id, txn, bhk, rent, price, loc in rows:
        if (unit_id, txn) not in live or (unit_id, txn) in seen:
            continue
        seen.add((unit_id, txn))
        amount = rent if txn == "RENT" else price
        for res in RESOLUTIONS:
            cell = h3.latlng_to_cell(loc.y, loc.x, res)
            c = cells.setdefault((cell, res, txn, bhk_bucket(bhk)), {"units": 0, "prices": []})
            c["units"] += 1
            if amount:
                c["prices"].append(amount)
    SupplyCell.objects.all().delete()
    objs = []
    for (cell, res, txn, bucket), c in cells.items():
        lat, lng = h3.cell_to_latlng(cell)
        p = sorted(c["prices"])
        bands = statistics.quantiles(p, n=4) if len(p) >= K_ANON else [None, None, None]
        objs.append(
            SupplyCell(
                h3_index=cell,
                resolution=res,
                txn_type=txn,
                bhk_bucket=bucket,
                units_available=c["units"],
                price_p25=_int(bands[0]),
                price_p50=_int(bands[1]),
                price_p75=_int(bands[2]),
                brokers_serving=ServiceArea.objects.filter(area__contains=Point(lng, lat, srid=4326), org__verification_status="verified")
                .values("org_id")
                .distinct()
                .count(),
                lat=lat,
                lng=lng,
            )
        )
    SupplyCell.objects.bulk_create(objs, batch_size=1000)
    return len(objs)


def _int(v):
    return int(round(v)) if v is not None else None


def zoom_to_res(zoom: float) -> int:
    return 7 if zoom < 12 else (8 if zoom < 14 else 9)


def map_view(*, bbox: tuple[float, float, float, float], zoom: float, txn_type: str, bhk: str | None = None) -> dict:
    """bbox = (min_lng, min_lat, max_lng, max_lat)."""
    res = zoom_to_res(zoom)
    min_lng, min_lat, max_lng, max_lat = bbox
    qs = SupplyCell.objects.filter(
        resolution=res, txn_type=txn_type, lat__gte=min_lat, lat__lte=max_lat, lng__gte=min_lng, lng__lte=max_lng
    )
    if bhk:
        qs = qs.filter(bhk_bucket=bhk)
    merged: dict = {}
    for c in qs:
        m = merged.setdefault(
            c.h3_index, {"h3": c.h3_index, "lat": c.lat, "lng": c.lng, "units": 0, "brokers_serving": c.brokers_serving, "bands": []}
        )
        m["units"] += c.units_available
        if c.price_p50:
            m["bands"].append((c.price_p25, c.price_p50, c.price_p75))
    clusters = []
    for m in merged.values():
        bands = m.pop("bands")
        m["price_band"] = (
            {"p25": min(b[0] for b in bands), "p50": int(statistics.median(b[1] for b in bands)), "p75": max(b[2] for b in bands)}
            if bands
            else None
        )
        clusters.append(m)
    online = online_brokers_in_bbox(bbox)
    return {"resolution": res, "clusters": clusters, "brokers_online": online}


def online_brokers_in_bbox(bbox) -> list[dict]:
    from django.contrib.gis.geos import Polygon

    poly = Polygon.from_bbox(bbox)
    poly.srid = 4326
    out = []
    for org_id, name, rating, loc in (
        ServiceArea.objects.filter(area__intersects=poly, org__verification_status="verified")
        .values_list("org_id", "org__name", "org__rating_bayes", "org__office_location")
        .distinct()
    ):
        if presence.is_online(org_id) and not any(o["id"] == str(org_id) for o in out):
            out.append(
                {"id": str(org_id), "name": name, "rating": float(rating), "location": {"lat": loc.y, "lng": loc.x} if loc else None}
            )
    return out
