from django.apps import AppConfig


class LabConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "lab"

    def ready(self):
        import lab.signals  # noqa: F401
