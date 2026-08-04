"""Simple, safe editing for the content inside verified exact-page layouts.

The public website keeps its tested HTML and responsive geometry. Editors can
change visible text nodes, links and images without touching HTML or switching
the whole page to builder mode. The implementation also connects the normal
page hero-image field to exact layouts, so the image chooser has an immediate
and predictable effect on the live page.
"""

from __future__ import annotations

from copy import deepcopy
from html import escape, unescape
import re
from urllib.parse import urlsplit

from django import forms
from django.conf import settings
from django.db import models
from django.utils.html import strip_tags
from wagtail import blocks
from wagtail.admin.panels import FieldPanel, HelpPanel, MultiFieldPanel
from wagtail.fields import StreamField
from wagtail.images import get_image_model, get_image_model_string
from wagtail.images.blocks import ImageChooserBlock
from wagtail.models import Page, Site


TEXT_NODE_RE = re.compile(r">(?P<text>[^<>]+)<", re.DOTALL)
IMG_TAG_RE = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
ANCHOR_RE = re.compile(
    r"<a\b(?P<attrs>[^>]*)>(?P<body>.*?)</a>",
    re.IGNORECASE | re.DOTALL,
)
ANCHOR_START_RE = re.compile(r"<a\b[^>]*>", re.IGNORECASE)
MAIN_RE = re.compile(
    r"(?P<main><main\b(?=[^>]*\bid=(?P<quote>[\"'])main-content(?P=quote))"
    r"[^>]*>.*?</main>)",
    re.IGNORECASE | re.DOTALL,
)
HERO_SECTION_RE = re.compile(
    r"(?P<section><section\b(?=[^>]*\bclass=(?P<quote>[\"'])"
    r"[^\"']*\b(?:page-hero|home-hero|hero-section)\b[^\"']*(?P=quote))"
    r"[^>]*>.*?</section>)",
    re.IGNORECASE | re.DOTALL,
)
ATTRIBUTE_RE_TEMPLATE = r"\s{attribute}\s*=\s*([\"']).*?\1"
SRC_RE = re.compile(r"\ssrc\s*=\s*([\"'])(?P<value>.*?)\1", re.IGNORECASE)
ALT_RE = re.compile(r"\salt\s*=\s*([\"'])(?P<value>.*?)\1", re.IGNORECASE)
HREF_RE = re.compile(r"\shref\s*=\s*([\"'])(?P<value>.*?)\1", re.IGNORECASE)


class ExactTextNodeBlock(blocks.StructBlock):
    node_index = blocks.IntegerBlock(widget=forms.HiddenInput())
    label = blocks.CharBlock(widget=forms.HiddenInput())
    original_text = blocks.TextBlock(widget=forms.HiddenInput())
    text = blocks.TextBlock(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3}),
        help_text="Edit the visible wording. Styling and layout are preserved.",
    )

    class Meta:
        icon = "pilcrow"
        label = "Text"
        collapsed = True
        label_format = "{label}"


class ExactImageElementBlock(blocks.StructBlock):
    image_index = blocks.IntegerBlock(widget=forms.HiddenInput())
    label = blocks.CharBlock(widget=forms.HiddenInput())
    original_src = blocks.CharBlock(required=False, widget=forms.HiddenInput())
    image = ImageChooserBlock(
        required=False,
        help_text="Choose a replacement. Leave empty to keep the current image.",
    )
    alt_text = blocks.CharBlock(
        required=False,
        max_length=220,
        help_text=(
            "Describe the image for accessibility. Leave blank only when it is "
            "purely decorative."
        ),
    )

    class Meta:
        icon = "image"
        label = "Image"
        collapsed = True
        label_format = "{label}"


class ExactLinkElementBlock(blocks.StructBlock):
    link_index = blocks.IntegerBlock(widget=forms.HiddenInput())
    label = blocks.CharBlock(widget=forms.HiddenInput())
    original_url = blocks.CharBlock(required=False, widget=forms.HiddenInput())
    url = blocks.CharBlock(
        required=False,
        max_length=1000,
        help_text=(
            "Use a page path such as /treatments/, a full https:// link, tel:, "
            "mailto: or a #section link."
        ),
    )

    class Meta:
        icon = "link"
        label = "Link"
        collapsed = True
        label_format = "{label}"


class ExactTextStreamBlock(blocks.StreamBlock):
    text = ExactTextNodeBlock()


class ExactImageStreamBlock(blocks.StreamBlock):
    image = ExactImageElementBlock()


class ExactLinkStreamBlock(blocks.StreamBlock):
    link = ExactLinkElementBlock()


_CONFIGURED = False


def _has_model_field(model, name: str) -> bool:
    try:
        model._meta.get_field(name)
    except models.FieldDoesNotExist:
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
    """Open the existing introduction/hero panel and explain its live effect."""

    panels = deepcopy(list(model.content_panels))
    for panel in panels:
        children = getattr(panel, "children", [])
        field_names = {
            getattr(child, "field_name", "")
            for child in children
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
    """Install fields, panels and middleware after Django loads all models."""

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
        insert_at = 2 if len(home_panels) >= 2 else len(home_panels)
        home_panels.insert(
            insert_at,
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

    middleware_path = "home.exact_editor.ExactContentEditorMiddleware"
    middleware = list(settings.MIDDLEWARE)
    if middleware_path not in middleware:
        try:
            position = middleware.index("home.middleware.SmartTokenMiddleware") + 1
        except ValueError:
            position = len(middleware)
        middleware.insert(position, middleware_path)
        settings.MIDDLEWARE = middleware

    _CONFIGURED = True


def _clean_visible_text(raw: str) -> str:
    return " ".join(unescape(raw).split())


def extract_exact_editor_payload(source: str) -> dict[str, list[dict]]:
    """Extract stable, human-readable edit rows from one exact main element."""

    text_items: list[dict] = []
    text_index = 0
    for match in TEXT_NODE_RE.finditer(source or ""):
        cleaned = _clean_visible_text(match.group("text"))
        if not cleaned:
            continue
        label_text = cleaned if len(cleaned) <= 88 else cleaned[:85].rstrip() + "…"
        text_items.append(
            {
                "node_index": text_index,
                "label": f"Text {text_index + 1} — {label_text}",
                "original_text": cleaned,
                "text": cleaned,
            }
        )
        text_index += 1

    image_items: list[dict] = []
    for image_index, match in enumerate(IMG_TAG_RE.finditer(source or "")):
        tag = match.group(0)
        src_match = SRC_RE.search(tag)
        alt_match = ALT_RE.search(tag)
        src = unescape(src_match.group("value")) if src_match else ""
        alt = unescape(alt_match.group("value")) if alt_match else ""
        filename = src.rsplit("/", 1)[-1] or "current image"
        label = alt.strip() or filename
        image_items.append(
            {
                "image_index": image_index,
                "label": f"Image {image_index + 1} — {label[:90]}",
                "original_src": src,
                "image": None,
                "alt_text": alt,
            }
        )

    link_items: list[dict] = []
    for link_index, match in enumerate(ANCHOR_RE.finditer(source or "")):
        href_match = HREF_RE.search(match.group("attrs"))
        if not href_match:
            continue
        url = unescape(href_match.group("value"))
        link_text = _clean_visible_text(strip_tags(match.group("body")))
        label_text = link_text or url
        link_items.append(
            {
                "link_index": link_index,
                "label": f"Link {link_index + 1} — {label_text[:90]}",
                "original_url": url,
                "url": url,
            }
        )

    return {
        "editable_text": text_items,
        "editable_images": image_items,
        "editable_links": link_items,
    }


def sync_exact_layout_editor_fields(layout) -> list[str]:
    """Populate empty simple-editor fields without overwriting later edits."""

    payload = extract_exact_editor_payload(layout.html)
    updates: list[str] = []
    for field_name, block_type in (
        ("editable_text", "text"),
        ("editable_images", "image"),
        ("editable_links", "link"),
    ):
        current = getattr(layout, field_name)
        if current:
            continue
        setattr(
            layout,
            field_name,
            [(block_type, value) for value in payload[field_name]],
        )
        updates.append(field_name)
    if updates:
        layout.save(update_fields=updates)
    return updates


def sync_all_exact_layout_editor_fields() -> int:
    from .models import ExactPageLayout

    updated = 0
    for layout in ExactPageLayout.objects.all().iterator():
        if sync_exact_layout_editor_fields(layout):
            updated += 1
    return updated


def sync_uploaded_homepage_images() -> list[str]:
    """Connect the two newest uploaded 'dr cheena langer' images once.

    The first of the two most recent uploads becomes the homepage hero image;
    the second becomes the doctor-section image and the reusable Doctor photo.
    Existing editor selections are never overwritten.
    """

    from .models import Doctor, HomePage

    image_model = get_image_model()
    matches = list(
        image_model.objects.filter(title__iexact="dr cheena langer")
        .order_by("-id")[:2]
    )
    if len(matches) < 2:
        matches = list(
            image_model.objects.filter(title__icontains="dr cheena langer")
            .order_by("-id")[:2]
        )
    if not matches:
        return []

    matches.reverse()
    hero_image = matches[0]
    doctor_image = matches[1] if len(matches) > 1 else matches[0]
    updates: list[str] = []

    home = HomePage.objects.first()
    if home is not None:
        changed = False
        if not home.hero_image_id:
            home.hero_image = hero_image
            updates.append("homepage hero image")
            changed = True
        if not home.doctor_section_image_id:
            home.doctor_section_image = doctor_image
            updates.append("homepage doctor image")
            changed = True
        if changed:
            home.save()
            home.save_revision().publish()

    doctor = Doctor.objects.filter(slug="dr-cheena-langer").first()
    if doctor is not None and not doctor.photo_id:
        doctor.photo = doctor_image
        doctor.save()
        doctor.save_revision().publish()
        updates.append("doctor profile image")

    return updates


def _stream_values(stream, block_type: str):
    for bound_block in stream or []:
        if getattr(bound_block, "block_type", "") != block_type:
            continue
        value = getattr(bound_block, "value", None)
        if hasattr(value, "get"):
            yield value


def _replace_attribute(tag: str, attribute: str, value: str) -> str:
    pattern = re.compile(
        ATTRIBUTE_RE_TEMPLATE.format(attribute=re.escape(attribute)),
        re.IGNORECASE,
    )
    safe_value = escape(str(value), quote=True)
    if pattern.search(tag):
        return pattern.sub(f' {attribute}="{safe_value}"', tag, count=1)
    return tag[:-1] + f' {attribute}="{safe_value}">'


def _remove_attribute(tag: str, attribute: str) -> str:
    return re.sub(
        ATTRIBUTE_RE_TEMPLATE.format(attribute=re.escape(attribute)),
        "",
        tag,
        flags=re.IGNORECASE,
    )


def _renditions(image):
    try:
        standard = image.get_rendition("max-900x900|format-webp")
        large = image.get_rendition("max-1600x1600|format-webp")
        return standard, large
    except (AttributeError, OSError, ValueError):
        fallback = type(
            "ImageAsset",
            (),
            {
                "url": image.file.url,
                "width": getattr(image, "width", 0) or 0,
                "height": getattr(image, "height", 0) or 0,
            },
        )()
        return fallback, fallback


def replace_image_tag(tag: str, image, alt_text: str = "") -> str:
    standard, large = _renditions(image)
    output = tag
    for attribute in ("src", "srcset", "sizes", "width", "height", "alt"):
        output = _remove_attribute(output, attribute)
    output = _replace_attribute(output, "src", standard.url)
    if large.url != standard.url:
        output = _replace_attribute(
            output,
            "srcset",
            f"{standard.url} {standard.width}w, {large.url} {large.width}w",
        )
        output = _replace_attribute(
            output,
            "sizes",
            "(max-width: 760px) 92vw, 46vw",
        )
    if standard.width:
        output = _replace_attribute(output, "width", str(standard.width))
    if standard.height:
        output = _replace_attribute(output, "height", str(standard.height))
    output = _replace_attribute(output, "alt", alt_text)
    return output


def _apply_text_overrides(source: str, layout) -> str:
    overrides = {
        int(value.get("node_index")): value
        for value in _stream_values(layout.editable_text, "text")
        if value.get("text") != value.get("original_text")
    }
    if not overrides:
        return source

    visible_index = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal visible_index
        raw = match.group("text")
        cleaned = _clean_visible_text(raw)
        if not cleaned:
            return match.group(0)
        current_index = visible_index
        visible_index += 1
        override = overrides.get(current_index)
        if override is None:
            return match.group(0)
        leading = raw[: len(raw) - len(raw.lstrip())]
        trailing = raw[len(raw.rstrip()):]
        replacement = escape(str(override.get("text") or ""))
        return ">" + leading + replacement + trailing + "<"

    return TEXT_NODE_RE.sub(replace, source)


def _apply_image_overrides(source: str, layout) -> str:
    overrides = {
        int(value.get("image_index")): value
        for value in _stream_values(layout.editable_images, "image")
        if value.get("image")
    }
    if not overrides:
        return source

    image_index = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal image_index
        current_index = image_index
        image_index += 1
        override = overrides.get(current_index)
        if override is None:
            return match.group(0)
        return replace_image_tag(
            match.group(0),
            override.get("image"),
            str(override.get("alt_text") or ""),
        )

    return IMG_TAG_RE.sub(replace, source)


def _apply_link_overrides(source: str, layout) -> str:
    overrides = {
        int(value.get("link_index")): value
        for value in _stream_values(layout.editable_links, "link")
        if value.get("url") != value.get("original_url")
    }
    if not overrides:
        return source

    link_index = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal link_index
        current_index = link_index
        link_index += 1
        override = overrides.get(current_index)
        if override is None:
            return match.group(0)
        return _replace_attribute(
            match.group(0),
            "href",
            str(override.get("url") or "#"),
        )

    return ANCHOR_START_RE.sub(replace, source)


def apply_exact_editor_overrides(source: str, layout) -> str:
    output = _apply_text_overrides(source, layout)
    output = _apply_image_overrides(output, layout)
    return _apply_link_overrides(output, layout)


def _replace_named_image(source: str, filename: str, image, alt_text: str) -> str:
    if not image:
        return source
    replaced = False

    def replace(match: re.Match[str]) -> str:
        nonlocal replaced
        tag = match.group(0)
        src_match = SRC_RE.search(tag)
        src = src_match.group("value") if src_match else ""
        if replaced or not src.lower().endswith(filename.lower()):
            return tag
        replaced = True
        return replace_image_tag(tag, image, alt_text)

    return IMG_TAG_RE.sub(replace, source)


def apply_page_media_slots(source: str, page) -> str:
    """Connect ordinary Wagtail image choosers to exact-layout placeholders."""

    output = source
    hero_image = getattr(page, "hero_image", None)
    if hero_image:
        hero_replaced = False

        def replace_hero_section(match: re.Match[str]) -> str:
            nonlocal hero_replaced
            section = match.group("section")
            if hero_replaced:
                return section
            updated, count = IMG_TAG_RE.subn(
                lambda image_match: replace_image_tag(
                    image_match.group(0),
                    hero_image,
                    getattr(page, "title", ""),
                ),
                section,
                count=1,
            )
            hero_replaced = bool(count)
            return updated

        output = HERO_SECTION_RE.sub(replace_hero_section, output, count=1)
        if not hero_replaced:
            output = _replace_named_image(
                output,
                "hero-care.svg",
                hero_image,
                getattr(page, "title", ""),
            )

    doctor_image = getattr(page, "doctor_section_image", None)
    if not doctor_image:
        from .models import Doctor

        doctor = Doctor.objects.filter(
            slug="dr-cheena-langer",
            is_active=True,
            live=True,
        ).first()
        doctor_image = doctor.photo if doctor else None
    if doctor_image:
        output = _replace_named_image(
            output,
            "doctor-care.svg",
            doctor_image,
            "Dr. Cheena Langer, consultant dermatologist",
        )
    return output


def normalise_path(value: str) -> str:
    path = urlsplit(value or "/").path or "/"
    if not path.startswith("/"):
        path = "/" + path
    if path != "/" and not path.endswith("/"):
        path += "/"
    return path


def _page_for_response(request, response):
    context = getattr(response, "context_data", None) or {}
    page = context.get("page") if hasattr(context, "get") else None
    if page is not None:
        return page.specific

    site = Site.find_for_request(request)
    if site is None:
        return None
    relative = request.path_info.strip("/")
    url_path = site.root_page.url_path
    if relative:
        url_path += relative + "/"
    return Page.objects.filter(url_path=url_path).specific().first()


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
            body = response.content.decode(getattr(response, "charset", "utf-8"))
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
        response.content = body.encode(getattr(response, "charset", "utf-8"))
        response.pop("Content-Length", None)
        return response
