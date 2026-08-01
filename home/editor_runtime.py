"""Install the extended block definitions after Django has loaded all apps.

Importing Wagtail block modules from ``home.__init__`` is too early: Django is
still constructing the app registry at that point. StreamField keeps its source
block definition in ``block_types_arg`` and materialises ``stream_block`` as a
cached property, so the safe integration point is ``AppConfig.ready``.
"""

from __future__ import annotations

from wagtail.fields import StreamField

from .editor_extensions import (
    ExtendedPageAdditionStreamBlock,
    ExtendedPageBodyStreamBlock,
)


_CONFIGURED = False


def _replace_stream_definition(field: StreamField, block_class) -> None:
    """Replace a StreamField definition and clear any previously cached block."""

    field.block_types_arg = block_class
    field.block_lookup = None
    field.__dict__.pop("stream_block", None)
    # Materialise once during startup so configuration problems fail early and
    # every subsequent form/render operation uses the same immutable definition.
    field.stream_block


def configure_extended_editor_streams() -> None:
    """Upgrade every editable field to the extended, backwards-compatible set."""

    global _CONFIGURED
    if _CONFIGURED:
        return

    from .models import (
        BlogPage,
        ClinicPage,
        ConditionPage,
        ContentIndexPage,
        DoctorPage,
        HomePage,
        ReusableSection,
        StandardPage,
        TreatmentPage,
    )

    page_models = (
        HomePage,
        ContentIndexPage,
        ConditionPage,
        TreatmentPage,
        StandardPage,
        BlogPage,
        DoctorPage,
        ClinicPage,
    )

    for model in page_models:
        _replace_stream_definition(
            model._meta.get_field("body"),
            ExtendedPageBodyStreamBlock,
        )
        _replace_stream_definition(
            model._meta.get_field("layout_additions"),
            ExtendedPageAdditionStreamBlock,
        )

    _replace_stream_definition(
        ReusableSection._meta.get_field("body"),
        ExtendedPageBodyStreamBlock,
    )
    _CONFIGURED = True
