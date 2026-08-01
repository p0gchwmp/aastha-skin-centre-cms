from pathlib import Path

from bs4 import BeautifulSoup
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
        soup = BeautifulSoup(html, "html.parser")
        gallery = soup.select_one("section.clinical-results")

        self.assertIsNotNone(gallery)
        self.assertIn("Clinical photographs", gallery.get_text(" ", strip=True))
        self.assertFalse(gallery.has_attr("data-clinical-carousel"))
        self.assertIsNone(gallery.select_one("[data-clinical-previous]"))
        self.assertIsNotNone(gallery.select_one("img[data-fallback-src]"))

    def test_multiple_images_use_accessible_non_autoplay_carousel(self):
        html = gallery_markup("/treatments/acne-scar-treatment/")
        soup = BeautifulSoup(html, "html.parser")
        gallery = soup.select_one("section.clinical-results")

        self.assertIsNotNone(gallery)
        self.assertTrue(gallery.has_attr("data-clinical-carousel"))
        self.assertIsNotNone(gallery.select_one("[data-clinical-previous]"))
        self.assertIsNotNone(gallery.select_one("[data-clinical-next]"))
        self.assertIsNotNone(gallery.select_one('[aria-live="polite"]'))
        self.assertIn("touchstart", html)
        self.assertIn("ArrowRight", html)
        self.assertNotIn("setInterval", html)
        self.assertNotIn("autoplay", html.lower())

    def test_hidden_slides_are_deferred(self):
        html = gallery_markup("/treatments/hair-fall-treatment/")
        soup = BeautifulSoup(html, "html.parser")
        slides = soup.select("[data-clinical-slide]")

        self.assertEqual(len(slides), 6)
        self.assertEqual(sum(slide.has_attr("hidden") for slide in slides), 5)
        self.assertEqual(len(soup.select("[data-clinical-slide] img[data-src]")), 5)
        self.assertEqual(len(soup.select('[data-clinical-slide] img[loading="lazy"]')), 6)

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

    def test_legacy_parity_wrapper_is_narrow_and_remains_strict(self):
        wrapper = (
            Path(__file__).resolve().parents[1]
            / "tools"
            / "audit_deployed_sites_with_extensions.py"
        ).read_text(encoding="utf-8")
        workflow = (
            Path(__file__).resolve().parents[1]
            / ".github"
            / "workflows"
            / "prelaunch-parity.yml"
        ).read_text(encoding="utf-8")

        self.assertIn('clone.select(".clinical-results")', wrapper)
        self.assertIn('clone.find_all(["style", "script"])', wrapper)
        self.assertIn('if "clinical-results" in source', wrapper)
        self.assertIn("parity.normalise_main = normalise_main", wrapper)
        self.assertIn("parity.headings = headings", wrapper)
        self.assertNotIn("allow_main_differences", wrapper)
        self.assertIn("audit_deployed_sites_with_extensions.py", workflow)
        self.assertNotIn("--allow-main-differences", workflow)

    def test_visual_parity_masks_only_gallery_and_browser_audit_covers_it(self):
        browser_parity = (
            Path(__file__).resolve().parents[1]
            / "tools"
            / "audit_browser_parity_hydrated.py"
        ).read_text(encoding="utf-8")
        gallery_browser = (
            Path(__file__).resolve().parents[1]
            / "tools"
            / "audit_clinical_result_galleries_browser.py"
        ).read_text(encoding="utf-8")
        workflow = (
            Path(__file__).resolve().parents[1]
            / ".github"
            / "workflows"
            / "prelaunch-parity.yml"
        ).read_text(encoding="utf-8")

        self.assertIn("document.querySelectorAll('.clinical-results')", browser_parity)
        self.assertIn("audit_clinical_result_galleries_browser.py", workflow)
        self.assertIn("CLINICAL_RESULT_GALLERIES", gallery_browser)
        self.assertIn("naturalWidth > 0", gallery_browser)
        self.assertIn("data-clinical-next", gallery_browser)
        self.assertIn("horizontal_overflow", gallery_browser)
        self.assertIn("page.wait_for_timeout(850)", gallery_browser)
