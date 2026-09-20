from __future__ import annotations

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase
from wagtail.models import Site

from home.local_search import LOCAL_SEARCH_AREAS
from home.management.commands.audit_release_signoff import (
    build_release_signoff_report,
)
from home.models import (
    ClinicLocation,
    ContentIndexPage,
    Doctor,
    HomePage,
    TreatmentPage,
)


class ReleaseSignoffAuditTests(TestCase):
    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.home = HomePage.objects.first()
        self.assertIsNotNone(self.home)

        self.doctor = Doctor(
            name="Dr Test",
            slug="dr-test-signoff",
            qualifications="MBBS, MD Dermatology",
            role="Consultant Dermatologist",
            registration_details="",
            is_active=True,
        )
        self.doctor.save()
        self.doctor.save_revision().publish()

        self.clinic = ClinicLocation(
            name="Test Clinic",
            slug="test-clinic-signoff",
            address="1 Test Road, Jammu",
            locality="Jammu",
            postal_code="180001",
            mobile="7000000000",
            google_maps_url="https://maps.example.com/test",
            reception_hours="Mon-Sat 10:00-18:00",
            doctor_hours="Mon-Sat 11:00-16:00",
            procedure_hours="Mon-Sat 11:00-18:00",
            is_active=True,
        )
        self.clinic.save()
        self.clinic.save_revision().publish()

        self.index = ContentIndexPage(
            title="Signoff treatments",
            slug="signoff-treatments",
            index_kind="treatments",
            search_description="Signoff treatment test index description for release QA.",
        )
        self.home.add_child(instance=self.index)
        self.index.save_revision().publish()

        self.treatment = TreatmentPage(
            title="Signoff treatment",
            slug="signoff-treatment",
            review_status="medical",
            search_description=(
                "A test medical treatment page used to verify release signoff reporting."
            ),
        )
        self.index.add_child(instance=self.treatment)
        self.treatment.save_revision().publish()

    def test_report_keeps_unverified_human_items_pending(self):
        report = build_release_signoff_report(self.site)

        doctor = next(
            item
            for item in report["doctor_signoff_pending"]
            if item["slug"] == self.doctor.slug
        )
        self.assertIn("registration_details", doctor["missing_fields"])
        self.assertIn("photo", doctor["missing_fields"])
        self.assertIn(
            "professional SEO profile is missing",
            doctor["verification_reasons"],
        )

        clinic = next(
            item
            for item in report["clinic_signoff_pending"]
            if item["slug"] == self.clinic.slug
        )
        self.assertEqual(clinic["missing_fields"], [])
        self.assertIn("local SEO profile is missing", clinic["verification_reasons"])

        medical_items = {
            item["path"]: item for item in report["medical_review_pending"]
        }
        self.assertIn(self.treatment.get_url(), medical_items)
        treatment_item = medical_items[self.treatment.get_url()]
        self.assertEqual(treatment_item["page_id"], self.treatment.pk)
        self.assertEqual(treatment_item["review_status"], "medical")
        self.assertEqual(treatment_item["reviewer"], "")
        self.assertIsNone(treatment_item["medical_review_date"])
        self.assertIn(
            "approved default social image is missing",
            report["site_signoff_pending"],
        )
        self.assertEqual(
            report["summary"]["local_search_areas_pending"],
            len(LOCAL_SEARCH_AREAS),
        )
        self.assertEqual(report["summary"]["local_search_areas_ready"], 0)

    def test_fail_on_pending_is_opt_in(self):
        call_command("audit_release_signoff")
        with self.assertRaises(CommandError):
            call_command("audit_release_signoff", fail_on_pending=True)
