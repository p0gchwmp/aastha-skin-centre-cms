"""Startup wiring for the exact-page simple editor.

Kept separate from the block definitions so Django migration imports remain
side-effect free and startup failures are easy to isolate.
"""

from __future__ import annotations

from copy import deepcopy

from django.conf import settings
from django.core.exceptions import FieldDoesNotExist
from django.db import models
from wagtail.admin.panels import FieldPanel, HelpPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.images import get_image_model_string

from .exact_editor import (
    ExactImageStreamBlock,
    ExactLinkStreamBlock,
    ExactTextStreamBlock,
    MAIN_RE,
    _page_for_response,
    apply_exact_editor_overrides,
    apply_page_media_slots,
    normalise_path,
)


_CONFIGURED = False


def _has_model_field(model, name: str) -> bool:
    try:
        model._meta.get_field(name)
    except FieldDoesNotExist:
        return False
    return True


def _page_models():
    from .models import (
        BlogPage,
        ClinicPage,
        ConditionPage,
        ContentIndexPage,
        DoctorPage,
        HomePage,
        StandardPage,
        TreatmentPage,
    )

    return (
        HomePage,
        ContentIndexPage,
        ConditionPage,
        TreatmentPage,
        StandardPage,
        BlogPage,
        DoctorPage,
        ClinicPage,
    )


def _make_existing_hero_field_obvious(model) -> None:
    panels = deepcopy(list(model.content_panels))
    for panel in panels:
        field_names = {
            getattr(child, "field_name", "")
            for child in getattr(panel, "children", [])
        }
        if "hero_image" not in field_names:
            continue
        panel.heading = "Main page introduction and hero image"
        panel.classname = ""
        panel.help_text = (
            "The Hero image chooser replaces the current main illustration or "
            "photograph in both Exact design and Full builder modes."
        )
        break
    model.content_panels = panels


def configure_exact_content_editor() -> None:
    global _CONFIGURED
    if _CONFIGURED:
        return

    from .models import ExactPageLayout, HomePage

    if not _has_model_field(ExactPageLayout, "editable_text"):
        StreamField(
            ExactTextStreamBlock(),
            blank=True,
            use_json_field=True,
            help_text="Visible text in page order. Open only the item to change.",
        ).contribute_to_class(ExactPageLayout, "editable_text")
    if not _has_model_field(ExactPageLayout, "editable_images"):
        StreamField(
            ExactImageStreamBlock(),
            blank=True,
            use_json_field=True,
            help_text="Existing page images in page order.",
        ).contribute_to_class(ExactPageLayout, "editable_images")
    if not _has_model_field(ExactPageLayout, "editable_links"):
        StreamField(
            ExactLinkStreamBlock(),
            blank=True,
            use_json_field=True,
            help_text="Existing buttons and links in page order.",
        ).contribute_to_class(ExactPageLayout, "editable_links")

    if not _has_model_field(HomePage, "doctor_section_image"):
        models.ForeignKey(
            get_image_model_string(),
            null=True,
            blank=True,
            on_delete=models.SET_NULL,
            related_name="+",
            help_text=(
                "Replaces the doctor illustration in the Meet your dermatologist "
                "section on the homepage."
            ),
        ).contribute_to_class(HomePage, "doctor_section_image")

    for page_model in _page_models():
        _make_existing_hero_field_obvious(page_model)

    home_panels = list(HomePage.content_panels)
    if not any(
        "doctor_section_image"
        in {
            getattr(child, "field_name", "")
            for child in getattr(panel, "children", [])
        }
        for panel in home_panels
    ):
        home_panels.insert(
            2 if len(home_panels) >= 2 else len(home_panels),
            MultiFieldPanel(
                [FieldPanel("doctor_section_image")],
                heading="Homepage doctor section image",
                help_text=(
                    "Choose the real Dr. Cheena Langer photograph that should "
                    "replace the illustrated doctor card."
                ),
            ),
        )
        HomePage.content_panels = home_panels

    ExactPageLayout.panels = [
        MultiFieldPanel(
            [FieldPanel("path"), FieldPanel("enabled")],
            heading="Page",
        ),
        HelpPanel(
            content=(
                "<p><strong>Simple editor:</strong> change wording, photographs "
                "and button/link destinations below. The tested design, spacing, "
                "mobile layout and typography stay intact.</p>"
            )
        ),
        MultiFieldPanel(
            [FieldPanel("editable_text")],
            heading="Text",
            help_text="Items are shown in the same order as the public page.",
        ),
        MultiFieldPanel(
            [FieldPanel("editable_images")],
            heading="Images",
            help_text="Choose only the images that need replacing.",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [FieldPanel("editable_links")],
            heading="Buttons and links",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [FieldPanel("html")],
            heading="Advanced source HTML — administrators only",
            help_text=(
                "Normal edits should use the fields above. Editing source HTML "
                "can break the verified layout."
            ),
            classname="collapsible collapsed",
        ),
    ]
    ExactPageLayout._meta.verbose_name = "editable page content"
    ExactPageLayout._meta.verbose_name_plural = "editable page content"

    middleware_path = "home.exact_editor_setup.ExactContentEditorMiddleware"
    middleware = list(settings.MIDDLEWARE)
    if middleware_path not in middleware:
        try:
            position = middleware.index("home.middleware.SmartTokenMiddleware") + 1
        except ValueError:
            position = len(middleware)
        middleware.insert(position, middleware_path)
        settings.MIDDLEWARE = middleware

    _CONFIGURED = True


class ExactContentEditorMiddleware:
    """Apply simple editor values after the verified main layout is rendered."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        content_type = response.get("Content-Type", "")
        if (
            response.status_code != 200
            or getattr(response, "streaming", False)
            or "text/html" not in content_type
        ):
            return response

        try:
            charset = getattr(response, "charset", "utf-8")
            body = response.content.decode(charset)
        except (AttributeError, UnicodeDecodeError):
            return response
        if 'id="main-content"' not in body and "id='main-content'" not in body:
            return response

        page = _page_for_response(request, response)
        if page is None or getattr(page, "layout_mode", "hybrid") == "builder":
            return response

        from .models import ExactPageLayout

        public_path = normalise_path(getattr(page, "url", "") or request.path_info)
        layout = ExactPageLayout.objects.filter(
            path=public_path,
            enabled=True,
        ).first()
        if layout is None:
            return response

        match = MAIN_RE.search(body)
        if not match:
            return response
        main = match.group("main")
        updated = apply_page_media_slots(main, page)
        updated = apply_exact_editor_overrides(updated, layout)
        if updated == main:
            return response

        body = body[: match.start("main")] + updated + body[match.end("main"):]
        response.content = body.encode(charset)
        if response.has_header("Content-Length"):
            del response["Content-Length"]
        return response
