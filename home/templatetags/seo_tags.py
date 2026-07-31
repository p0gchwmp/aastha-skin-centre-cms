"""Template tags for canonical page-specific structured data."""

from __future__ import annotations

import json

from django import template

from home.models import ClinicLocation, Doctor, SiteSettings
from home.seo import build_structured_data
from seo_support.schema import enrich_structured_data

register = template.Library()


@register.simple_tag(takes_context=True)
def seo_schema(context, page=None) -> str:
    """Return compact JSON-LD for every public page, including the homepage."""

    request = context.get("request")
    if request is None:
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
    clinics = list(clinics)
    doctors = list(doctors)

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
    payload = enrich_structured_data(
        payload,
        clinics=clinics,
        doctors=doctors,
        request=request,
        origin=origin,
    )
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
