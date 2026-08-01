from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"

    def ready(self):
        # Register model automation and editor-only hook extensions after Django
        # has loaded all models. Importing here avoids circular imports during
        # migrations while keeping the hook modules explicit and testable.
        from . import admin_extensions, signals  # noqa: F401
