from django.core.management.base import BaseCommand
from datetime import date
from django.db.models import Exists, OuterRef

from society.models import Society, MaintenanceBill
from society.services import generate_monthly_maintenance_bill


class Command(BaseCommand):
    help = "Automatically generate monthly maintenance bills for all active societies"

    def handle(self, *args, **kwargs):

        today = date.today()
        billing_month = today.replace(day=1)

        self.stdout.write("Running maintenance billing scheduler...")

        societies = Society.objects.all()

        for society in societies:

            # Prevent duplicate billing
            already_generated = MaintenanceBill.objects.filter(
                society=society,
                billing_month=billing_month
            ).exists()

            if already_generated:
                continue
            if not society.flats.exists():
                continue

            if not society.maintenance_charges.filter(is_active=True).exists():
                continue
            
            try:
                generate_monthly_maintenance_bill(
                    society=society,
                    billing_month=billing_month
                )

                self.stdout.write(
                    self.style.SUCCESS(
                        f"Billing generated for {society.name}"
                    )
                )

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f"Billing failed for {society.name}: {str(e)}"
                    )
                )

        self.stdout.write("Maintenance billing scheduler finished.")
