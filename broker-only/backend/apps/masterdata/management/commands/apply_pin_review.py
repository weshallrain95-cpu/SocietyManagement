"""Apply the pilot broker's pin-review answers (exported from the pin-check page's store).

python manage.py apply_pin_review /path/to/pins/        # a folder of <society-slug>.json files
python manage.py apply_pin_review pins.json --dry-run    # or one JSON list
"""

import json
import re
from pathlib import Path

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.masterdata import dedupe
from apps.masterdata.models import Society, SocietyAlias
from apps.masterdata.services import move_society_pin, parse_maps_link
from common.notify import queue_for_admin


def slug(name: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


class Command(BaseCommand):
    help = "Apply pin corrections and local names from the Thane West pin-check page."

    def add_arguments(self, parser):
        parser.add_argument("path")
        parser.add_argument("--dry-run", action="store_true")

    def handle(self, path, dry_run, **_):
        p = Path(path)
        rows = [json.loads(f.read_text()) | {"_id": f.stem} for f in sorted(p.rglob("*.json"))] if p.is_dir() else json.loads(p.read_text())
        by_slug = {slug(s.canonical_name): s for s in Society.objects.filter(status="active")}
        stats = {"confirmed": 0, "moved": 0, "needs_ops": 0, "aliases": 0, "unknown": 0}
        with transaction.atomic():
            for r in rows:
                r = r.get("data", r)  # accept raw store exports and plain documents
                soc = by_slug.get(r.get("_id") or "") or by_slug.get(slug(r.get("society", "")))
                if soc is None:
                    stats["unknown"] += 1
                    continue
                for alias in [a.strip() for a in str(r.get("aliases", "")).split(",") if a.strip()]:
                    dedupe.learn_alias(soc, alias, SocietyAlias.Source.ADMIN)
                    stats["aliases"] += 1
                if r.get("status") == "correct":
                    prov = dict(soc.provenance or {}, verified=True, verified_by="pilot_broker_pin_review")
                    Society.objects.filter(pk=soc.pk).update(provenance=prov)
                    stats["confirmed"] += 1
                elif r.get("status") == "wrong":
                    point = parse_maps_link(r.get("link", "")) or (
                        parse_maps_link(f"{r['lat']},{r['lng']}") if r.get("lat") and r.get("lng") else None
                    )
                    if point is None:
                        queue_for_admin(
                            "pin_correction",
                            soc,
                            f"Pin reported wrong for {soc.canonical_name}; link needs checking",
                            {"link": r.get("link", "")},
                        )
                        stats["needs_ops"] += 1
                    else:
                        move_society_pin(soc, point, user=None, reason="pilot broker pin review")
                        stats["moved"] += 1
            if dry_run:
                transaction.set_rollback(True)
        self.stdout.write(self.style.SUCCESS(("DRY RUN " if dry_run else "") + ", ".join(f"{k}: {v}" for k, v in stats.items())))
