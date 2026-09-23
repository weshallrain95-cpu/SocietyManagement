from django.apps import AppConfig


class MarketplaceConfig(AppConfig):
    name = "apps.marketplace"
    label = "marketplace"

    def ready(self):
        from . import handlers  # noqa: F401
