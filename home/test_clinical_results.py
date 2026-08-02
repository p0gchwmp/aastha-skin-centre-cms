from pathlib import Path
from types import SimpleNamespace

from bs4 import BeautifulSoup
from django.contrib.staticfiles import finders
from django.test import SimpleTestCase

from home.clinical_results import CLINICAL_RESULT_GALLERIES
from home.clinical_results_local import (
    RESPONSIVE_WIDTHS,
    gallery_markup,
    hero_gallery_markup,
    local_asset_path,
    responsive_asset_path,
)
from home.templatetags.clinical_results import (
    exact_page_with_clinical_results,
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

    def test_source_drive_ids_remain_explicit_and_unique_for_provenance(self):
        ids = [
            image["id"]
            for gallery in CLINICAL_RESULT_GALLERIES.values()
            for image in gallery["images"]
        ]
        self.assertEqual(len(ids), 44)
        self.assertEqual(len(set(ids)), 44)

    def test_every_placement_has_a_local_webp(self):
        paths = [
            local_asset_path(route, index)
            for route, gallery in CLINICAL_RESULT_GALLERIES.items()
            for index in range(1, len(gallery["images"]) + 1)
        ]
        self.assertEqual(len(paths), 44)
        self.assertEqual(len(set(paths)), 44)
        for path in paths:
            self.assertTrue(path.endswith(".webp"))
            self.assertIsNotNone(finders.find(path), path)

    def test_responsive_candidate_paths_are_deterministic(self):
        route = "/treatments/acne-scar-treatment/"
        self.assertEqual(RESPONSIVE_WIDTHS, (384, 640, 768))
        for width in RESPONSIVE_WIDTHS:
            self.assertEqual(
                responsive_asset_path(route, 1, width),
                "images/clinical-results/acne-scar-treatment/"
                f"acne-scar-treatment-01-{width}w.webp",
            )
        self.assertEqual(
            responsive_asset_path(route, 1, 1200),
            local_asset_path(route, 1),
        )

    def test_runtime_markup_never_calls_google_drive(self):
        for route in CLINICAL_RESULT_GALLERIES:
            for html in (gallery_markup(route), hero_gallery_markup(route)):
                self.assertNotIn("drive.google.com", html)
                self.assertIn("/assets/images/clinical-results/", html)
                self.assertNotIn("data-fallback-src", html)

    def test_one_image_uses_static_figure_without_carousel_controls(self):
        html = gallery_markup("/treatments/acne-treatment/")
        soup = BeautifulSoup(html, "html.parser")
        gallery = soup.select_one("section.clinical-results")

        self.assertIsNotNone(gallery)
        self.assertIn("Clinical photographs", gallery.get_text(" ", strip=True))
        self.assertFalse(gallery.has_attr("data-clinical-carousel"))
        self.assertIsNone(gallery.select_one("[data-clinical-previous]"))
        image = gallery.select_one("img")
        self.assertIsNotNone(image)
        self.assertEqual(
            image.get("src"),
            "/assets/images/clinical-results/acne-treatment/acne-treatment-01.webp",
        )
        for width in RESPONSIVE_WIDTHS:
            self.assertIn(
                f"acne-treatment-01-{width}w.webp {width}w",
                image.get("srcset"),
            )
        self.assertIn("acne-treatment-01.webp 1200w", image.get("srcset"))
        self.assertTrue(image.get("sizes"))

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
        self.assertIn("event.key === 'Home'", html)
        self.assertIn("event.key === 'End'", html)
        self.assertNotIn("setInterval", html)
        self.assertNotIn("autoplay", html.lower())

    def test_hidden_slides_are_deferred(self):
        html = gallery_markup("/treatments/hair-fall-treatment/")
        soup = BeautifulSoup(html, "html.parser")
        slides = soup.select("[data-clinical-slide]")

        self.assertEqual(len(slides), 6)
        self.assertEqual(sum(slide.has_attr("hidden") for slide in slides), 5)
        self.assertEqual(len(soup.select("[data-clinical-slide] img[data-src]")), 5)
        self.assertEqual(
            len(soup.select("[data-clinical-slide] img[data-srcset]")),
            5,
        )
        self.assertEqual(
            len(soup.select("[data-clinical-slide] img[data-sizes]")),
            5,
        )
        self.assertEqual(
            len(soup.select('[data-clinical-slide] img[loading="lazy"]')),
            6,
        )
        self.assertIn("image.dataset.sizes", html)
        self.assertIn("image.dataset.srcset", html)

    def test_hero_gallery_uses_real_responsive_photograph_and_compact_controls(self):
        html = hero_gallery_markup("/treatments/acne-scar-treatment/")
        soup = BeautifulSoup(html, "html.parser")
        gallery = soup.select_one("section.clinical-results--hero")

        self.assertIsNotNone(gallery)
        self.assertTrue(gallery.has_attr("data-clinical-carousel"))
        first_image = gallery.select_one("[data-clinical-slide] img")
        self.assertEqual(first_image.get("loading"), "eager")
        self.assertEqual(first_image.get("fetchpriority"), "high")
        self.assertEqual(
            first_image.get("src"),
            "/assets/images/clinical-results/acne-scar-treatment/"
            "acne-scar-treatment-01.webp",
        )
        for width in RESPONSIVE_WIDTHS:
            self.assertIn(
                f"acne-scar-treatment-01-{width}w.webp {width}w",
                first_image.get("srcset"),
            )
        self.assertIn(
            "acne-scar-treatment-01.webp 1200w",
            first_image.get("srcset"),
        )
        self.assertIn("max-width: 760px", first_image.get("sizes"))
        self.assertIn("382px", first_image.get("sizes"))
        self.assertEqual(
            len(gallery.select("[data-clinical-slide] img[data-src]")),
            3,
        )
        self.assertEqual(
            len(gallery.select("[data-clinical-slide] img[data-srcset]")),
            3,
        )
        self.assertEqual(
            gallery.select_one("[data-clinical-previous]").get_text(
                " ", strip=True
            ),
            "←",
        )
        self.assertEqual(
            gallery.select_one("[data-clinical-next]").get_text(
                " ", strip=True
            ),
            "→",
        )

    def test_local_dimensions_match_materialised_source_bound(self):
        html = hero_gallery_markup("/treatments/hair-fall-treatment/")
        soup = BeautifulSoup(html, "html.parser")
        first_image = soup.select_one("[data-clinical-slide] img")

        self.assertEqual(first_image.get("width"), "1200")
        self.assertEqual(first_image.get("height"), "1200")

    def test_deferred_images_do_not_trigger_false_load_error(self):
        html = hero_gallery_markup("/treatments/acne-scar-treatment/")
        soup = BeautifulSoup(html, "html.parser")
        error = soup.select_one("[data-clinical-error]")

        self.assertIsNotNone(error)
        self.assertTrue(error.has_attr("hidden"))
        self.assertIn("image.hasAttribute('src')", html)
        self.assertNotIn("dispatchEvent(new Event('error'))", html)
        self.assertIn(
            ".clinical-results__load-error[hidden]",
            html,
        )

    def test_exact_page_places_gallery_inside_existing_hero_art(self):
        source = (
            '<main id="main-content">'
            '<section class="page-hero page-hero--professional">'
            '<div class="container">'
            '<div class="page-hero-copy"><h1>Acne scars</h1></div>'
            '<div class="page-hero-art">'
            '<img src="/assets/images/professional/acne-care.svg" '
            'alt="Decorative illustration">'
            "</div>"
            "</div></section>"
            "<p>Body copy</p>"
            "</main>"
        )
        context = {
            "request": SimpleNamespace(
                path_info="/treatments/acne-scar-treatment/"
            ),
            "page": SimpleNamespace(url=""),
        }

        rendered = str(exact_page_with_clinical_results(context, source))
        soup = BeautifulSoup(rendered, "html.parser")
        hero_art = soup.select_one(".page-hero-art")

        self.assertIsNotNone(hero_art)
        self.assertIsNotNone(
            hero_art.select_one(
                'img[src="/assets/images/professional/acne-care.svg"]'
            )
        )
        self.assertIsNotNone(
            hero_art.select_one("section.clinical-results--hero")
        )
        self.assertEqual(
            len(soup.select("section.clinical-results")),
            1,
        )
        self.assertNotIn(
            "1 clinic-supplied photograph",
            rendered,
        )

    def test_unknown_page_has_no_gallery(self):
        self.assertEqual(gallery_markup("/treatments/rosacea-treatment/"), "")
        self.assertEqual(
            hero_gallery_markup("/treatments/rosacea-treatment/"),
            "",
        )

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

        self.assertIn(
            "document.querySelectorAll('.clinical-results')",
            browser_parity,
        )
        self.assertIn("audit_clinical_result_galleries_browser.py", workflow)
        self.assertIn("CLINICAL_RESULT_GALLERIES", gallery_browser)
        self.assertIn("naturalWidth > 0", gallery_browser)
        self.assertIn("data-clinical-next", gallery_browser)
        self.assertIn("horizontal_overflow", gallery_browser)
        self.assertIn("page.wait_for_timeout(850)", gallery_browser)
