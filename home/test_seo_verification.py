from datetime import date

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import TestCase
from wagtail.models import Site

from home.management.commands.initialize_cms import sync_local_search_pages
from home.models import ClinicLocation, Doctor, HomePage
from home.seo_verification import (
    CLINIC_PROFILE_CANDIDATES,
    DOCTOR_PROFILE_CANDIDATES,
    build_seo_verification_state,
    ensure_candidate_seo_profiles,
)
from seo_support.models import ClinicSEOProfile, DoctorSEOProfile


class SEOVerificationBootstrapTests(TestCase):
    def setUp(self):
        self.home = HomePage.objects.first()
        self.assertIsNotNone(self.home)

        ClinicLocation.objects.update(is_active=False)
        Doctor.objects.update(is_active=False)

        self.karan = ClinicLocation.objects.create(
            name="Karan Nagar",
            slug="karan-nagar",
            address="Lane 2, Karan Nagar, Jammu",
            is_active=True,
            sort_order=1,
        )
        self.paloura = ClinicLocation.objects.create(
            name="Paloura Chowk",
            slug="paloura",
            address="Paloura Chowk, Jammu",
            is_active=True,
            sort_order=2,
        )
        self.doctor = Doctor.objects.create(
            name="Dr. Cheena Langer",
            slug="dr-cheena-langer",
            qualifications="MBBS, MD Dermatology",
            role="Consultant Dermatologist",
            is_active=True,
        )

    def test_candidate_profiles_are_created_without_verification(self):
        result = ensure_candidate_seo_profiles()

        self.assertEqual(
            set(result["created"]),
            {"clinic:karan-nagar", "clinic:paloura", "doctor:dr-cheena-langer"},
        )

        karan = ClinicSEOProfile.objects.get(clinic=self.karan)
        paloura = ClinicSEOProfile.objects.get(clinic=self.paloura)
        doctor = DoctorSEOProfile.objects.get(doctor=self.doctor)

        self.assertEqual(
            karan.google_business_url,
            CLINIC_PROFILE_CANDIDATES["karan-nagar"]["google_business_url"],
        )
        self.assertEqual(
            karan.justdial_url,
            CLINIC_PROFILE_CANDIDATES["karan-nagar"]["justdial_url"],
        )
        self.assertEqual(
            paloura.google_business_url,
            CLINIC_PROFILE_CANDIDATES["paloura"]["google_business_url"],
        )
        self.assertEqual(
            doctor.practo_url,
            DOCTOR_PROFILE_CANDIDATES["dr-cheena-langer"]["practo_url"],
        )
        self.assertIsNone(karan.facts_verified_on)
        self.assertIsNone(paloura.facts_verified_on)
        self.assertIsNone(doctor.facts_verified_on)

    def test_existing_editor_identity_url_is_never_overwritten(self):
        profile = ClinicSEOProfile.objects.create(
            clinic=self.karan,
            google_business_url="https://example.com/editor-owned-google-profile",
        )

        ensure_candidate_seo_profiles()

        profile.refresh_from_db()
        self.assertEqual(
            profile.google_business_url,
            "https://example.com/editor-owned-google-profile",
        )
        self.assertTrue(profile.justdial_url)
        self.assertIsNone(profile.facts_verified_on)


class SEOVerificationStateTests(TestCase):
    def setUp(self):
        self.home = HomePage.objects.first()
        self.assertIsNotNone(self.home)

        ClinicLocation.objects.update(is_active=False)
        Doctor.objects.update(is_active=False)

        self.clinic = ClinicLocation.objects.create(
            name="Karan Nagar",
            slug="karan-nagar",
            address="Lane 2, Karan Nagar, Jammu",
            is_active=True,
            sort_order=1,
        )
        self.doctor = Doctor.objects.create(
            name="Dr. Cheena Langer",
            slug="dr-cheena-langer",
            qualifications="MBBS, MD Dermatology",
            role="Consultant Dermatologist",
            is_active=True,
        )
        ensure_candidate_seo_profiles()
        sync_local_search_pages()
        self.home.refresh_from_db()

    def test_area_stays_blocked_until_service_area_is_verified_and_activated(self):
        state = build_seo_verification_state()
        gandhi = next(item for item in state["areas"] if item["slug"] == "gandhi-nagar")
        self.assertFalse(gandhi["fact_verified"])
        self.assertFalse(gandhi["indexable"])
        self.assertFalse(gandhi["ready"])

        profile = ClinicSEOProfile.objects.get(clinic=self.clinic)
        profile.service_area = "Gandhi Nagar"
        profile.verification_reviewer = "SEO reviewer"
        profile.verification_notes = "Checked against current branch service-area records."
        profile.facts_verified_on = date(2026, 9, 19)
        profile.save(
            update_fields=[
                "service_area",
                "verification_reviewer",
                "verification_notes",
                "facts_verified_on",
            ]
        )

        state = build_seo_verification_state()
        gandhi = next(item for item in state["areas"] if item["slug"] == "gandhi-nagar")
        self.assertTrue(gandhi["fact_verified"])
        self.assertFalse(gandhi["indexable"])
        self.assertEqual(gandhi["status"], "Verified — activation pending")

        call_command("activate_verified_local_search", apply=True)

        state = build_seo_verification_state()
        gandhi = next(item for item in state["areas"] if item["slug"] == "gandhi-nagar")
        self.assertTrue(gandhi["ready"])
        self.assertTrue(gandhi["indexable"])
        self.assertEqual(gandhi["status"], "Indexable")

    def test_control_centre_renders_verification_dashboard(self):
        user = get_user_model().objects.create_superuser(
            username="seo-verification-admin",
            email="seo-verification@example.invalid",
            password="test-password",
        )
        self.client.force_login(user)

        response = self.client.get(
            "/admin/aastha-control-centre/",
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        body = response.content.decode()
        self.assertIn("Verification &amp; indexation readiness", body)
        self.assertIn("18 area hubs", body)
        self.assertIn("Not approved yet", body)
        self.assertIn("Gandhi Nagar", body)
        self.assertIn("Clinical content review queue", body)
        self.assertIn("No bulk approval:", body)
        self.assertIn("verification date, reviewer and verification notes", body)
