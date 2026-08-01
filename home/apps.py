from django.apps import AppConfig


class HomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "home"

    def ready(self):
        # Django has loaded every model at this point, so Wagtail StreamField
        # definitions can be upgraded without importing model-backed block
        # modules during app-registry construction.
        from .editor_runtime import configure_extended_editor_streams

        configure_extended_editor_streams()

        # Register model automation and editor-only hook extensions after the
        # extended fields are ready.
        from . import admin_extensions, signals  # noqa: F401
