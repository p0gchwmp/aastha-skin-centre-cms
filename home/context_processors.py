"""Common public-template data and search-engine metadata."""

import json

from django.conf import settings

from .models import ClinicLocation, Doctor, SiteSettings


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
    site_settings = SiteSettings.for_request(request)
    host = request.get_host().split(":", 1)[0].lower()
    site_is_public = bool(
        settings.PUBLIC_SITE_HOST and host == settings.PUBLIC_SITE_HOST
    )
    origin = settings.PUBLIC_SITE_URL or (
        f"{request.scheme}://{request.get_host()}"
    )
    canonical_url = f"{origin}{request.path}"

    clinic_schema = {
        "@type": "MedicalClinic",
        "@id": f"{origin}/#clinic",
        "name": site_settings.clinic_name,
        "url": f"{origin}/",
        "description": site_settings.default_meta_description,
        "medicalSpecialty": "Dermatology",
        "telephone": [
            site_settings.primary_mobile,
            site_settings.secondary_mobile,
        ],
        "email": site_settings.email,
        "address": [
            {
                "@type": "PostalAddress",
                "name": clinic.name,
                "streetAddress": clinic.address,
                "addressLocality": clinic.locality or "Jammu",
                "postalCode": clinic.postal_code,
                "addressRegion": "Jammu and Kashmir",
                "addressCountry": "IN",
            }
            for clinic in clinics
        ],
    }
    if site_settings.logo:
        clinic_schema["logo"] = request.build_absolute_uri(
            site_settings.logo.file.url
        )

    graph = [clinic_schema]
    graph.extend(
        {
            "@type": "Physician",
            "@id": f"{origin}/dr-{doctor.slug}/#physician",
            "name": doctor.name,
            "url": f"{origin}/dr-{doctor.slug}/",
            "jobTitle": doctor.role or "Dermatologist",
            "description": doctor.short_bio,
            "medicalSpecialty": "Dermatology",
            "worksFor": {"@id": f"{origin}/#clinic"},
        }
        for doctor in doctors
    )

    return {
        "clinic_locations": clinics,
        "active_doctors": doctors,
        "site_is_public": site_is_public,
        "public_site_url": settings.PUBLIC_SITE_URL,
        "canonical_url": canonical_url,
        # The homepage already carries its curated schema in CMS content.
        # Add the global graph everywhere else to avoid duplicate entities.
        "structured_data_json": (
            ""
            if request.path == "/"
            else json.dumps(
                {"@context": "https://schema.org", "@graph": graph},
                ensure_ascii=False,
                separators=(",", ":"),
            )
        ),
    }
