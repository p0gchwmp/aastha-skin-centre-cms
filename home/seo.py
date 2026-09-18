"""Structured-data builders for public clinic pages.

The helpers in this module deliberately use only facts stored in Wagtail. Empty
or unverified fields are omitted instead of being guessed.
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Iterable
from urllib.parse import urlsplit

from django.utils.html import strip_tags

from .local_search import AREA_BY_SLUG, PRIORITY_TREATMENT_SLUGS
from .models import (
    BlogPage,
    ClinicLocation,
    ClinicPage,
    ConditionPage,
    Doctor,
    DoctorPage,
    SiteSettings,
    StandardPage,
    TreatmentPage,
)


def _compact(value: Any) -> Any:
    """Recursively remove blank values while preserving false and zero."""

    if isinstance(value, dict):
        output = {}
        for key, item in value.items():
            compacted = _compact(item)
            if compacted not in (None, "", [], {}):
                output[key] = compacted
        return output
    if isinstance(value, (list, tuple)):
        output = [_compact(item) for item in value]
        return [item for item in output if item not in (None, "", [], {})]
    if isinstance(value, (date, datetime)):
        return value.isoformat()
    return value


def _absolute_url(origin: str, value: str | None) -> str:
    if not value:
        return ""
    parsed = urlsplit(str(value))
    path = parsed.path or "/"
    query = f"?{parsed.query}" if parsed.query else ""
    fragment = f"#{parsed.fragment}" if parsed.fragment else ""
    return f"{origin.rstrip('/')}{path}{query}{fragment}"


def _page_url(page, request, origin: str) -> str:
    if page is None:
        return ""
    try:
        value = page.get_url(request=request)
    except (AttributeError, TypeError):
        value = getattr(page, "url", "")
    return _absolute_url(origin, value or "/")


def _image_url(origin: str, image) -> str:
    if not image:
        return ""
    try:
        return _absolute_url(origin, image.file.url)
    except (AttributeError, ValueError):
        return ""


def _description(page, site_settings: SiteSettings) -> str:
    return (
        getattr(page, "search_description", "")
        or getattr(page, "introduction", "")
        or site_settings.default_meta_description
    ).strip()


def _social_urls(site_settings: SiteSettings) -> list[str]:
    return [
        value
        for value in (
            site_settings.facebook_url,
            site_settings.instagram_url,
            site_settings.youtube_url,
        )
        if value
    ]


def _clinic_page(clinic: ClinicLocation):
    return (
        ClinicPage.objects.live()
        .public()
        .filter(clinic=clinic)
        .order_by("path")
        .first()
    )


def _doctor_page(doctor: Doctor):
    return (
        DoctorPage.objects.live()
        .public()
        .filter(doctor=doctor)
        .order_by("path")
        .first()
    )


def _clinic_url(clinic: ClinicLocation, request, origin: str) -> str:
    page = _clinic_page(clinic)
    if page:
        return _page_url(page, request, origin)
    return f"{origin.rstrip('/')}/locations/"


def _clinic_id(clinic: ClinicLocation, request, origin: str) -> str:
    url = _clinic_url(clinic, request, origin)
    suffix = "clinic" if _clinic_page(clinic) else f"clinic-{clinic.slug}"
    return f"{url.rstrip('/')}/#{suffix}"


def _doctor_url(doctor: Doctor, request, origin: str) -> str:
    page = _doctor_page(doctor)
    if page:
        return _page_url(page, request, origin)
    return f"{origin.rstrip('/')}/dr-{doctor.slug}/"


def _doctor_id(doctor: Doctor, request, origin: str) -> str:
    return f"{_doctor_url(doctor, request, origin).rstrip('/')}/#physician"


def _organization_entity(
    site_settings: SiteSettings,
    clinics: Iterable[ClinicLocation],
    origin: str,
    request,
) -> dict[str, Any]:
    clinic_refs = [
        {"@id": _clinic_id(clinic, request, origin)} for clinic in clinics
    ]
    logo = _image_url(origin, site_settings.logo)
    phones = [
        value
        for value in (
            site_settings.primary_mobile,
            site_settings.secondary_mobile,
        )
        if value
    ]
    return _compact(
        {
            "@type": "Organization",
            "@id": f"{origin.rstrip('/')}/#organization",
            "name": site_settings.clinic_name,
            "alternateName": site_settings.short_name,
            "url": f"{origin.rstrip('/')}/",
            "description": site_settings.default_meta_description,
            "email": site_settings.email,
            "telephone": phones,
            "logo": {"@type": "ImageObject", "url": logo} if logo else None,
            "sameAs": _social_urls(site_settings),
            "areaServed": {
                "@type": "AdministrativeArea",
                "name": "Jammu and Kashmir",
            },
            "subOrganization": clinic_refs,
            "contactPoint": {
                "@type": "ContactPoint",
                "contactType": "appointments",
                "telephone": site_settings.primary_mobile,
                "areaServed": "IN",
                "availableLanguage": ["English", "Hindi"],
            },
        }
    )


def _website_entity(site_settings: SiteSettings, origin: str) -> dict[str, Any]:
    return _compact(
        {
            "@type": "WebSite",
            "@id": f"{origin.rstrip('/')}/#website",
            "url": f"{origin.rstrip('/')}/",
            "name": site_settings.clinic_name,
            "alternateName": site_settings.short_name,
            "description": site_settings.default_meta_description,
            "inLanguage": "en-IN",
            "publisher": {"@id": f"{origin.rstrip('/')}/#organization"},
        }
    )


def _clinic_entity(
    clinic: ClinicLocation,
    site_settings: SiteSettings,
    origin: str,
    request,
) -> dict[str, Any]:
    clinic_url = _clinic_url(clinic, request, origin)
    image = _image_url(origin, clinic.hero_image)
    return _compact(
        {
            "@type": "MedicalClinic",
            "@id": _clinic_id(clinic, request, origin),
            "name": f"{site_settings.short_name} – {clinic.name}",
            "url": clinic_url,
            "description": (
                f"Dermatology, skin, hair and laser care at the "
                f"{clinic.name} clinic in Jammu."
            ),
            "medicalSpecialty": "Dermatology",
            "parentOrganization": {
                "@id": f"{origin.rstrip('/')}/#organization"
            },
            "address": {
                "@type": "PostalAddress",
                "streetAddress": clinic.address,
                "addressLocality": clinic.locality or "Jammu",
                "addressRegion": "Jammu and Kashmir",
                "postalCode": clinic.postal_code,
                "addressCountry": "IN",
            },
            "telephone": clinic.mobile or clinic.landline or site_settings.primary_mobile,
            "email": clinic.email or site_settings.email,
            "hasMap": clinic.google_maps_url,
            "image": image,
            "areaServed": {"@type": "City", "name": "Jammu"},
        }
    )


def _physician_entity(
    doctor: Doctor,
    clinics: Iterable[ClinicLocation],
    origin: str,
    request,
) -> dict[str, Any]:
    image = _image_url(origin, doctor.photo)
    return _compact(
        {
            "@type": "Physician",
            "@id": _doctor_id(doctor, request, origin),
            "name": doctor.name,
            "url": _doctor_url(doctor, request, origin),
            "jobTitle": doctor.role or "Consultant Dermatologist",
            "description": doctor.short_bio,
            "medicalSpecialty": "Dermatology",
            "honorificSuffix": doctor.qualifications,
            "identifier": doctor.registration_details,
            "image": image,
            "telephone": doctor.phone,
            "email": doctor.email,
            "worksFor": [
                {"@id": _clinic_id(clinic, request, origin)} for clinic in clinics
            ],
            "affiliation": {
                "@id": f"{origin.rstrip('/')}/#organization"
            },
        }
    )


def _breadcrumb_entity(page, request, origin: str) -> dict[str, Any] | None:
    if page is None or not hasattr(page, "get_ancestors"):
        return None
    ancestors = (
        page.get_ancestors(inclusive=True)
        .filter(depth__gt=1)
        .live()
        .public()
        .specific()
    )
    items = [
        {
            "@type": "ListItem",
            "position": position,
            "name": ancestor.title,
            "item": _page_url(ancestor, request, origin),
        }
        for position, ancestor in enumerate(ancestors, start=1)
    ]
    if len(items) < 2:
        return None
    return {
        "@type": "BreadcrumbList",
        "@id": f"{_page_url(page, request, origin)}#breadcrumb",
        "itemListElement": items,
    }


def _review_fields(page, request, origin: str) -> dict[str, Any]:
    reviewer = getattr(page, "reviewed_by", None)
    return _compact(
        {
            "reviewedBy": (
                {"@id": _doctor_id(reviewer, request, origin)}
                if reviewer
                else None
            ),
            "lastReviewed": getattr(page, "medical_review_date", None),
        }
    )


def _modified_date(page) -> str:
    value = (
        getattr(page, "last_published_at", None)
        or getattr(page, "latest_revision_created_at", None)
    )
    return value.isoformat() if value else ""


def _page_entity(
    page,
    site_settings: SiteSettings,
    origin: str,
    canonical_url: str,
    request,
) -> dict[str, Any] | None:
    if page is None:
        return None

    description = _description(page, site_settings)
    common = {
        "@id": f"{canonical_url}#webpage",
        "url": canonical_url,
        "name": page.seo_title or page.title,
        "description": description,
        "isPartOf": {"@id": f"{origin.rstrip('/')}/#website"},
        "publisher": {"@id": f"{origin.rstrip('/')}/#organization"},
        "inLanguage": "en-IN",
        "dateModified": _modified_date(page),
    }

    if isinstance(page, StandardPage):
        parent = page.get_parent().specific
        area = (
            AREA_BY_SLUG.get(page.slug)
            if getattr(parent, "slug", "") == "areas"
            else None
        )
        if area:
            treatment_rows = list(
                TreatmentPage.objects.live()
                .public()
                .filter(slug__in=PRIORITY_TREATMENT_SLUGS)
            )
            treatment_by_slug = {item.slug: item for item in treatment_rows}
            item_list = []
            for position, slug in enumerate(PRIORITY_TREATMENT_SLUGS, start=1):
                treatment = treatment_by_slug.get(slug)
                if treatment is None:
                    continue
                item_list.append(
                    {
                        "@type": "ListItem",
                        "position": position,
                        "name": treatment.title,
                        "url": _page_url(treatment, request, origin),
                    }
                )
            return _compact(
                {
                    **common,
                    "@type": "CollectionPage",
                    "about": {
                        "@type": "Place",
                        "name": area["name"],
                    },
                    "mainEntity": {
                        "@type": "ItemList",
                        "name": (
                            "Dermatology services in Jammu for patients "
                            f"searching from {area['name']}"
                        ),
                        "itemListElement": item_list,
                    },
                }
            )

    if isinstance(page, BlogPage):
        author = page.author
        image = _image_url(origin, page.social_image or page.hero_image)
        return _compact(
            {
                **common,
                "@type": "BlogPosting",
                "@id": f"{canonical_url}#article",
                "headline": page.seo_title or page.title,
                "mainEntityOfPage": {"@id": f"{canonical_url}#webpage"},
                "datePublished": page.published_date,
                "author": (
                    {"@id": _doctor_id(author, request, origin)}
                    if author
                    else {"@id": f"{origin.rstrip('/')}/#organization"}
                ),
                "image": image,
                **_review_fields(page, request, origin),
            }
        )

    if isinstance(page, DoctorPage) and page.doctor:
        return _compact(
            {
                **common,
                "@type": "ProfilePage",
                "mainEntity": {
                    "@id": _doctor_id(page.doctor, request, origin)
                },
            }
        )

    if isinstance(page, ClinicPage) and page.clinic:
        return _compact(
            {
                **common,
                "@type": "WebPage",
                "mainEntity": {
                    "@id": _clinic_id(page.clinic, request, origin)
                },
            }
        )

    if isinstance(page, (ConditionPage, TreatmentPage)):
        medical_type = (
            "MedicalCondition" if isinstance(page, ConditionPage) else "MedicalProcedure"
        )
        return _compact(
            {
                **common,
                "@type": "MedicalWebPage",
                "about": {
                    "@type": medical_type,
                    "name": page.title,
                    "description": description,
                },
                "specialty": "Dermatology",
                **_review_fields(page, request, origin),
            }
        )

    return _compact({**common, "@type": "WebPage"})


def build_structured_data(
    *,
    page,
    request,
    origin: str,
    canonical_url: str,
    site_settings: SiteSettings,
    clinics: Iterable[ClinicLocation],
    doctors: Iterable[Doctor],
) -> dict[str, Any]:
    """Build a canonical, page-aware Schema.org graph.

    The homepage keeps its existing curated JSON-LD snapshot, so callers should
    not invoke this builder for ``/``.
    """

    clinics = list(clinics)
    doctors = list(doctors)
    graph: list[dict[str, Any]] = [
        _organization_entity(site_settings, clinics, origin, request),
        _website_entity(site_settings, origin),
    ]
    graph.extend(
        _clinic_entity(clinic, site_settings, origin, request)
        for clinic in clinics
    )
    graph.extend(
        _physician_entity(doctor, clinics, origin, request) for doctor in doctors
    )

    breadcrumb = _breadcrumb_entity(page, request, origin)
    if breadcrumb:
        graph.append(breadcrumb)

    page_entity = _page_entity(
        page,
        site_settings,
        origin,
        canonical_url,
        request,
    )
    if page_entity:
        graph.append(page_entity)

    return _compact({"@context": "https://schema.org", "@graph": graph})
