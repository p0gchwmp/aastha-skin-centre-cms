from pathlib import Path

from django.test import SimpleTestCase

from home.clinical_results import (
    CLINICAL_RESULT_GALLERIES,
    drive_thumbnail_url,
    gallery_markup,
)


class ClinicalResultGalleryTests(SimpleTestCase):
    def test_verified_route_manifest(self):
        self.assertEqual(len(CLINICAL_RESULT_GALLERIES), 16)
        self.assertEqual(
            sum(len(item["images"]) for item in CLINICAL_RESULT_GALLERIES.values()),
            44,
        )
        self.assertNotIn("/treatments/earlobe-repair/", CLINICAL_RESULT_GALLERIES)
        self.assertNotIn(
            "/treatments/laser-skin-rejuvenation/",
            CLINICAL_RESULT_GALLERIES,
        )

    def test_drive_ids_are_explicit_and_unique(self):
        ids = [
            image["id"]
            for gallery in CLINICAL_RESULT_GALLERIES.values()
            for image in gallery["images"]
        ]
        self.assertEqual(len(ids), 44)
        self.assertEqual(len(set(ids)), 44)
        self.assertTrue(
            all(
                url.startswith("https://drive.google.com/thumbnail?")
                for url in map(drive_thumbnail_url, ids)
            )
        )

    def test_one_image_uses_static_figure_without_carousel_controls(self):
        html = gallery_markup("/treatments/acne-treatment/")
        self.assertIn("Clinical photographs", html)
        self.assertNotIn("data-clinical-carousel", html)
        self.assertNotIn("data-clinical-previous", html)
        self.assertIn("data-fallback-src", html)

    def test_multiple_images_use_accessible_non_autoplay_carousel(self):
        html = gallery_markup("/treatments/acne-scar-treatment/")
        self.assertIn("data-clinical-carousel", html)
        self.assertIn("data-clinical-previous", html)
        self.assertIn("data-clinical-next", html)
        self.assertIn('aria-live="polite"', html)
        self.assertIn("touchstart", html)
        self.assertIn("ArrowRight", html)
        self.assertNotIn("setInterval", html)
        self.assertNotIn("autoplay", html.lower())

    def test_hidden_slides_are_deferred(self):
        html = gallery_markup("/treatments/hair-fall-treatment/")
        self.assertEqual(html.count(' loading="lazy"'), 6)
        self.assertEqual(html.count(" data-src="), 5)
        self.assertEqual(html.count(" hidden>"), 5)

    def test_unknown_page_has_no_gallery(self):
        self.assertEqual(gallery_markup("/treatments/rosacea-treatment/"), "")

    def test_flexible_template_places_gallery_inside_page_content(self):
        template = (
            Path(__file__).resolve().parents[1]
            / "home"
            / "templates"
            / "home"
            / "flexible_page.html"
        ).read_text(encoding="utf-8")
        self.assertIn(
            "{% exact_page_with_clinical_results exact_main %}",
            template,
        )
        self.assertIn("{% clinical_result_gallery %}", template)
