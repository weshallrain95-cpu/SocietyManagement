from django.core.management.base import BaseCommand
from society_product.engines.communications_engine import CommunicationsEngine


class Command(BaseCommand):
    help = "Process pending notification events"

    def handle(self, *args, **kwargs):

        engine = CommunicationsEngine()

        processed = engine.process_queue()

        self.stdout.write(
            self.style.SUCCESS(
                f"Processed {processed} notification events"
            )
        )
        