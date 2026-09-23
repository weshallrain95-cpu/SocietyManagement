from django.core.management.base import BaseCommand

from apps.masterdata.location import compute_for_building
from apps.masterdata.models import Building


class Command(BaseCommand):
    help = "Recompute distance facts for all buildings (run after POI data changes)."

    def handle(self, **_):
        n = 0
        for b in Building.objects.filter(merged_into__isnull=True).iterator():
            compute_for_building(b)
            n += 1
        self.stdout.write(self.style.SUCCESS(f"Location facts computed for {n} buildings"))
