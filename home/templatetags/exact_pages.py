"""Render the verified static layout while retaining CMS-managed facts."""

from __future__ import annotations

from html import escape
from urllib.parse import urlsplit

from django import template
from django.utils.safestring import mark_safe

from home.models import ExactPageLayout, SiteSettings


register = template.Library()


def normalise_path(value: str) -> str:
    path = urlsplit(value or "/").path or "/"
    if not path.startswith("/"):
        path = "/" + path
    if path != "/" and not path.endswith("/"):
        path += "/"
    return path


def _safe(value) -> str:
    return escape(str(value), quote=True)


def apply_global_facts(source: str, site_settings: SiteSettings) -> str:
    """Replace facts that administrators manage centrally.

    The snapshot remains byte-for-byte faithful for layout and content
    structure. Only verified clinic facts are substituted.
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
        ("20+ years", "25+ years"),
        (
            "More than 20 years in medicine",
            "Over 25 years of clinical excellence",
        ),
        (
            "more than 20 years in medicine",
            "over 25 years of clinical excellence",
        ),
    ]
    output = source
    for current, replacement in replacements:
        output = output.replace(current, _safe(replacement))
    return output


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
