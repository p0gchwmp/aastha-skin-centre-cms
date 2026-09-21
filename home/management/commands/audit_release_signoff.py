"""Report the human approvals still required before production cutover."""

from __future__ import annotations

import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from wagtail.models import Site

from home.local_search import LOCAL_SEARCH_AREAS, PRIORITY_TREATMENT_SLUGS
from home.seo_verification import entity_evidence_snapshot
from home.models import (
    BlogPage,
    ClinicLocation,
    ConditionPage,
    Doctor,
    SiteSettings,
    TreatmentPage,
)
from seo_support.models import ClinicSEOProfile, DoctorSEOProfile


MEDICAL_PAGE_TYPES = (ConditionPage, TreatmentPage, BlogPage)


def _clean(value) -> str:
    return str(value or "").strip()


def build_release_signoff_report(site=None) -> dict[str, object]:
    site = site or Site.objects.filter(is_default_site=True).first()
    if site is None:
        raise CommandError("No default Wagtail site exists.")

    pages = list(
        site.root_page.get_descendants(inclusive=True)
        .live()
        .public()
        .specific()
        .order_by("path")
    )
    medical_pages = [page for page in pages if isinstance(page, MEDICAL_PAGE_TYPES)]

    priority_treatment_slugs = set(PRIORITY_TREATMENT_SLUGS)
    medical_pending = []
    for page in medical_pages:
        reasons = []
        if getattr(page, "review_status", "") != "approved":
            reasons.append(
                f"review status is {getattr(page, 'review_status', '') or 'blank'}"
            )
        if not getattr(page, "reviewed_by_id", None):
            reasons.append("reviewer is not recorded")
        if not getattr(page, "medical_review_date", None):
            reasons.append("medical review date is not recorded")
        if reasons:
            medical_pending.append(
                {
                    "page_id": page.pk,
                    "path": page.get_url() or page.url_path,
                    "title": page.title,
                    "page_type": page.__class__.__name__,
                    "review_status": getattr(page, "review_status", ""),
                    "reviewer": (
                        str(page.reviewed_by)
                        if getattr(page, "reviewed_by_id", None)
                        else ""
                    ),
                    "medical_review_date": getattr(
                        page, "medical_review_date", None
                    ),
                    "reasons": reasons,
                    "priority_key": (
                        "p1"
                        if isinstance(page, TreatmentPage)
                        and page.slug in priority_treatment_slugs
                        else "p2"
                        if isinstance(page, (TreatmentPage, ConditionPage))
                        else "p3"
                    ),
                    "priority_label": (
                        "P1 · core treatment"
                        if isinstance(page, TreatmentPage)
                        and page.slug in priority_treatment_slugs
                        else "P2 · clinical page"
                        if isinstance(page, (TreatmentPage, ConditionPage))
                        else "P3 · journal"
                    ),
                    "priority_rank": (
                        1
                        if isinstance(page, TreatmentPage)
                        and page.slug in priority_treatment_slugs
                        else 2
                        if isinstance(page, (TreatmentPage, ConditionPage))
                        else 3
                    ),
                }
            )

    medical_pending.sort(
        key=lambda item: (
            item["priority_rank"],
            item["page_type"],
            item["title"].casefold(),
        )
    )
    medical_review_groups = [
        {
            "key": key,
            "label": label,
            "description": description,
            "items": [item for item in medical_pending if item["priority_key"] == key],
        }
        for key, label, description in (
            (
                "p1",
                "Priority 1 — core treatment pages",
                "Highest-impact treatment pages used in local search, navigation and patient conversion.",
            ),
            (
                "p2",
                "Priority 2 — remaining clinical pages",
                "Other live treatment and condition pages requiring medical sign-off.",
            ),
            (
                "p3",
                "Priority 3 — journal & educational articles",
                "Blog and educational content reviewed after patient-critical clinical pages.",
            ),
        )
    ]

    clinic_rows = []
    clinic_pending = []
    active_clinics = list(
        ClinicLocation.objects.filter(is_active=True, live=True).order_by(
            "sort_order", "name"
        )
    )
    for clinic in active_clinics:
        missing_fields = [
            field
            for field in (
                "address",
                "postal_code",
                "google_maps_url",
                "reception_hours",
                "doctor_hours",
                "procedure_hours",
            )
            if not _clean(getattr(clinic, field, ""))
        ]
        if not (_clean(clinic.mobile) or _clean(clinic.landline)):
            missing_fields.append("phone")

        try:
            seo_profile = clinic.seo_profile
        except ClinicSEOProfile.DoesNotExist:
            seo_profile = None

        verification_reasons = []
        if seo_profile is None:
            verification_reasons.append("local SEO profile is missing")
        else:
            if not seo_profile.facts_verified_on:
                verification_reasons.append("local SEO facts have no verification date")
            if not _clean(seo_profile.verification_reviewer):
                verification_reasons.append("local SEO verification reviewer is missing")
            if not _clean(seo_profile.verification_notes):
                verification_reasons.append("local SEO verification notes are missing")

        row = {
            "name": clinic.name,
            "slug": clinic.slug,
            "address": clinic.address,
            "postal_code": clinic.postal_code,
            "mobile": clinic.mobile,
            "landline": clinic.landline,
            "google_maps_url": clinic.google_maps_url,
            "reception_hours": clinic.reception_hours,
            "doctor_hours": clinic.doctor_hours,
            "procedure_hours": clinic.procedure_hours,
            "verification": (
                {
                    "date": seo_profile.facts_verified_on,
                    "reviewer": seo_profile.verification_reviewer,
                    "source_url": seo_profile.verification_source_url,
                    "notes": seo_profile.verification_notes,
                    "complete": seo_profile.verification_complete,
                }
                if seo_profile is not None
                else None
            ),
            "missing_fields": missing_fields,
            "verification_reasons": verification_reasons,
            "public_evidence": entity_evidence_snapshot("clinic", clinic.slug),
        }
        clinic_rows.append(row)
        if missing_fields or verification_reasons:
            clinic_pending.append(row)

    doctor_rows = []
    doctor_pending = []
    active_doctors = list(
        Doctor.objects.filter(is_active=True, live=True).order_by(
            "sort_order", "name"
        )
    )
    for doctor in active_doctors:
        missing_fields = [
            field
            for field in ("qualifications", "role", "registration_details")
            if not _clean(getattr(doctor, field, ""))
        ]
        if not doctor.photo_id:
            missing_fields.append("photo")

        try:
            seo_profile = doctor.seo_profile
        except DoctorSEOProfile.DoesNotExist:
            seo_profile = None

        verification_reasons = []
        if seo_profile is None:
            verification_reasons.append("professional SEO profile is missing")
        else:
            if not seo_profile.facts_verified_on:
                verification_reasons.append(
                    "professional profile facts have no verification date"
                )
            if not _clean(seo_profile.verification_reviewer):
                verification_reasons.append(
                    "professional profile verification reviewer is missing"
                )
            if not _clean(seo_profile.verification_notes):
                verification_reasons.append(
                    "professional profile verification notes are missing"
                )

        row = {
            "name": doctor.name,
            "slug": doctor.slug,
            "qualifications": doctor.qualifications,
            "role": doctor.role,
            "registration_details": doctor.registration_details,
            "photo_present": bool(doctor.photo_id),
            "verification": (
                {
                    "date": seo_profile.facts_verified_on,
                    "reviewer": seo_profile.verification_reviewer,
                    "source_url": seo_profile.verification_source_url,
                    "notes": seo_profile.verification_notes,
                    "complete": seo_profile.verification_complete,
                }
                if seo_profile is not None
                else None
            ),
            "missing_fields": missing_fields,
            "verification_reasons": verification_reasons,
            "public_evidence": entity_evidence_snapshot("doctor", doctor.slug),
        }
        doctor_rows.append(row)
        if missing_fields or verification_reasons:
            doctor_pending.append(row)

    verified_service_areas = {
        area.casefold()
        for profile in ClinicSEOProfile.objects.all()
        if profile.verification_complete
        for area in profile.service_areas
    }
    local_search_ready = [
        area
        for area in LOCAL_SEARCH_AREAS
        if area["name"].casefold() in verified_service_areas
    ]
    local_search_pending = [
        area
        for area in LOCAL_SEARCH_AREAS
        if area["name"].casefold() not in verified_service_areas
    ]

    settings = SiteSettings.for_site(site)
    site_pending = []
    if not settings.default_social_image_id:
        site_pending.append("approved default social image is missing")

    report = {
        "site": site.hostname,
        "summary": {
            "medical_pages_total": len(medical_pages),
            "medical_pages_pending": len(medical_pending),
            "medical_pages_approved": len(medical_pages) - len(medical_pending),
            "medical_priority_1_pending": sum(
                1 for item in medical_pending if item["priority_key"] == "p1"
            ),
            "medical_priority_2_pending": sum(
                1 for item in medical_pending if item["priority_key"] == "p2"
            ),
            "medical_priority_3_pending": sum(
                1 for item in medical_pending if item["priority_key"] == "p3"
            ),
            "clinics_total": len(clinic_rows),
            "clinics_pending": len(clinic_pending),
            "doctors_total": len(doctor_rows),
            "doctors_pending": len(doctor_pending),
            "site_items_pending": len(site_pending),
            "local_search_areas_total": len(LOCAL_SEARCH_AREAS),
            "local_search_areas_ready": len(local_search_ready),
            "local_search_areas_pending": len(local_search_pending),
            "public_evidence_conflicts": sum(
                1
                for row in (*clinic_rows, *doctor_rows)
                if (row.get("public_evidence") or {}).get("state") == "conflict"
                and not (row.get("verification") or {}).get("complete")
            ),
        },
        "medical_review_pending": medical_pending,
        "medical_review_groups": medical_review_groups,
        "clinics": clinic_rows,
        "clinic_signoff_pending": clinic_pending,
        "doctors": doctor_rows,
        "doctor_signoff_pending": doctor_pending,
        "site_signoff_pending": site_pending,
        "local_search_ready": local_search_ready,
        "local_search_pending": local_search_pending,
        "manual_confirmation": {
            "consultation_fee": str(settings.consultation_fee),
            "currency_symbol": settings.currency_symbol,
            "follow_up_days": settings.follow_up_days,
            "follow_up_included": settings.follow_up_included,
            "primary_mobile": settings.primary_mobile,
            "secondary_mobile": settings.secondary_mobile,
            "whatsapp_mobile": settings.whatsapp_mobile,
            "email": settings.email,
            "note": (
                "Populated values are shown for human confirmation only. "
                "This audit does not treat a filled field as an approval."
            ),
        },
    }
    return report


class Command(BaseCommand):
    help = (
        "Report medical, clinic, doctor and media approvals still required "
        "before production cutover."
    )

    def add_arguments(self, parser):
        parser.add_argument("--json", type=Path, dest="json_path")
        parser.add_argument(
            "--fail-on-pending",
            action="store_true",
            help="Return non-zero while any signoff item is still pending.",
        )

    def handle(self, *args, **options):
        report = build_release_signoff_report()
        summary = report["summary"]

        self.stdout.write(
            "Release signoff audit: "
            f"{summary['medical_pages_pending']}/{summary['medical_pages_total']} "
            "medical pages pending; "
            f"{summary['clinics_pending']}/{summary['clinics_total']} clinics pending; "
            f"{summary['doctors_pending']}/{summary['doctors_total']} doctors pending; "
            f"{summary['site_items_pending']} site/media item(s) pending; "
            f"{summary['local_search_areas_ready']}/"
            f"{summary['local_search_areas_total']} local-search areas verified; "
            f"{summary['public_evidence_conflicts']} unresolved public-source conflict(s)."
        )

        for item in report["doctor_signoff_pending"]:
            reasons = item["missing_fields"] + item["verification_reasons"]
            self.stdout.write(
                self.style.WARNING(
                    f"DOCTOR — {item['name']}: " + "; ".join(reasons)
                )
            )
        for item in report["clinic_signoff_pending"]:
            reasons = item["missing_fields"] + item["verification_reasons"]
            self.stdout.write(
                self.style.WARNING(
                    f"CLINIC — {item['name']}: " + "; ".join(reasons)
                )
            )
        for item in report["site_signoff_pending"]:
            self.stdout.write(self.style.WARNING(f"SITE — {item}"))
        for area in report["local_search_pending"]:
            self.stdout.write(
                self.style.WARNING(
                    f"LOCAL SEO — {area['name']}: service-area verification pending"
                )
            )

        if options.get("json_path"):
            path = options["json_path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(report, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )

        pending = (
            summary["medical_pages_pending"]
            + summary["clinics_pending"]
            + summary["doctors_pending"]
            + summary["site_items_pending"]
            + summary["local_search_areas_pending"]
        )
        if options.get("fail_on_pending") and pending:
            raise CommandError(
                f"Release signoff audit found {pending} pending approval group(s)."
            )
