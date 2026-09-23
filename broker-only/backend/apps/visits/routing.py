"""Visit ordering. Google Routes API (waypoint optimisation) is used when configured; this local
fallback (nearest neighbour + 2-opt on street-adjusted distances) always works, including offline."""

import math

ROAD_FACTOR = 1.35
SPEED_M_PER_MIN = {"drive": 300, "two_wheeler": 350, "walk": 80}


def haversine_m(a, b) -> float:
    lat1, lng1, lat2, lng2 = map(math.radians, (a[1], a[0], b[1], b[0]))
    h = math.sin((lat2 - lat1) / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin((lng2 - lng1) / 2) ** 2
    return 2 * 6_371_000 * math.asin(math.sqrt(h))


def travel_min(a, b, mode: str) -> int:
    return max(1, round(haversine_m(a, b) * ROAD_FACTOR / SPEED_M_PER_MIN.get(mode, 300)))


def order_stops(start, points: list[tuple[float, float]]) -> list[int]:
    """Return an index order visiting all points, starting near `start` (or the first point)."""
    n = len(points)
    if n <= 2:
        return list(range(n))
    here = start or points[0]
    remaining, order = set(range(n)), []
    while remaining:
        nxt = min(remaining, key=lambda i: haversine_m(here, points[i]))
        order.append(nxt)
        remaining.remove(nxt)
        here = points[nxt]

    def length(o):
        total = haversine_m(start, points[o[0]]) if start else 0
        return total + sum(haversine_m(points[o[i]], points[o[i + 1]]) for i in range(len(o) - 1))

    improved = True
    while improved:
        improved = False
        for i in range(0, n - 1):
            for j in range(i + 1, n):
                cand = order[:i] + order[i : j + 1][::-1] + order[j + 1 :]
                if length(cand) + 1e-6 < length(order):
                    order, improved = cand, True
    return order
