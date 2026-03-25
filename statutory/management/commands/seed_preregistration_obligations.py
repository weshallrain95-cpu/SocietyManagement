from django.core.management.base import BaseCommand
from statutory.models import LegalStage, LegalObligation


class Command(BaseCommand):

    help = "Seed / update production-grade legal obligations"

    def handle(self, *args, **options):

        stage = LegalStage.objects.filter(
            name__icontains="Pre-Registration"
        ).first()

        if not stage:
            self.stdout.write(
                self.style.ERROR("Pre-Registration stage not found.")
            )
            return

        obligations = [

            (
            "Collect minimum 60% consent from flat purchasers",
            "Society formation requires consent from at least 60% of flat purchasers to initiate cooperative housing society registration."
            ),

            (
            "Form provisional promoter / managing committee",
            "A Chief Promoter and provisional managing committee must represent the proposed society during registration."
            ),

            (
            "Decide and reserve proposed society name",
            "A unique proposed society name must be finalized before filing the registration application."
            ),

        ]

        for index, (title, purpose) in enumerate(obligations, start=1):

            obj, created = LegalObligation.objects.update_or_create(
                legal_stage=stage,
                title=title,
                defaults={
                    "description": title,
                    "purpose": purpose,
                    "reference_law": "MCS Act, 1960 / MCS Rules, 1961",
                    "is_mandatory": True,
                    "sequence_order": index,
                }
            )
            if created:
                self.stdout.write(f"Created: {title}")
            else:
                self.stdout.write(f"Updated: {title}")

        self.stdout.write(
            self.style.SUCCESS("Pre-registration obligations synchronized.")
        )

