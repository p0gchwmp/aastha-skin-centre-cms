from pathlib import Path

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase


class SiteVisualCueTests(SimpleTestCase):
    VISUALS = (
        "acne-care.svg",
        "pigmentation-care.svg",
        "hair-scalp-care.svg",
        "dermatologist-diagnosis.svg",
        "medical-experience.svg",
        "two-clinic-locations.svg",
        "complete-care.svg",
        "personalised-plan.svg",
    )

    def setUp(self):
        css_path = finders.find("css/site-visual-cues.css")
        js_path = finders.find("js/site-visual-cues.js")
        self.assertIsNotNone(css_path)
        self.assertIsNotNone(js_path)
        self.stylesheet = Path(css_path).read_text(encoding="utf-8")
        self.script = Path(js_path).read_text(encoding="utf-8")
        self.base_template = (
            Path(__file__).resolve().parents[1]
            / "aastha_cms"
            / "templates"
            / "base.html"
        ).read_text(encoding="utf-8")

    def test_global_template_loads_visual_css_and_script(self):
        self.assertIn("css/site-visual-cues.css", self.base_template)
        self.assertIn("js/site-visual-cues.js", self.base_template)
        self.assertLess(
            self.base_template.index("css/mobile-layout-qa.css"),
            self.base_template.index("css/site-visual-cues.css"),
        )

    def test_all_message_visual_assets_are_public_static_files(self):
        for filename in self.VISUALS:
            with self.subTest(filename=filename):
                self.assertIsNotNone(
                    finders.find(f"icons/message-visuals/{filename}")
                )
                self.assertIn(filename, self.stylesheet)

    def test_homepage_concerns_and_credibility_have_explicit_visuals(self):
        for cue in (
            "acne-care.svg",
            "pigmentation-care.svg",
            "hair-scalp-care.svg",
            "dermatologist-diagnosis.svg",
            "medical-experience.svg",
            "two-clinic-locations.svg",
            "complete-care.svg",
            "personalised-plan.svg",
        ):
            self.assertIn(cue, self.stylesheet)
        self.assertIn(".concern-card:nth-child(1)", self.stylesheet)
        self.assertIn(".trust-item:nth-child(5)", self.stylesheet)

    def test_script_maps_meaning_and_protects_large_clinical_images(self):
        for term in (
            "acne", "melasma", "hair fall", "doctor-led", "experience",
            "karan nagar", "complete care", "treatment plan",
        ):
            self.assertIn(term, self.script)
        for protected in (
            ".treatment-card", ".condition-card", ".doctor-card",
            ".doctor-profile", ".page-hero-art",
        ):
            self.assertIn(protected, self.script)
        self.assertIn("clinicalDetailPage", self.script)
        self.assertIn("aria-hidden", self.script)

    def test_dark_mode_and_reduced_motion_are_supported(self):
        self.assertIn('html[data-theme="dark"] .message-visual', self.stylesheet)
        self.assertIn("prefers-reduced-motion", self.stylesheet)
