"""Computed location facts (MD-07). Brokers cannot type 'near station'; the map decides."""

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.measure import D

from .models import Building, LocationFact, Poi

ROAD_FACTOR = 1.3  # straight line -> street distance in dense MMR grids
WALK_M_PER_MIN = 80  # ~4.8 km/h
AUTO_M_PER_MIN = 300  # ~18 km/h in traffic, plus 2 min to find an auto


def estimate_minutes(distance_m: float) -> tuple[int, int]:
    street = distance_m * ROAD_FACTOR
    return max(1, round(street / WALK_M_PER_MIN)), max(1, round(street / AUTO_M_PER_MIN + 2))


def compute_for_building(building: Building, max_km: float = 8) -> list[LocationFact]:
    facts = []
    for poi_type in Poi.Type.values:
        nearest = (
            Poi.objects.filter(type=poi_type, location__dwithin=(building.location, D(km=max_km)))
            .annotate(d=Distance("location", building.location))
            .order_by("d")
            .first()
        )
        if not nearest:
            LocationFact.objects.filter(building=building, poi_type=poi_type).delete()
            continue
        walk, drive = estimate_minutes(nearest.d.m)
        fact, _ = LocationFact.objects.update_or_create(
            building=building,
            poi_type=poi_type,
            defaults={
                "poi": nearest,
                "poi_name": nearest.name,
                "distance_m": round(nearest.d.m),
                "walk_min": walk,
                "drive_min": drive,
                "method": "estimate",
            },
        )
        facts.append(fact)
    return facts


def schools_within(building: Building, metres: int = 1000) -> int:
    return Poi.objects.filter(type=Poi.Type.SCHOOL, location__dwithin=(building.location, D(m=metres))).count()


def facts_dict(building: Building) -> dict:
    return {
        f.poi_type: {"name": f.poi_name, "distance_m": f.distance_m, "walk_min": f.walk_min, "drive_min": f.drive_min}
        for f in building.location_facts.all()
    }
