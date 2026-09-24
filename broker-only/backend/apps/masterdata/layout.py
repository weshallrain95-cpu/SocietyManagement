"""Building layouts: which wings and flat numbers can exist (MD-13).

Our master data is a closed universe. A broker never invents a building: they pick a wing we
know, and the flat number is checked against that wing's floors and flats per floor.

- A *verified* layout (RERA, field survey or ops) blocks impossible flats, e.g. 2504 in a
  20-floor wing. The broker can report the layout as wrong; ops fixes it.
- An *unverified* layout (typed by a broker, or partly known) only warns; the broker confirms.
- A society marked `wings_complete` never gets a new wing from a broker: an unknown wing name
  is a typo, and we suggest the closest real one.
"""

from dataclasses import asdict, dataclass
from difflib import SequenceMatcher

from .models import Building, Society
from .normalise import normalise_building, normalise_unit_no


@dataclass
class Issue:
    code: str
    message: str
    blocking: bool = False

    def as_dict(self):
        return asdict(self)


def floor_word(n: int) -> str:
    return "ground floor" if n == 0 else f"floor {n}"


def layout_dict(b: Building) -> dict:
    return {
        "floors_total": b.floors_total,
        "lowest_floor": b.lowest_floor,
        "units_per_floor": b.units_per_floor,
        "skip_floors": b.skip_floors,
        "extra_unit_nos": b.extra_unit_nos,
        "verified": b.layout_verified,
        "source": b.layout_source,
    }


def expected_units(b: Building) -> int | None:
    if not (b.floors_total and b.units_per_floor):
        return None
    floors = [f for f in range(b.lowest_floor, b.floors_total + 1) if f not in b.skip_floors]
    return len(floors) * b.units_per_floor + len(b.extra_unit_nos)


def check_unit(b: Building, unit_no: str, floor: int | None = None) -> list[Issue]:
    """What is wrong with flat `unit_no` in wing `b`? Empty list = fine, or nothing known to check against."""
    parsed = normalise_unit_no(unit_no)
    no = parsed.unit_no
    if no in {normalise_unit_no(x).unit_no for x in b.extra_unit_nos}:
        return []
    issues: list[Issue] = []
    hard = b.layout_verified
    fl = floor if floor is not None else parsed.floor
    if floor is not None and parsed.floor is not None and floor != parsed.floor:
        issues.append(Issue("floor_mismatch", f"Flat {no} is normally on {floor_word(parsed.floor)}, but {floor_word(floor)} was entered."))
    if fl is not None:
        if b.floors_total is not None and fl > b.floors_total:
            issues.append(
                Issue("above_top_floor", f"{b.name} has {b.floors_total} floors, so flat {no} ({floor_word(fl)}) cannot exist.", hard)
            )
        elif 0 <= fl < b.lowest_floor:
            issues.append(Issue("below_lowest_floor", f"Flats in {b.name} start from {floor_word(b.lowest_floor)}.", hard))
        elif fl in b.skip_floors:
            issues.append(Issue("no_flats_on_floor", f"{b.name} has no flats on {floor_word(fl)} (refuge or podium floor).", hard))
    if b.units_per_floor and no.isdigit() and len(no) >= 3:
        pos = int(no[-2:])
        if pos == 0 or pos > b.units_per_floor:
            issues.append(
                Issue(
                    "no_such_flat_position",
                    f"{b.name} has {b.units_per_floor} flats per floor (…01 to …{b.units_per_floor:02d}), so flat {no} cannot exist.",
                    hard,
                )
            )
    return issues


def _similar(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()


def wings(society: Society):
    return list(society.buildings.filter(merged_into__isnull=True).order_by("name"))


def resolve_wing(society: Society, name: str | None) -> tuple[Building | None, list[Issue], list[str]]:
    """Find the wing a broker means. Returns (building or None if a new one would be created, issues, suggestions)."""
    existing = wings(society)
    if not (name or "").strip():
        if len(existing) == 1:
            return existing[0], [], []
        if len(existing) > 1:
            names = [b.name for b in existing]
            return None, [Issue("which_wing", f"{society.canonical_name} has {len(names)} wings. Which one?", True)], names
        return None, [], []  # first flat in a society we know nothing about: a "Main" building is created
    key = normalise_building(name)
    for b in existing:
        if b.name_normalised == key:
            return b, [], []
    # Brokers shorten: "B" for "Rodas B", or add the society's name: "Rodas B" for "B". Accept only an unambiguous match.
    short = [
        b
        for b in existing
        if (len(key) <= 2 and b.name_normalised.endswith(key)) or (len(b.name_normalised) <= 2 and key.endswith(b.name_normalised))
    ]
    if len(short) == 1:
        return short[0], [], []
    ranked = sorted(existing, key=lambda b: -_similar(key, b.name_normalised))
    suggestions = [b.name for b in ranked if _similar(key, b.name_normalised) >= 0.5][:3]
    if society.wings_complete:
        known = ", ".join(b.name for b in existing[:8])
        hint = f" Did you mean {suggestions[0]}?" if suggestions else ""
        return (
            None,
            [Issue("unknown_wing", f"{society.canonical_name} has no wing “{name.strip()}”. Wings: {known}.{hint}", True)],
            (suggestions or [b.name for b in existing]),
        )
    if suggestions:
        msg = f"“{name.strip()}” is a new wing for {society.canonical_name}. Did you mean {suggestions[0]}?"
        return None, [Issue("new_wing", msg)], suggestions
    return None, [], []


def issues_json(result: dict) -> dict:
    return result | {"issues": [i.as_dict() for i in result["issues"]]}


def check_flat(society: Society, wing: str | None, unit_no: str, floor: int | None = None) -> dict:
    """One call for the app and uploads: resolve the wing, then check the flat."""
    wing = (wing or "").strip() or normalise_unit_no(unit_no).wing or None  # "B-1203" typed as the flat means wing B
    b, issues, suggestions = resolve_wing(society, wing)
    if b is not None:
        issues += check_unit(b, unit_no, floor)
    return {
        "wing": b.name if b else wing,
        "building": {"id": str(b.pk), "name": b.name, "layout": layout_dict(b)} if b else None,
        "issues": issues,
        "suggestions": suggestions,
        "blocking": any(i.blocking for i in issues),
    }
