"""Common public-template data and canonical search-engine metadata."""

import os

from django.conf import settings

from .models import ClinicLocation, Doctor, SiteSettings


def _env_flag(name: str, default: bool = False) -> bool:
    """Read a conservative boolean environment feature flag."""

    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def site_collections(request):
    if request.path.startswith("/admin/"):
        return {}

    clinics = list(
        ClinicLocation.objects.filter(is_active=True, live=True).order_by(
            "sort_order", "name"
        )
    )
    doctors = list(
        Doctor.objects.filter(is_active=True, live=True).order_by(
            "sort_order", "name"
        )
    )
    SiteSettings.for_request(request)
    host = request.get_host().split(":", 1)[0].lower()
    is_render_host = host.endswith(".onrender.com")
    configured_public_host_is_render = bool(
        settings.PUBLIC_SITE_HOST
        and settings.PUBLIC_SITE_HOST.endswith(".onrender.com")
    )
    site_is_public = bool(
        settings.PUBLIC_SITE_HOST
        and host == settings.PUBLIC_SITE_HOST
        and not is_render_host
    )
    configured_origin = (
        settings.PUBLIC_SITE_URL
        if settings.PUBLIC_SITE_URL and not configured_public_host_is_render
        else ""
    )
    origin = configured_origin or f"{request.scheme}://{request.get_host()}"
    canonical_url = f"{origin}{request.path}"

    return {
        "clinic_locations": clinics,
        "active_doctors": doctors,
        "site_is_public": site_is_public,
        "public_site_url": configured_origin,
        "canonical_url": canonical_url,
        # Production-safe rollout switch. It is intentionally environment based
        # so the editorial frontend can be deployed and tested without changing
        # page data or publishing revisions in Wagtail.
        "editorial_v37_enabled": _env_flag("AASTHA_EDITORIAL_V37", False),
    }
