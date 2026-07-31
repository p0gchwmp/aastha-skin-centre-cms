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

    def test_global_template_loads_visual_css_script_and_asset_manifest(self):
        self.assertIn("css/site-visual-cues.css", self.base_template)
        self.assertIn("js/site-visual-cues.js", self.base_template)
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

    def test_script_injects_responsive_images_not_a_vector_sprite(self):
        self.assertIn("message-visual__img", self.script)
        self.assertIn("image.srcset", self.script)
        self.assertIn("128w", self.script)
        self.assertIn("256w", self.script)
        self.assertIn("512w", self.script)
        self.assertIn("image.sizes", self.script)
        self.assertIn("decoding = 'async'", self.script)
        self.assertIn("element.replaceChildren(image)", self.script)
        self.assertNotIn("createElementNS", self.script)
        self.assertNotIn("message-visual__svg", self.script)
        self.assertNotIn("background-size: 500% 200%", self.stylesheet)

    def test_homepage_concerns_and_credibility_have_explicit_semantics(self):
        for cue in (
            "['acne', 'pigmentation', 'hair']",
            "['diagnosis', 'experience', 'locations', 'complete', 'plan']",
        ):
            self.assertIn(cue, self.script)
        self.assertIn(".concern-card:nth-child(-n + 3)", self.stylesheet)
        self.assertIn(".trust-item .trust-icon", self.stylesheet)
        self.assertIn("116px", self.stylesheet)
        self.assertIn("94px", self.stylesheet)

    def test_script_maps_site_meaning_without_replacing_real_photography(self):
        for term in (
            "acne",
            "melasma",
            "laser hair reduction",
            "hair fall",
            "fungal infection",
            "eczema",
            "doctor-led",
            "20 years",
            "karan nagar",
            "complete care",
            "treatment plan",
        ):
            self.assertIn(term, self.script)
        for protected in (
            ".treatment-card",
            ".condition-card",
            ".doctor-card",
            ".doctor-profile",
            ".page-hero-art",
        ):
            self.assertIn(protected, self.script)
        self.assertIn(".cms-card", self.script)
        self.assertIn("aria-hidden", self.script)

    def test_dark_mode_and_reduced_motion_preserve_artwork(self):
        self.assertIn('html[data-theme="dark"] .message-visual', self.stylesheet)
        self.assertIn("brightness(.90)", self.stylesheet)
        self.assertIn("prefers-reduced-motion", self.stylesheet)
