from __future__ import annotations

import base64

from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import TestCase
from wagtail.images import get_image_model
from wagtail.models import Site

from home.approved_media import (
    APPROVED_DOCTOR_PORTRAIT_TITLE,
    sync_approved_doctor_media,
)
from home.models import Doctor, HomePage, SiteSettings


TINY_PNG = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAAIAAAACCAIAAAD91JpzAAAAFElEQVR4nGP8z8DAwMDAxMDA"
    "wMAAAAwBAQDJ/pLvAAAAAElFTkSuQmCC"
)


class ApprovedDoctorMediaTests(TestCase):
    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        self.home = HomePage.objects.first()
        self.assertIsNotNone(self.home)
        self.doctor = Doctor.objects.filter(slug="dr-cheena-langer").first()
        if self.doctor is None:
            self.doctor = Doctor.objects.create(
                name="Dr. Cheena Langer",
                slug="dr-cheena-langer",
                qualifications="MBBS, MD Dermatology",
                role="Consultant Dermatologist",
                is_active=True,
            )
        self.doctor.photo = None
        self.doctor.save(update_fields=["photo"])
        self.home.doctor_section_image = None
        self.home.save(update_fields=["doctor_section_image"])
        self.settings = SiteSettings.for_site(self.site)
        self.settings.default_social_image = None
        self.settings.save(update_fields=["default_social_image"])

    def test_blank_slots_receive_one_real_media_record(self):
        calls = []

        def fetcher(url):
            calls.append(url)
            return TINY_PNG

        result = sync_approved_doctor_media(self.site, fetcher=fetcher)

        self.assertEqual(len(calls), 1)
        self.assertTrue(result["created_image"])
        self.assertCountEqual(
            result["updates"],
            [
                "doctor profile image",
                "homepage doctor image",
                "default social image",
            ],
        )

        self.doctor.refresh_from_db()
        self.home.refresh_from_db()
        self.settings.refresh_from_db()
        self.assertIsNotNone(self.doctor.photo_id)
        self.assertEqual(self.home.doctor_section_image_id, self.doctor.photo_id)
        self.assertEqual(self.settings.default_social_image_id, self.doctor.photo_id)
        image = get_image_model().objects.get(pk=self.doctor.photo_id)
        self.assertEqual(image.title, APPROVED_DOCTOR_PORTRAIT_TITLE)

    def test_existing_editor_media_is_reused_and_never_overwritten(self):
        image = get_image_model().objects.create(
            title="Editor selected real portrait",
            file=SimpleUploadedFile("editor-selected.png", TINY_PNG, "image/png"),
        )
        self.doctor.photo = image
        self.doctor.save(update_fields=["photo"])

        result = sync_approved_doctor_media(
            self.site,
            fetcher=lambda url: self.fail("network fetch should not be needed"),
        )

        self.doctor.refresh_from_db()
        self.home.refresh_from_db()
        self.settings.refresh_from_db()
        self.assertEqual(self.doctor.photo_id, image.id)
        self.assertEqual(self.home.doctor_section_image_id, image.id)
        self.assertEqual(self.settings.default_social_image_id, image.id)
        self.assertFalse(result["created_image"])

    def test_fetch_failure_is_non_destructive_and_keeps_release_blockers_visible(self):
        def failing_fetcher(url):
            raise OSError("source unavailable")

        result = sync_approved_doctor_media(self.site, fetcher=failing_fetcher)

        self.assertIn("source unavailable", result["warning"])
        self.doctor.refresh_from_db()
        self.settings.refresh_from_db()
        self.assertIsNone(self.doctor.photo_id)
        self.assertIsNone(self.settings.default_social_image_id)
