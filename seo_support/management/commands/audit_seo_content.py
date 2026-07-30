"""Report CMS-side SEO and medical-review gaps before publication campaigns."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from wagtail.models import Page, Site

from home.models import BlogPage, ClinicLocation, ConditionPage, Doctor, SiteSettings, TreatmentPage
from seo_support.models import ClinicSEOProfile, DoctorSEOProfile


class Command(BaseCommand):
    help = "Audit live Wagtail pages and verified local SEO profiles."

    def add_arguments(self, parser):
        parser.add_argument("--json", type=Path, dest="json_path")
        parser.add_argument(
            "--fail-on-errors",
            action="store_true",
            help="Return a non-zero exit code when blocking SEO errors exist.",
        )

    def handle(self, *args, **options):
        pages = list(Page.objects.live().public().specific().order_by("path"))
        default_site = Site.objects.filter(is_default_site=True).first()
        site_settings = SiteSettings.for_site(default_site) if default_site else None
        default_social_image = bool(
            site_settings and site_settings.default_social_image_id
        )
        today = timezone.localdate()

        page_rows = []
        errors: list[str] = []
        warnings: list[str] = []
        titles = Counter()
        descriptions = Counter()

        for page in pages:
            effective_title = (page.seo_title or page.title or "").strip()
            description = (page.search_description or "").strip()
            path = page.url_path or f"page:{page.pk}"
            titles[effective_title] += 1
            if description:
                descriptions[description] += 1

            page_errors: list[str] = []
            page_warnings: list[str] = []
            if not description:
                page_errors.append("missing meta description")
            if len(effective_title) > 65:
                page_warnings.append(f"long SEO title ({len(effective_title)} characters)")
            if description and len(description) > 165:
                page_warnings.append(
                    f"long meta description ({len(description)} characters)"
                )
            if description and len(description) < 70:
                page_warnings.append(
                    f"short meta description ({len(description)} characters)"
                )

            noindex = bool(getattr(page, "noindex", False))
            canonical_override = (
                getattr(page, "canonical_url_override", "") or ""
            ).strip()
            if noindex and canonical_override:
                page_warnings.append("both noindex and canonical override are set")

            if isinstance(page, (ConditionPage, TreatmentPage, BlogPage)):
                status = getattr(page, "review_status", "")
                reviewer = getattr(page, "reviewed_by", None)
                reviewed_on = getattr(page, "medical_review_date", None)
                next_review = getattr(page, "next_review_date", None)
                if status != "approved":
                    page_warnings.append(f"medical review status is {status or 'blank'}")
                if status == "approved" and not reviewer:
                    page_errors.append("approved medical page has no reviewer")
                if status == "approved" and not reviewed_on:
                    page_errors.append("approved medical page has no review date")
                if next_review and next_review < today:
                    page_warnings.append(
                        f"medical review overdue since {next_review.isoformat()}"
                    )

            social_image = bool(getattr(page, "social_image_id", None))
            if not social_image and not default_social_image:
                page_warnings.append("no page or default social image")

            page_rows.append(
                {
                    "id": page.pk,
                    "path": path,
                    "title": effective_title,
                    "description": description,
                    "errors": page_errors,
                    "warnings": page_warnings,
                }
            )
            errors.extend(f"{path}: {item}" for item in page_errors)
            warnings.extend(f"{path}: {item}" for item in page_warnings)

        for title, count in titles.items():
            if title and count > 1:
                warnings.append(f"duplicate effective title ({count} pages): {title!r}")
        for description, count in descriptions.items():
            if count > 1:
                warnings.append(
                    f"duplicate meta description ({count} pages): {description!r}"
                )

        active_clinics = list(
            ClinicLocation.objects.filter(is_active=True, live=True).order_by(
                "sort_order", "name"
            )
        )
        profiled_clinic_ids = set(
            ClinicSEOProfile.objects.filter(clinic__in=active_clinics).values_list(
                "clinic_id", flat=True
            )
        )
        for clinic in active_clinics:
            if clinic.pk not in profiled_clinic_ids:
                warnings.append(f"clinic {clinic}: missing local SEO profile")

        active_doctors = list(
            Doctor.objects.filter(is_active=True, live=True).order_by(
                "sort_order", "name"
            )
        )
        profiled_doctor_ids = set(
            DoctorSEOProfile.objects.filter(doctor__in=active_doctors).values_list(
                "doctor_id", flat=True
            )
        )
        for doctor in active_doctors:
            if doctor.pk not in profiled_doctor_ids:
                warnings.append(f"doctor {doctor}: missing SEO profile")

        payload = {
            "generated_on": today.isoformat(),
            "pages_audited": len(page_rows),
            "pages": page_rows,
            "errors": errors,
            "warnings": warnings,
        }
        if options.get("json_path"):
            path = options["json_path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(payload, indent=2, ensure_ascii=False),
                encoding="utf-8",
            )

        self.stdout.write(
            f"SEO content audit: {len(page_rows)} pages, "
            f"{len(errors)} errors, {len(warnings)} warnings."
        )
        for item in errors:
            self.stdout.write(self.style.ERROR(f"ERROR — {item}"))
        for item in warnings:
            self.stdout.write(self.style.WARNING(f"WARN — {item}"))

        if options.get("fail_on_errors") and errors:
            raise CommandError(f"SEO content audit found {len(errors)} blocking errors.")
