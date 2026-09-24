"""Load an official list of flats (TMC property-tax register extract, MahaRERA, IGR) and work out each wing's layout.

python manage.py import_flat_register tmc-ward-majiwada.xlsx --source tmc --dry-run
python manage.py import_flat_register rodas.csv --source tmc --society "Hiranandani Estate"
python manage.py import_flat_register partial.csv --source igr --partial   # not every flat is listed

Columns (any order, English or Marathi headings): Society, Wing, Flat no, Floor, Carpet area, Property no, Ward.
Owner names, phone numbers and other personal columns are ignored and never stored.
Template: tools/building-layouts/flat-register-template.xlsx
"""

from pathlib import Path

from django.core.management.base import BaseCommand, CommandError

from apps.masterdata import dedupe
from apps.masterdata.registers import import_register


class Command(BaseCommand):
    help = "Import an official flat register and derive wing layouts (floors, flats per floor, refuge floors)."

    def add_arguments(self, parser):
        parser.add_argument("path")
        parser.add_argument("--source", required=True, choices=["tmc", "rera", "igr", "ops"])
        parser.add_argument("--society", help="Every row belongs to this society (when the file has no society column)")
        parser.add_argument("--partial", action="store_true", help="The file does not list every flat of each wing")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, path, source, society, partial, dry_run, **_):
        p = Path(path)
        if not p.exists():
            raise CommandError(f"{p} not found")
        soc = None
        if society:
            d = dedupe.decide(dedupe.find_candidates(society))
            if d.action != "auto":
                raise CommandError(f"Society {society!r} not found in our master data")
            soc = d.best.society
        try:
            res = import_register(p.name, p.read_bytes(), source=source, complete=not partial, dry_run=dry_run, society=soc)
        except ValueError as e:
            raise CommandError(str(e))
        style = self.style.SUCCESS if not res.unmatched else self.style.WARNING
        self.stdout.write(
            style(
                f"{'DRY RUN ' if dry_run else ''}wings: {res.wings}, new flats: {res.flats_new}, "
                f"already known: {res.flats_known}, unmatched societies: {len(res.unmatched)}"
            )
        )
        for w in res.layouts:
            skip = f", no flats on {w['skip_floors']}" if w["skip_floors"] else ""
            extra = f", extra {w['extra_unit_nos']}" if w["extra_unit_nos"] else ""
            self.stdout.write(
                f"  {w['society']} / {w['wing']}: floors {w['lowest_floor']}–{w['floors_total']}, "
                f"{w['units_per_floor']} per floor{skip}{extra} ({w['flats']} flats)"
            )
        if res.ignored_columns:
            self.stdout.write(f"  ignored columns (never stored): {', '.join(map(str, res.ignored_columns))}")
        for line in res.unmatched:
            self.stdout.write(f"  unmatched: {line}")
