from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"

    def ready(self):
        # Register snippet-to-page automation only after Django has loaded all
        # models. Importing here avoids circular imports during migrations.
        from . import signals  # noqa: F401
