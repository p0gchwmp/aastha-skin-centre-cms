"""Render the verified static layout while retaining CMS-managed facts."""

from __future__ import annotations

from html import escape
import re
from urllib.parse import urlsplit

from django import template
from django.utils.safestring import mark_safe

from home.models import ExactPageLayout, SiteSettings


register = template.Library()
IMG_TAG = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
LOADING_ATTR = re.compile(r"\sloading\s*=\s*([\"']).*?\1", re.IGNORECASE)
DECODING_ATTR = re.compile(r"\sdecoding\s*=\s*([\"']).*?\1", re.IGNORECASE)
FETCHPRIORITY_ATTR = re.compile(
    r"\sfetchpriority\s*=\s*([\"']).*?\1", re.IGNORECASE
)


def normalise_path(value: str) -> str:
    path = urlsplit(value or "/").path or "/"
    if not path.startswith("/"):
        path = "/" + path
    if path != "/" and not path.endswith("/"):
        path += "/"
    return path


def _safe(value) -> str:
    return escape(str(value), quote=True)


def _append_img_attributes(tag: str, attributes: str) -> str:
    """Add attributes without reserialising the verified snapshot HTML."""
    if tag.endswith("/>"):
        return f"{tag[:-2]}{attributes} />"
    return f"{tag[:-1]}{attributes}>"


def optimise_image_delivery(source: str) -> str:
    """Keep the first content image eager and defer the remaining page images.

    The exact layout is stored as verified HTML. A narrow tag-level rewrite adds
    browser delivery hints while preserving element order, content, URLs and
    visual styling. Header/footer branding is rendered outside this snapshot.
    """

    image_index = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal image_index
        tag = match.group(0)
        is_first = image_index == 0
        image_index += 1

        tag = LOADING_ATTR.sub("", tag)
        tag = DECODING_ATTR.sub("", tag)
        tag = FETCHPRIORITY_ATTR.sub("", tag)
        if is_first:
            return _append_img_attributes(
                tag,
                ' loading="eager" decoding="async" fetchpriority="high"',
            )
        return _append_img_attributes(
            tag,
            ' loading="lazy" decoding="async"',
        )

    return IMG_TAG.sub(replace, source)


def apply_global_facts(source: str, site_settings: SiteSettings) -> str:
    """Replace facts that administrators manage centrally.

    The snapshot remains faithful for layout and content structure. Only clinic
    facts represented by explicit Wagtail settings and non-visual image-delivery
    hints are substituted. Medical credentials, experience statements and other
    clinical claims are intentionally left untouched and must be edited through
    the reviewed page content.
    """

    primary_digits = site_settings.primary_phone_digits[-10:]
    secondary_digits = site_settings.secondary_phone_digits[-10:]
    whatsapp_digits = "".join(
        character
        for character in site_settings.whatsapp_mobile
        if character.isdigit()
    )[-10:]
    fee = (
        f"{site_settings.currency_symbol}"
        f"{site_settings.consultation_fee:,.0f}"
    )
    follow_up_days = str(site_settings.follow_up_days)

    replacements = [
        (
            "https://wa.me/917006613362",
            f"https://wa.me/91{whatsapp_digits}",
        ),
        ("tel:+917006613362", f"tel:+91{primary_digits}"),
        ("tel:7006613362", f"tel:{primary_digits}"),
        ("tel:+919796676541", f"tel:+91{secondary_digits}"),
        ("tel:9796676541", f"tel:{secondary_digits}"),
        (
            "mailto:aasthaskinsurgs@gmail.com",
            f"mailto:{site_settings.email}",
        ),
        ("aasthaskinsurgs@gmail.com", site_settings.email),
        ("7006613362", site_settings.primary_mobile),
        ("9796676541", site_settings.secondary_mobile),
        ("₹500", fee),
        ("within 10 days", f"within {follow_up_days} days"),
        ("10-day period", f"{follow_up_days}-day period"),
    ]
    output = source
    for current, replacement in replacements:
        output = output.replace(current, _safe(replacement))
    return optimise_image_delivery(output)


@register.simple_tag(takes_context=True)
def exact_page_main(context):
    request = context.get("request")
    page = context.get("page")
    public_path = getattr(page, "url", "") or getattr(
        request,
        "path_info",
        "/",
    )
    layout = ExactPageLayout.objects.filter(
        path=normalise_path(public_path),
        enabled=True,
    ).first()
    if layout is None:
        return ""

    site_settings = SiteSettings.for_request(request)
    return mark_safe(apply_global_facts(layout.html, site_settings))
