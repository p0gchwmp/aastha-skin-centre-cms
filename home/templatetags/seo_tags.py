"""Template tags for canonical page-specific structured data."""

from __future__ import annotations

import json

from django import template

from home.models import ClinicLocation, Doctor, SiteSettings
from home.seo import build_structured_data

register = template.Library()


@register.simple_tag(takes_context=True)
def seo_schema(context, page=None) -> str:
    """Return compact JSON-LD for the current public page.

    The imported homepage already includes a curated clinic graph, so the tag
    intentionally returns an empty string there to avoid duplicate entities.
    """

    request = context.get("request")
    if request is None or request.path == "/":
        return ""

    specific_page = getattr(page, "specific", page) if page else None
    site_settings = SiteSettings.for_request(request)
    clinics = context.get("clinic_locations")
    if clinics is None:
        clinics = ClinicLocation.objects.filter(is_active=True, live=True).order_by(
            "sort_order", "name"
        )
    doctors = context.get("active_doctors")
    if doctors is None:
        doctors = Doctor.objects.filter(is_active=True, live=True).order_by(
            "sort_order", "name"
        )

    configured_origin = context.get("public_site_url", "")
    origin = configured_origin or f"{request.scheme}://{request.get_host()}"
    canonical_url = context.get("canonical_url") or f"{origin}{request.path}"
    canonical_override = getattr(specific_page, "canonical_url_override", "")
    if canonical_override:
        canonical_url = canonical_override

    payload = build_structured_data(
        page=specific_page,
        request=request,
        origin=origin,
        canonical_url=canonical_url,
        site_settings=site_settings,
        clinics=clinics,
        doctors=doctors,
    )
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
