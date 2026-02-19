from django.apps import AppConfig


class StatutoryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "statutory"

    def ready(self):
        # Force-load bylaws models so Django registers them
        import bylaws.models