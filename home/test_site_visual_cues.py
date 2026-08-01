from pathlib import Path
import subprocess
import sys

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase
from PIL import Image


class SiteVisualCueTests(SimpleTestCase):
    ASSETS = {
        "acne": "acne-care",
        "pigmentation": "pigmentation-care",
        "hair": "hair-scalp-care",
        "diagnosis": "dermatologist-diagnosis",
        "experience": "medical-experience",
        "locations": "two-clinic-locations",
        "complete": "complete-care",
        "plan": "personalised-plan",
        "laser": "advanced-laser-care",
        "clinical": "clinical-skin-care",
    }
    SIZES = (128, 256, 512)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.root = Path(__file__).resolve().parents[1]
        subprocess.run(
            [sys.executable, str(cls.root / "tools" / "build_visual_cue_assets.py")],
            cwd=cls.root,
            check=True,
            capture_output=True,
            text=True,
        )

    def setUp(self):
        css_path = finders.find("css/site-visual-cues.css")
        js_path = finders.find("js/site-visual-cues.js")
        self.assertIsNotNone(css_path)
        self.assertIsNotNone(js_path)
        self.stylesheet = Path(css_path).read_text(encoding="utf-8")
        self.script = Path(js_path).read_text(encoding="utf-8")

        self.base_template = (
            self.root / "aastha_cms" / "templates" / "base.html"
        ).read_text(encoding="utf-8")
        self.asset_manifest = (
            self.root
            / "home"
            / "templates"
            / "home"
            / "partials"
            / "pastel_clay_sprite.html"
        ).read_text(encoding="utf-8")
        self.generator = (
            self.root / "tools" / "build_visual_cue_assets.py"
        ).read_text(encoding="utf-8")

    def test_global_template_loads_one_visual_css_script_and_asset_manifest(self):
        self.assertEqual(self.base_template.count("css/site-visual-cues.css"), 1)
        self.assertEqual(self.base_template.count("js/site-visual-cues.js"), 1)
        self.assertIn("home/partials/pastel_clay_sprite.html", self.base_template)
        self.assertIn('id="visual-cue-assets"', self.asset_manifest)
        self.assertNotIn("<svg", self.asset_manifest)
        self.assertLess(
            self.base_template.index("css/mobile-layout-qa.css"),
            self.base_template.index("css/site-visual-cues.css"),
        )

    def test_build_expands_four_sources_into_thirty_transparent_webps(self):
        self.assertIn('"group-a-128.webp"', self.generator)
        self.assertIn('"group-b-128.webp"', self.generator)
        self.assertIn("Image.Resampling.LANCZOS", self.generator)
        self.assertIn("lossless=True", self.generator)

        for cue, slug in self.ASSETS.items():
            for size in self.SIZES:
                with self.subTest(cue=cue, size=size):
                    relative = f"images/visual-cues/{slug}-{size}.webp"
                    asset_path = finders.find(relative)
                    self.assertIsNotNone(asset_path)
                    with Image.open(asset_path) as image:
                        self.assertEqual(image.format, "WEBP")
                        self.assertEqual(image.size, (size, size))
                        self.assertIn("A", image.getbands())
                        self.assertEqual(image.getchannel("A").getextrema(), (0, 255))
                    self.assertIn(relative, self.asset_manifest)

    def test_script_uses_responsive_raster_images_and_restores_failed_icons(self):
        self.assertIn("message-visual__img", self.script)
        self.assertIn("image.srcset", self.script)
        self.assertIn("128w", self.script)
        self.assertIn("256w", self.script)
        self.assertIn("512w", self.script)
        self.assertIn("image.sizes", self.script)
        self.assertIn("image.loading = 'lazy'", self.script)
        self.assertNotIn("image.loading = 'eager'", self.script)
        self.assertIn("decoding = 'async'", self.script)
        self.assertIn("element.replaceChildren(image)", self.script)
        self.assertIn("restoreOriginal(element)", self.script)
        self.assertNotIn("createElementNS", self.script)
        self.assertNotIn("message-visual__svg", self.script)

    def test_existing_placeholders_only_are_upgraded(self):
        self.assertIn("const PLACEHOLDER_SELECTOR", self.script)
        self.assertIn("'.hub-icon'", self.script)
        self.assertIn("document.querySelectorAll(PLACEHOLDER_SELECTOR)", self.script)
        self.assertNotIn("createElement('span')", self.script)
        self.assertNotIn("insertBefore", self.script)
        self.assertNotIn("visual-cue-card--managed", self.script)
        self.assertNotIn("hub-category-heading--clay", self.script)

    def test_category_meaning_is_taken_from_the_heading_not_child_links(self):
        self.assertIn("const headingLabel", self.script)
        self.assertIn(".hub-category-heading", self.script)
        self.assertIn("querySelector('h1, h2, h3, h4, strong')", self.script)
        self.assertNotIn("context.textContent", self.script)

        expected = {
            "medical dermatology": "clinical",
            "procedural and aesthetic care": "laser",
            "acne scars and resurfacing": "acne",
            "pigmentation and laser treatments": "pigmentation",
            "hair and scalp treatments": "hair",
            "aesthetic and anti ageing": "complete",
            "minor procedures and dermatosurgery": "diagnosis",
        }
        for label, cue in expected.items():
            with self.subTest(label=label, cue=cue):
                self.assertIn(f"['{label}', '{cue}']", self.script)

    def test_homepage_credibility_icons_have_distinct_explicit_semantics(self):
        self.assertIn(
            "const cues = ['diagnosis', 'experience', 'locations', 'complete', 'plan']",
            self.script,
        )
        self.assertIn(".trust-item .trust-icon", self.script)

    def test_visual_css_keeps_original_slot_sizes_and_does_not_reflow_cards(self):
        for size in ("54px", "42px", "46px"):
            self.assertIn(size, self.stylesheet)
        self.assertIn(".hub-icon.message-visual", self.stylesheet)
        self.assertIn(".icon-bubble.message-visual", self.stylesheet)
        self.assertIn(".trust-icon.message-visual", self.stylesheet)

        for forbidden in (
            "grid-auto-rows",
            "height: 100% !important",
            "margin-top: auto !important",
            ".clinic-location-grid",
            ".location-contact-grid",
            ".clinic-choice-grid",
            "grid-template-columns: 96px",
        ):
            self.assertNotIn(forbidden, self.stylesheet)

    def test_dark_mode_and_reduced_motion_preserve_artwork(self):
        self.assertIn('html[data-theme="dark"] .message-visual__img', self.stylesheet)
        self.assertIn("prefers-reduced-motion", self.stylesheet)
