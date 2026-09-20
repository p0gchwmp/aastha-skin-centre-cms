"""SEO verification state and safe candidate-profile bootstrap.

Candidate third-party identities may be prefilled to reduce admin work, but this
module never marks facts verified. Search schema/indexation still depends on an
explicit facts_verified_on date entered after human checking.
"""

from __future__ import annotations

from home.local_search import LOCAL_SEARCH_AREAS
from home.models import ClinicLocation, Doctor, StandardPage
from seo_support.models import ClinicSEOProfile, DoctorSEOProfile


CLINIC_PROFILE_CANDIDATES = {
    "karan-nagar": {
        "google_business_url": "https://maps.app.goo.gl/pHCQ1r4crKuZBSi98",
        "justdial_url": (
            "https://www.justdial.com/Jammu/"
            "Aastha-Skin-Dermato-Cosmetic-Centre-Near-Amphalla-Chowk-"
            "Karan-Nagar/9999PX191-X191-110209095958-N1H9_BZDET"
        ),
    },
    "paloura": {
        "google_business_url": "https://maps.app.goo.gl/kh4AqZoUkscpEgWc8",
        "justdial_url": (
            "https://www.justdial.com/Jammu/"
            "AASTHA-SKIN-AND-DERMATO-COSMETIC-CENTRE-Near-Govt-Higher-"
            "Secondary-School-Paloura/9999PX191-X191-250621103839-Q8M5_BZDET"
        ),
    },
}

DOCTOR_PROFILE_CANDIDATES = {
    "dr-cheena-langer": {
        "practo_url": (
            "https://www.practo.com/jammu/doctor/"
            "cheena-langer-dermatologist-1"
        ),
    },
}


def _fill_blank_fields(instance, candidates: dict[str, str]) -> list[str]:
    changed = []
    for field_name, candidate in candidates.items():
        if candidate and not (getattr(instance, field_name, "") or "").strip():
            setattr(instance, field_name, candidate)
            changed.append(field_name)
    if changed:
        instance.save(update_fields=changed)
    return changed


def ensure_candidate_seo_profiles() -> dict[str, list[str]]:
    """Create missing SEO profile rows and fill only blank candidate identity URLs.

    This intentionally leaves facts_verified_on blank. Editors must still check
    branch/doctor facts before schema enrichment or local-page activation.
    """

    created = []
    updated = []

    for clinic in ClinicLocation.objects.filter(is_active=True):
        defaults = CLINIC_PROFILE_CANDIDATES.get(clinic.slug, {})
        profile, was_created = ClinicSEOProfile.objects.get_or_create(
            clinic=clinic,
            defaults=defaults,
        )
        if was_created:
            created.append(f"clinic:{clinic.slug}")
        else:
            changed = _fill_blank_fields(profile, defaults)
            if changed:
                updated.append(f"clinic:{clinic.slug}:{','.join(changed)}")

    for doctor in Doctor.objects.filter(is_active=True):
        defaults = DOCTOR_PROFILE_CANDIDATES.get(doctor.slug, {})
        profile, was_created = DoctorSEOProfile.objects.get_or_create(
            doctor=doctor,
            defaults=defaults,
        )
        if was_created:
            created.append(f"doctor:{doctor.slug}")
        else:
            changed = _fill_blank_fields(profile, defaults)
            if changed:
                updated.append(f"doctor:{doctor.slug}:{','.join(changed)}")

    return {"created": created, "updated": updated}


def _clinic_status(clinic: ClinicLocation) -> dict[str, object]:
    profile = ClinicSEOProfile.objects.filter(clinic=clinic).first()
    missing = []
    if profile is None:
        missing.append("SEO profile")
    else:
        if not profile.google_business_url:
            missing.append("Google Business / Maps URL")
        if not profile.service_areas:
            missing.append("service areas")
        if not profile.verification_reviewer:
            missing.append("verification reviewer")
        if not profile.verification_notes:
            missing.append("verification notes")
        if not profile.facts_verified_on:
            missing.append("verification date")

    return {
        "name": clinic.name,
        "slug": clinic.slug,
        "profile": profile,
        "verified": bool(profile and profile.verification_complete),
        "ready": bool(
            profile
            and profile.verification_complete
            and profile.google_business_url
            and profile.service_areas
        ),
        "missing": missing,
    }


def _doctor_status(doctor: Doctor) -> dict[str, object]:
    profile = DoctorSEOProfile.objects.filter(doctor=doctor).first()
    missing = []
    if profile is None:
        missing.append("SEO profile")
    else:
        if not profile.practo_url:
            missing.append("professional profile URL")
        if not profile.verification_reviewer:
            missing.append("verification reviewer")
        if not profile.verification_notes:
            missing.append("verification notes")
        if not profile.facts_verified_on:
            missing.append("verification date")

    return {
        "name": doctor.name,
        "slug": doctor.slug,
        "profile": profile,
        "verified": bool(profile and profile.verification_complete),
        "ready": bool(profile and profile.verification_complete and profile.practo_url),
        "missing": missing,
    }


def build_seo_verification_state() -> dict[str, object]:
    """Return one dashboard-safe view of entity/local-search verification."""

    clinics = [
        _clinic_status(clinic)
        for clinic in ClinicLocation.objects.filter(is_active=True, live=True).order_by(
            "sort_order", "name"
        )
    ]
    doctors = [
        _doctor_status(doctor)
        for doctor in Doctor.objects.filter(is_active=True, live=True).order_by(
            "sort_order", "name"
        )
    ]

    verified_service_areas = {
        area.casefold()
        for profile in ClinicSEOProfile.objects.all()
        if profile.verification_complete
        for area in profile.service_areas
    }

    areas_parent = StandardPage.objects.none()
    try:
        from home.models import ContentIndexPage

        areas_index = ContentIndexPage.objects.live().public().filter(slug="areas").first()
        if areas_index is not None:
            areas_parent = (
                StandardPage.objects.live().public().child_of(areas_index)
            )
    except Exception:
        areas_parent = StandardPage.objects.none()

    pages_by_slug = {page.slug: page for page in areas_parent}
    areas = []
    for area in LOCAL_SEARCH_AREAS:
        page = pages_by_slug.get(area["slug"])
        fact_verified = area["name"].casefold() in verified_service_areas
        indexable = bool(page and not page.noindex)
        areas.append(
            {
                **area,
                "page": page,
                "path": (
                    page.get_url()
                    if page is not None
                    else f"/areas/{area['slug']}/"
                ),
                "fact_verified": fact_verified,
                "indexable": indexable,
                "ready": bool(fact_verified and indexable),
                "status": (
                    "Indexable"
                    if fact_verified and indexable
                    else "Verified — activation pending"
                    if fact_verified
                    else "Verification pending"
                ),
            }
        )

    return {
        "clinics": clinics,
        "doctors": doctors,
        "areas": areas,
        "counts": {
            "clinic_ready": sum(1 for item in clinics if item["ready"]),
            "clinic_total": len(clinics),
            "doctor_ready": sum(1 for item in doctors if item["ready"]),
            "doctor_total": len(doctors),
            "area_verified": sum(1 for item in areas if item["fact_verified"]),
            "area_indexable": sum(1 for item in areas if item["indexable"]),
            "area_total": len(areas),
        },
        "links": {
            "clinic_profiles": "/admin/snippets/seo_support/clinicseoprofile/",
            "doctor_profiles": "/admin/snippets/seo_support/doctorseoprofile/",
            "pages": "/admin/pages/",
        },
    }
