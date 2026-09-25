"""MahaRERA's public project list -> the society universe (D18).

The public list gives each registered project's RERA number, name, promoter and pin code (no map pin, and
no wings/floors/flats: those sit behind a CAPTCHA on the details page and are not collected). Projects are
grouped into complexes ("LODHA SPLENDORA - PLATINO - B" and "... - PLATINO - D" are one society), then:

- a complex that clearly matches a known society adds its RERA numbers to that society;
- anything else becomes a *provisional* society for ops to approve or merge (MD-04). Its pin is the
  area's centre and is flagged approximate, so it shows up for pin checking. Brokers never see a
  provisional society until ops approves it.

Collected with tools/maharera/fetch_projects.py; loaded with `manage.py import_rera_projects`.
"""

import csv
import re
from dataclasses import dataclass, field

from django.db import transaction

from apps.audit.services import audit
from common.notify import queue_for_admin

from . import dedupe
from .models import Locality, Society
from .normalise import normalise_name

# Pin code -> the pilot area it usually belongs to (refined by a locality word in the name when present).
PILOT_PINCODES = {
    "400606": "Pokhran Road",
    "400607": "Hiranandani Estate",
    "400608": "Balkum",
    "400610": "Vasant Vihar",
    "400615": "Kasarvadavali",
}

NAME_SURE = 0.97
# The public list has no project type; skip what is plainly not housing.
NOT_HOUSING = re.compile(r"\b(hotel|commercial|shops?|offices?|industrial|warehouse|godown|mall|hospital|school|it park)\b", re.I)

_SUFFIX = re.compile(
    r"\s*(?:[-–,(]\s*)?\b(?:phase|ph|wing|wings|tower|towers|bldg|building|buildings|plot|sector|stage|part|cluster|type)\b.*$",
    re.I,
)
_TRAILING_CODE = re.compile(r"\s+(?:[A-Z]|[IVX]{1,4}|\d{1,2}|[A-Z]\d?|\d[A-Z])$")


def _key(name: str) -> str:
    n = normalise_name(name)
    return n.strong_compact or n.compact


@dataclass
class Complex:
    name: str
    pincode: str
    projects: list = field(default_factory=list)
    buildings: set = field(default_factory=set)


def complex_name(project_name: str) -> tuple[str, str]:
    """('LODHA SPLENDORA - PLATINO - B') -> ('LODHA SPLENDORA', 'PLATINO - B'); redevelopment prefixes dropped."""
    raw = re.sub(r"\s+", " ", project_name or "").strip()
    raw = re.sub(r"^(?:proposed\s+)?re-?development\s+of\s+", "", raw, flags=re.I)
    parts = [p.strip() for p in re.split(r"\s+[-–]\s+|\s*[-–]\s*(?=[A-Z0-9]{1,3}$)", raw) if p.strip()]
    base, rest = (parts[0], " - ".join(parts[1:])) if parts else (raw, "")
    m = _SUFFIX.search(base)
    if m and m.start() > 2:
        rest = (base[m.start() :].strip(" -,(") + (" - " + rest if rest else "")).strip()
        base = base[: m.start()]
    code = _TRAILING_CODE.search(base)
    if code and len(base) - len(code.group(0)) > 3:
        rest = (code.group(0).strip() + (" - " + rest if rest else "")).strip()
        base = base[: code.start()]
    return base.strip(" -,"), rest


def read_projects(path: str, pincodes=PILOT_PINCODES) -> dict[tuple[str, str], Complex]:
    groups: dict[tuple[str, str], Complex] = {}
    with open(path, newline="", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            pin = (row.get("pincode") or "").strip()
            if pin not in pincodes or NOT_HOUSING.search(row.get("project_name", "")):
                continue
            base, building = complex_name(row["project_name"])
            key = (normalise_name(base).compact or base.lower(), pin)
            g = groups.setdefault(key, Complex(name=base.title() if base.isupper() else base, pincode=pin))
            g.projects.append({k: row.get(k, "") for k in ("rera_no", "project_name", "promoter", "last_modified", "details_url")})
            if building:
                g.buildings.add(building)
    return groups


def _locality_for(c: Complex, localities: dict[str, Locality]) -> Locality:
    hint = normalise_name(c.name).locality_hint or normalise_name(" ".join(p["project_name"] for p in c.projects)).locality_hint
    for name, loc in localities.items():
        if hint and hint in name.lower():
            return loc
    by_pin = [loc for loc in localities.values() if c.pincode in (loc.pincodes or [])]
    if len(by_pin) == 1:
        return by_pin[0]
    return localities.get(PILOT_PINCODES.get(c.pincode, ""), by_pin[0] if by_pin else next(iter(localities.values())))


@dataclass
class Result:
    matched: list = field(default_factory=list)  # (complex, society)
    proposed: list = field(default_factory=list)  # (complex, society or None on dry run)
    already: int = 0


def import_projects(groups: dict, *, user=None, dry_run=False) -> Result:
    localities = {l.name: l for l in Locality.objects.all()}
    if not localities:
        raise ValueError("No localities yet; seed the micro-market first")
    res = Result()
    with transaction.atomic():
        for c in groups.values():
            rera_nos = sorted({p["rera_no"] for p in c.projects})
            existing = Society.objects.filter(rera_project_nos__overlap=rera_nos).first()
            if existing:
                res.already += 1
                target = existing
            else:
                loc = _locality_for(c, localities)
                # Name only: societies on record have no pin code yet, and the area is only a guess from the
                # pin code. Link only a near-exact name with no close runner-up; ops sorts out the rest.
                cands = dedupe.find_candidates(c.name)
                best = cands[0] if cands else None
                runner = cands[1].signals.get("name", 0) if len(cands) > 1 else 0
                sure = (
                    best
                    and best.signals.get("name", 0) >= NAME_SURE
                    and best.signals["name"] - runner >= 0.05
                    # Same words once place names ("Thane") and filler are dropped: "Hiranandani Westgate" is
                    # not "Hiranandani Estate", however close the spelling.
                    and _key(c.name) == _key(best.society.canonical_name)
                )
                target = best.society if sure else None
                if target is None:
                    if dry_run:
                        res.proposed.append((c, None))
                        continue
                    target = Society.objects.create(
                        canonical_name=c.name,
                        kind=Society.Kind.PROJECT,
                        locality=loc,
                        location=loc.centroid,
                        pincode=c.pincode,
                        status=Society.Status.PROVISIONAL,
                        rera_project_nos=rera_nos,
                        provenance={
                            "source": "maharera",
                            "location_approx": True,
                            "promoters": sorted({p["promoter"] for p in c.projects if p["promoter"]}),
                            "rera_buildings": sorted(c.buildings),
                            "projects": c.projects,
                        },
                    )
                    audit(user, "society.proposed", target, {"source": "maharera", "rera_nos": rera_nos})
                    queue_for_admin(
                        "provisional_society",
                        target,
                        f"From MahaRERA: {c.name} ({len(rera_nos)} project{'s' if len(rera_nos) > 1 else ''}, {c.pincode})",
                        {"candidates": [x.as_dict() for x in cands[:3]], "source": "maharera"},
                    )
                    res.proposed.append((c, target))
                    continue
                res.matched.append((c, target))
            if dry_run:
                continue
            new = [n for n in rera_nos if n not in target.rera_project_nos]
            if new:
                target.rera_project_nos = sorted({*target.rera_project_nos, *new})
                prov = dict(target.provenance or {})
                known = {p["rera_no"] for p in prov.get("rera_projects", [])}
                prov["rera_projects"] = prov.get("rera_projects", []) + [p for p in c.projects if p["rera_no"] not in known]
                prov["rera_buildings"] = sorted({*prov.get("rera_buildings", []), *c.buildings})
                target.provenance = prov
                if not target.pincode:
                    target.pincode = c.pincode
                target.save(update_fields=["rera_project_nos", "provenance", "pincode"])
                audit(user, "society.rera_linked", target, {"rera_nos": new})
        if dry_run:
            transaction.set_rollback(True)
    return res
