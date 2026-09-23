from django.apps import AppConfig


class StatusConfig(AppConfig):
    name = "apps.status"
    label = "status"

    def ready(self):
        from . import handlers  # noqa: F401
