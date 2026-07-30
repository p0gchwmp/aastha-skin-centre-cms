"""Enrich the core schema graph with verified optional SEO profiles."""

from __future__ import annotations

from typing import Any, Iterable

from home.models import ClinicLocation, Doctor
from home.seo import _clinic_id, _doctor_id


def _optional_profile(instance):
    try:
        return instance.seo_profile
    except instance._meta.apps.get_model(
        "seo_support",
        "ClinicSEOProfile" if isinstance(instance, ClinicLocation) else "DoctorSEOProfile",
    ).DoesNotExist:
        return None


def _entity_by_id(graph: list[dict[str, Any]], entity_id: str):
    return next((entity for entity in graph if entity.get("@id") == entity_id), None)


def enrich_structured_data(
    payload: dict[str, Any],
    *,
    clinics: Iterable[ClinicLocation],
    doctors: Iterable[Doctor],
    request,
    origin: str,
) -> dict[str, Any]:
    """Add geo, hours and verified third-party identities to schema nodes."""

    graph = payload.get("@graph")
    if not isinstance(graph, list):
        return payload

    for clinic in clinics:
        profile = _optional_profile(clinic)
        if profile is None:
            continue
        entity = _entity_by_id(graph, _clinic_id(clinic, request, origin))
        if entity is None:
            continue

        if profile.latitude is not None and profile.longitude is not None:
            entity["geo"] = {
                "@type": "GeoCoordinates",
                "latitude": float(profile.latitude),
                "longitude": float(profile.longitude),
            }
        opening_hours = profile.opening_hours_specifications()
        if opening_hours:
            entity["openingHoursSpecification"] = opening_hours
        if profile.same_as_urls:
            entity["sameAs"] = profile.same_as_urls
        if profile.google_business_url:
            entity["hasMap"] = profile.google_business_url
        if profile.service_areas:
            entity["areaServed"] = [
                {"@type": "Place", "name": area}
                for area in profile.service_areas
            ]

    for doctor in doctors:
        profile = _optional_profile(doctor)
        if profile is None:
            continue
        entity = _entity_by_id(graph, _doctor_id(doctor, request, origin))
        if entity is not None and profile.same_as_urls:
            entity["sameAs"] = profile.same_as_urls

    return payload
