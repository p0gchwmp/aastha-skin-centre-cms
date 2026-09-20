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


# Public-source review snapshots are deliberately descriptive, not approvals.
# They make source conflicts visible to editors while keeping verification human-owned.
# Re-check the linked sources before entering verification evidence.
PUBLIC_EVIDENCE_OBSERVED_ON = "2026-09-21"
ENTITY_EVIDENCE_SNAPSHOTS = {
    ("clinic", "karan-nagar"): {
        "state": "conflict",
        "label": "Public hours conflict",
        "observed_on": PUBLIC_EVIDENCE_OBSERVED_ON,
        "summary": (
            "The clinic-owned Karan Nagar page lists Monday-Saturday reception "
            "10:00 AM-8:00 PM and doctor consultation 11:00 AM-4:00 PM, while "
            "the current external business listing exposes a different, shorter "
            "hours window. Confirm the live branch schedule before verification."
        ),
        "sources": [
            {
                "label": "Aastha Karan Nagar page",
                "url": "https://www.aasthaskincentre.in/locations/karan-nagar/",
                "kind": "First-party",
            },
            {
                "label": "Google Business candidate",
                "url": CLINIC_PROFILE_CANDIDATES["karan-nagar"]["google_business_url"],
                "kind": "Third-party",
            },
            {
                "label": "Justdial candidate",
                "url": CLINIC_PROFILE_CANDIDATES["karan-nagar"]["justdial_url"],
                "kind": "Third-party",
            },
        ],
        "checks": [
            {
                "label": "Identity / address",
                "state": "aligned",
                "note": "Karan Nagar / Amphalla identity and Jammu PIN are consistent enough to review.",
            },
            {
                "label": "Primary phone",
                "state": "aligned",
                "note": "70066 13362 appears on the clinic-owned page and the business listing.",
            },
            {
                "label": "Opening / doctor hours",
                "state": "conflict",
                "note": "External listing hours differ from the clinic-owned schedule.",
            },
        ],
    },
    ("clinic", "paloura"): {
        "state": "conflict",
        "label": "Public hours conflict",
        "observed_on": PUBLIC_EVIDENCE_OBSERVED_ON,
        "summary": (
            "The clinic-owned Paloura page lists Monday-Saturday reception "
            "10:00 AM-8:00 PM and doctor consultation 6:00 PM-8:00 PM, while "
            "the current external business listing exposes a different morning "
            "hours window. Confirm the live branch schedule before verification."
        ),
        "sources": [
            {
                "label": "Aastha Paloura page",
                "url": "https://www.aasthaskincentre.in/locations/paloura/",
                "kind": "First-party",
            },
            {
                "label": "Google Business candidate",
                "url": CLINIC_PROFILE_CANDIDATES["paloura"]["google_business_url"],
                "kind": "Third-party",
            },
            {
                "label": "Justdial candidate",
                "url": CLINIC_PROFILE_CANDIDATES["paloura"]["justdial_url"],
                "kind": "Third-party",
            },
        ],
        "checks": [
            {
                "label": "Identity / address",
                "state": "aligned",
                "note": "Paloura / Patoli identity, opposite the government school, is consistent enough to review.",
            },
            {
                "label": "Primary phone",
                "state": "aligned",
                "note": "70066 13362 appears on the clinic-owned page and the business listing.",
            },
            {
                "label": "Opening / doctor hours",
                "state": "conflict",
                "note": "External listing hours differ materially from the clinic-owned schedule.",
            },
        ],
    },
    ("doctor", "dr-cheena-langer"): {
        "state": "candidate-aligned",
        "label": "Core identity aligned",
        "observed_on": PUBLIC_EVIDENCE_OBSERVED_ON,
        "summary": (
            "The clinic-owned profile and Practo both support the core identity: "
            "Dr. Cheena Langer, dermatologist, MBBS with MD Dermatology, and about "
            "20 years in medicine. Practo also lists J&K Medical Council registration "
            "9538 from 2007. Human approval is still required."
        ),
        "sources": [
            {
                "label": "Aastha doctor profile",
                "url": "https://www.aasthaskincentre.in/dr-cheena-langer/",
                "kind": "First-party",
            },
            {
                "label": "Practo candidate",
                "url": DOCTOR_PROFILE_CANDIDATES["dr-cheena-langer"]["practo_url"],
                "kind": "Third-party",
            },
        ],
        "checks": [
            {
                "label": "Name / specialty",
                "state": "aligned",
                "note": "Both sources identify Dr. Cheena Langer as a dermatologist in Jammu.",
            },
            {
                "label": "Qualifications",
                "state": "aligned",
                "note": "MBBS and MD Dermatology are supported across the clinic profile and Practo.",
            },
            {
                "label": "Registration candidate",
                "state": "aligned",
                "note": "Practo lists registration 9538 with the J&K Medical Council in 2007.",
            },
        ],
    },
}


def entity_evidence_snapshot(kind: str, slug: str) -> dict[str, object] | None:
    """Return a review-only public-source snapshot without implying verification."""

    snapshot = ENTITY_EVIDENCE_SNAPSHOTS.get((kind, slug))
    if snapshot is None:
        return None
    return {
        **snapshot,
        "sources": [dict(item) for item in snapshot["sources"]],
        "checks": [dict(item) for item in snapshot["checks"]],
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
        "evidence": entity_evidence_snapshot("clinic", clinic.slug),
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
        "evidence": entity_evidence_snapshot("doctor", doctor.slug),
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
                "review_bucket": (
                    "Jammu locality candidate"
                    if area["kind"] == "jammu"
                    else "Regional travel-origin candidate"
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
            "area_jammu_total": sum(1 for item in areas if item["kind"] == "jammu"),
            "area_regional_total": sum(
                1 for item in areas if item["kind"] == "regional"
            ),
            "evidence_conflicts": sum(
                1
                for item in (*clinics, *doctors)
                if item.get("evidence", {}).get("state") == "conflict"
                and not item["verified"]
            ),
        },
        "links": {
            "clinic_profiles": "/admin/snippets/seo_support/clinicseoprofile/",
            "doctor_profiles": "/admin/snippets/seo_support/doctorseoprofile/",
            "pages": "/admin/pages/",
        },
    }
