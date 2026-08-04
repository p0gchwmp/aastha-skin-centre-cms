from __future__ import annotations

from io import BytesIO
import shutil
import tempfile
from types import SimpleNamespace

from django.core.files.base import ContentFile
from django.test import SimpleTestCase, TestCase, override_settings
from PIL import Image as PillowImage
from wagtail.images import get_image_model

from home.exact_editor import (
    apply_exact_editor_overrides,
    apply_page_media_slots,
    extract_exact_editor_payload,
)
from home.exact_editor_sync import (
    sync_exact_layout_editor_fields,
    sync_uploaded_homepage_images,
)
from home.models import Doctor, ExactPageLayout, HomePage


class ExactEditorExtractionTests(SimpleTestCase):
    def test_extracts_visible_text_images_and_links_in_page_order(self):
        source = (
            '<main id="main-content">'
            '<h1>Clear <span>skin</span></h1>'
            '<p>Diagnosis-led care.</p>'
            '<img src="/assets/images/professional/hero-care.svg" alt="Care">'
            '<a class="button" href="/book-appointment/">Book now</a>'
            "</main>"
        )

        payload = extract_exact_editor_payload(source)

        self.assertEqual(
            [item["text"] for item in payload["editable_text"]],
            ["Clear", "skin", "Diagnosis-led care.", "Book now"],
        )
        self.assertEqual(len(payload["editable_images"]), 1)
        self.assertEqual(
            payload["editable_images"][0]["original_src"],
            "/assets/images/professional/hero-care.svg",
        )
        self.assertEqual(len(payload["editable_links"]), 1)
        self.assertEqual(
            payload["editable_links"][0]["url"],
            "/book-appointment/",
        )

    def test_changed_values_replace_content_without_flattening_markup(self):
        source = (
            '<main id="main-content">'
            '<h1>Clear <span>skin</span></h1>'
            '<p>Original wording.</p>'
            '<a class="button" href="/old/">Book now</a>'
            "</main>"
        )
        layout = SimpleNamespace(
            editable_text=[
                SimpleNamespace(
                    block_type="text",
                    value={
                        "node_index": 2,
                        "original_text": "Original wording.",
                        "text": "Updated & safer wording.",
                    },
                )
            ],
            editable_images=[],
            editable_links=[
                SimpleNamespace(
                    block_type="link",
                    value={
                        "link_index": 0,
                        "original_url": "/old/",
                        "url": "/book-appointment/",
                    },
                )
            ],
        )

        rendered = apply_exact_editor_overrides(source, layout)

        self.assertIn("<h1>Clear <span>skin</span></h1>", rendered)
        self.assertIn("<p>Updated &amp; safer wording.</p>", rendered)
        self.assertIn('href="/book-appointment/"', rendered)
        self.assertNotIn("Original wording.", rendered)


class ExactEditorDatabaseTests(TestCase):
    def test_runtime_fields_are_real_model_fields(self):
        self.assertEqual(
            HomePage._meta.get_field("doctor_section_image").name,
            "doctor_section_image",
        )
        for field_name in ("editable_text", "editable_images", "editable_links"):
            self.assertEqual(
                ExactPageLayout._meta.get_field(field_name).name,
                field_name,
            )

    def test_sync_populates_empty_editor_fields_and_preserves_later_edits(self):
        layout = ExactPageLayout.objects.create(
            path="/editor-test/",
            html=(
                '<main id="main-content"><h1>Editor test</h1>'
                '<p>Body copy</p><a href="/contact/">Contact</a></main>'
            ),
        )

        updates = sync_exact_layout_editor_fields(layout)
        layout.refresh_from_db()

        self.assertCountEqual(
            updates,
            ["editable_text", "editable_images", "editable_links"],
        )
        self.assertEqual(len(layout.editable_text), 3)
        self.assertEqual(len(layout.editable_links), 1)

        raw = list(layout.editable_text.raw_data)
        raw[0]["value"]["text"] = "My saved edit"
        layout.editable_text = raw
        layout.save(update_fields=["editable_text"])

        self.assertEqual(sync_exact_layout_editor_fields(layout), [])
        layout.refresh_from_db()
        self.assertEqual(layout.editable_text[0].value["text"], "My saved edit")


class HomepagePhotoBindingTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp(prefix="aastha-home-photo-test-")
        self.media_override = override_settings(MEDIA_ROOT=self.media_root)
        self.media_override.enable()
        self.addCleanup(self.media_override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, True)

        self.home = HomePage.objects.get(slug="home")
        self.home.hero_image = None
        self.home.doctor_section_image = None
        self.home.save()

        self.doctor = Doctor.objects.filter(slug="dr-cheena-langer").first()
        if self.doctor is None:
            self.doctor = Doctor.objects.create(
                name="Dr. Cheena Langer",
                slug="dr-cheena-langer",
            )
        self.doctor.photo = None
        self.doctor.save()

    def _image(self, name: str, colour):
        stream = BytesIO()
        PillowImage.new("RGB", (900, 900), colour).save(stream, format="PNG")
        stream.seek(0)
        return get_image_model().objects.create(
            title="dr cheena langer",
            file=ContentFile(stream.read(), name=name),
        )

    def test_two_latest_matching_uploads_fill_distinct_homepage_slots_once(self):
        hero = self._image("dr-cheena-langer-hero.png", (120, 20, 60))
        doctor = self._image("dr-cheena-langer-doctor.png", (220, 170, 150))

        updates = sync_uploaded_homepage_images()
        self.home.refresh_from_db()
        self.doctor.refresh_from_db()

        self.assertEqual(self.home.hero_image_id, hero.id)
        self.assertEqual(self.home.doctor_section_image_id, doctor.id)
        self.assertEqual(self.doctor.photo_id, doctor.id)
        self.assertCountEqual(
            updates,
            [
                "homepage hero image",
                "homepage doctor image",
                "doctor profile image",
            ],
        )

        replacement = self._image("later-upload.png", (10, 30, 80))
        self.assertEqual(sync_uploaded_homepage_images(), [])
        self.home.refresh_from_db()
        self.assertNotEqual(self.home.hero_image_id, replacement.id)
        self.assertEqual(self.home.hero_image_id, hero.id)

    def test_selected_photos_replace_both_homepage_svg_placeholders(self):
        hero = self._image("hero.png", (120, 20, 60))
        doctor = self._image("doctor.png", (220, 170, 150))
        self.home.hero_image = hero
        self.home.doctor_section_image = doctor
        self.home.save()
        source = (
            '<main id="main-content">'
            '<section class="home-hero"><img '
            'src="/assets/images/professional/hero-care.svg" alt=""></section>'
            '<section><img src="/assets/images/professional/doctor-care.svg" '
            'alt=""></section></main>'
        )

        rendered = apply_page_media_slots(source, self.home)

        self.assertNotIn("hero-care.svg", rendered)
        self.assertNotIn("doctor-care.svg", rendered)
        self.assertIn("Dr. Cheena Langer, consultant dermatologist", rendered)
        self.assertIn("srcset=", rendered)
