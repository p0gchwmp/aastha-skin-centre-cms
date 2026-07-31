from pathlib import Path

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase


class SiteVisualCueTests(SimpleTestCase):
    CUES = (
        "acne",
        "pigmentation",
        "hair",
        "diagnosis",
        "experience",
        "locations",
        "complete",
        "plan",
        "laser",
        "clinical",
    )

    def setUp(self):
        css_path = finders.find("css/site-visual-cues.css")
        js_path = finders.find("js/site-visual-cues.js")
        self.assertIsNotNone(css_path)
        self.assertIsNotNone(js_path)
        self.stylesheet = Path(css_path).read_text(encoding="utf-8")
        self.script = Path(js_path).read_text(encoding="utf-8")
        root = Path(__file__).resolve().parents[1]
        self.base_template = (root / "aastha_cms" / "templates" / "base.html").read_text(
            encoding="utf-8"
        )
        self.sprite = (
            root
            / "home"
            / "templates"
            / "home"
            / "partials"
            / "pastel_clay_sprite.html"
        ).read_text(encoding="utf-8")

    def test_global_template_loads_visual_css_script_and_sprite(self):
        self.assertIn("css/site-visual-cues.css", self.base_template)
        self.assertIn("js/site-visual-cues.js", self.base_template)
        self.assertIn('home/partials/pastel_clay_sprite.html', self.base_template)
        self.assertLess(
            self.base_template.index("css/mobile-layout-qa.css"),
            self.base_template.index("css/site-visual-cues.css"),
        )

    def test_sprite_contains_ten_distinct_message_led_clay_scenes(self):
        for cue in self.CUES:
            with self.subTest(cue=cue):
                self.assertIn(f'id="clay-{cue}"', self.sprite)
        self.assertIn("#clay-${cue}", self.script)
        self.assertEqual(self.sprite.count("<symbol id=\"clay-"), 10)
        self.assertNotIn("<text", self.sprite)
        self.assertIn("clay-texture", self.sprite)
        self.assertIn("clay-shadow", self.sprite)

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

    def test_script_maps_broad_site_meaning_without_blocking_clinical_pages(self):
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
        self.assertNotIn("clinicalDetailPage", self.script)
        self.assertIn(".cms-card", self.script)
        self.assertIn("aria-hidden", self.script)

    def test_svg_is_injected_as_crisp_vector_not_as_a_text_glyph(self):
        self.assertIn("createElementNS", self.script)
        self.assertIn("message-visual__svg", self.script)
        self.assertIn("replaceChildren", self.script)
        self.assertIn("shape-rendering: geometricPrecision", self.stylesheet)
        self.assertNotIn("background-image: var(--visual-image)", self.stylesheet)

    def test_dark_mode_and_reduced_motion_preserve_detail(self):
        self.assertIn('html[data-theme="dark"] .message-visual', self.stylesheet)
        self.assertIn("brightness(.96)", self.stylesheet)
        self.assertIn("prefers-reduced-motion", self.stylesheet)
