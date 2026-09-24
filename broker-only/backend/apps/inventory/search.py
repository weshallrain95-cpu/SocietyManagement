"""Find a flat the way brokers say it: "HE A-1203", "rodas a 1203", "Lodha Amara 1501", "1203".

Brokers keep planning visits their own way until they trust the matching engine, so staff must be
able to jump straight to a society and flat number. Only the broker's own flats are searched (RLS).
A flat that isn't in the broker's list is simply not found: the platform never offers a unit to a
broker (it could be another broker's), and never moves flats between brokers.
"""

import re

from django.db.models import Q

from apps.masterdata import dedupe
from apps.masterdata.models import Building
from apps.masterdata.normalise import normalise_building, normalise_unit_no

from .models import Listing

_UNIT = re.compile(r"^(?:[a-z]\s*[-/]?\s*)?\d{1,4}[a-z]?$|^g\s*-?\s*\d{1,2}$|^ph\s*-?\s*\d{1,2}$", re.I)


def parse_query(q: str) -> tuple[str, str, str]:
    """Split into (place text, flat number, wing letter). The flat number is the last token that looks like one."""
    tokens = re.split(r"[\s,]+", q.strip())
    unit_no, wing = "", ""
    # "a-1203" / "A1203" / "1203" / "G-2" / "PH1" at the end; also "a 1203" as two tokens
    if tokens and _UNIT.match(tokens[-1]) and any(ch.isdigit() for ch in tokens[-1]):
        u = normalise_unit_no(tokens.pop())
        unit_no, wing = u.unit_no, u.wing
        if not wing and tokens and re.fullmatch(r"[a-z]", tokens[-1], re.I):
            wing = tokens.pop().upper()
    return " ".join(tokens), unit_no, wing


def search_flats(listings, q: str, *, org, limit: int = 20) -> dict:
    text, unit_no, wing = parse_query(q)
    listings = listings.filter(archived_at__isnull=True).select_related("unit__building__society")
    societies: list = []
    if text:
        cands = [c for c in dedupe.find_candidates(text, include_provisional_for_org=org, limit=5) if c.score >= 0.5]
        societies = [c.society for c in cands]
        key = normalise_building(text)
        # a wing name typed as the place ("Rodas A 1203") finds the wing's society too
        wing_hits = Building.objects.filter(merged_into__isnull=True, name_normalised__startswith=key).values_list("pk", flat=True)[:50]
        listings = listings.filter(Q(unit__building__society__in=societies) | Q(unit__building__in=list(wing_hits)))
    if unit_no:
        listings = listings.filter(unit__unit_no_normalised__startswith=unit_no)
    if not (text or unit_no):
        return {"results": [], "unit_no": "", "wing": ""}

    rank_soc = {s.pk: i for i, s in enumerate(societies)}

    def rank(l: Listing):
        u = l.unit
        return (
            u.unit_no_normalised != unit_no,  # exact flat number first
            bool(wing) and not u.building.name_normalised.endswith(wing),  # then the wing they said
            rank_soc.get(u.building.society_id, 99),
            u.building.name,
            u.unit_no_normalised,
        )

    results = sorted(listings[:200], key=rank)[:limit]
    return {"results": results, "unit_no": unit_no, "wing": wing}
