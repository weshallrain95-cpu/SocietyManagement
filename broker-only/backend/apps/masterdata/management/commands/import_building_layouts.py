"""Load wings and flat layouts from a spreadsheet (MahaRERA extract, field survey, broker knowledge).

python manage.py import_building_layouts layouts.xlsx --dry-run
python manage.py import_building_layouts layouts.xlsx --mark-complete   # every wing of these societies is listed

Template: tools/building-layouts/building-layout-template.xlsx. Societies must already exist (matched by
name or known nickname); unmatched names are listed, never created.
"""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.audit.services import audit
from apps.inventory.upload import read_table
from apps.masterdata import dedupe
from apps.masterdata.layout import layout_dict
from apps.masterdata.models import Society
from apps.masterdata.services import get_or_create_building

COLUMNS = {
    "society": ("society", "society name", "project", "project name"),
    "wing": ("wing", "building", "tower", "wing / building"),
    "floors_total": ("floors", "total floors", "top floor", "no of floors"),
    "lowest_floor": ("first floor with flats", "lowest floor", "first residential floor"),
    "units_per_floor": ("flats per floor", "units per floor"),
    "skip_floors": ("floors with no flats", "refuge floors", "skip floors"),
    "extra_unit_nos": ("flats outside the pattern", "extra flats", "exceptions"),
    "source": ("source",),
    "verified": ("verified", "checked"),
    "rera_no": ("rera no", "rera", "rera project no", "maharera no"),
}
SOURCES = {"rera", "survey", "ops", "broker"}


def _num(v, label, row_no):
    if v in (None, ""):
        return None
    try:
        return int(float(str(v).strip()))
    except ValueError:
        raise ValueError(f"row {row_no}: {label} {v!r} is not a number") from None


def _list(v):
    return [x.strip() for x in str(v or "").replace(";", ",").split(",") if x.strip()]


class Command(BaseCommand):
    help = "Import wings and flat layouts (floors, flats per floor, refuge floors) from .xlsx or .csv."

    def add_arguments(self, parser):
        parser.add_argument("path")
        parser.add_argument("--dry-run", action="store_true")
        parser.add_argument("--mark-complete", action="store_true", help="Brokers can no longer add wings to these societies")

    def handle(self, path, dry_run, mark_complete, **_):
        p = Path(path)
        if not p.exists():
            raise CommandError(f"{p} not found")
        headers, rows = read_table(p.name, p.read_bytes())
        lookup = {h: key for key, names in COLUMNS.items() for h in headers if str(h).strip().lower() in names}
        if "society" not in lookup.values() or "wing" not in lookup.values():
            raise CommandError("The sheet needs at least 'Society' and 'Wing' columns")
        stats = {"wings_new": 0, "wings_updated": 0, "unmatched": [], "errors": []}
        seen: set = set()
        with transaction.atomic():
            for i, raw in enumerate(rows, start=2):
                r = {lookup[h]: v for h, v in raw.items() if h in lookup}
                name = str(r.get("society") or "").strip()
                if not name or name.lower().startswith("example"):
                    continue
                cands = dedupe.find_candidates(name)
                decision = dedupe.decide(cands)
                if decision.action != "auto":
                    stats["unmatched"].append(f"row {i}: {name}" + (f" (closest: {cands[0].society.canonical_name})" if cands else ""))
                    continue
                soc = decision.best.society
                try:
                    floors = _num(r.get("floors_total"), "Floors", i)
                    lowest = _num(r.get("lowest_floor"), "First floor with flats", i)
                    per = _num(r.get("units_per_floor"), "Flats per floor", i)
                    skip = [_num(x, "Floors with no flats", i) for x in _list(r.get("skip_floors"))]
                except ValueError as e:
                    stats["errors"].append(str(e))
                    continue
                existed = soc.buildings.filter(merged_into__isnull=True).count()
                b = get_or_create_building(soc, str(r.get("wing") or "").strip() or None)
                stats["wings_new" if soc.buildings.filter(merged_into__isnull=True).count() > existed else "wings_updated"] += 1
                before = layout_dict(b)
                b.floors_total = floors if floors is not None else b.floors_total
                b.lowest_floor = lowest if lowest is not None else b.lowest_floor
                b.units_per_floor = per if per is not None else b.units_per_floor
                b.skip_floors = skip or b.skip_floors
                b.extra_unit_nos = _list(r.get("extra_unit_nos")) or b.extra_unit_nos
                src = str(r.get("source") or "").strip().lower()
                b.layout_source = src if src in SOURCES else (b.layout_source or "ops")
                b.layout_verified = str(r.get("verified") or "").strip().lower() in ("yes", "y", "true", "1") and bool(
                    b.floors_total and b.units_per_floor
                )
                b.save()
                audit(None, "building.layout_imported", b, {"from": before, "to": layout_dict(b), "file": p.name}, actor_label="import")
                rera = str(r.get("rera_no") or "").strip().upper()
                if rera and rera not in soc.rera_project_nos:
                    soc.rera_project_nos = [*soc.rera_project_nos, rera[:20]]
                    soc.save(update_fields=["rera_project_nos"])
                seen.add(soc.pk)
            if mark_complete:
                Society.objects.filter(pk__in=seen).update(wings_complete=True)
            if dry_run:
                transaction.set_rollback(True)
        out = self.style.SUCCESS if not (stats["unmatched"] or stats["errors"]) else self.style.WARNING
        self.stdout.write(
            out(
                f"{'DRY RUN ' if dry_run else ''}societies: {len(seen)}, new wings: {stats['wings_new']}, "
                f"updated wings: {stats['wings_updated']}, unmatched: {len(stats['unmatched'])}, errors: {len(stats['errors'])}"
                + (", marked complete" if mark_complete else "")
            )
        )
        for line in stats["unmatched"] + stats["errors"]:
            self.stdout.write(f"  {line}")
