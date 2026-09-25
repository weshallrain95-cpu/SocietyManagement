"""Load MahaRERA's public project list (from tools/maharera/fetch_projects.py) into the society universe.

python manage.py import_rera_projects ../tools/maharera/thane_projects.csv --dry-run
python manage.py import_rera_projects ../tools/maharera/thane_projects.csv

Only the pilot pin codes are loaded (apps/masterdata/rera.py PILOT_PINCODES). Known societies get their RERA
numbers; everything else becomes a provisional society in the ops review queue, pin flagged approximate.
"""

from django.core.management.base import BaseCommand

from apps.masterdata.rera import import_projects, read_projects
from common import rls


class Command(BaseCommand):
    help = "Import MahaRERA registered projects (public list) as societies to review."

    def add_arguments(self, parser):
        parser.add_argument("path")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, path, dry_run, **_):
        groups = read_projects(path)
        with rls.platform_context():
            res = import_projects(groups, dry_run=dry_run)
        n_proj = sum(len(g.projects) for g in groups.values())
        self.stdout.write(f"{n_proj} projects in the pilot pin codes, grouped into {len(groups)} complexes")
        self.stdout.write(f"  linked to societies already on record: {len(res.matched) + res.already}")
        for c, s in res.matched[:40]:
            self.stdout.write(f"    {c.name} -> {s.canonical_name}")
        self.stdout.write(f"  new provisional societies for ops review: {len(res.proposed)}")
        if dry_run:
            self.stdout.write(self.style.WARNING("Dry run: nothing saved"))
