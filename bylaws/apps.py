from django.apps import AppConfig


class BylawsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "bylaws"

    def ready(self):
        import bylaws.signals
