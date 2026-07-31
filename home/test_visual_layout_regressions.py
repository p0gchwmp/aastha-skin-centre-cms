from pathlib import Path

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase


class VisualLayoutRegressionTests(SimpleTestCase):
    def setUp(self):
        css_path = finders.find("css/site-visual-layout-fixes.css")
        js_path = finders.find("js/site-visual-layout-fixes.js")
        self.assertIsNotNone(css_path)
        self.assertIsNotNone(js_path)

        self.stylesheet = Path(css_path).read_text(encoding="utf-8")
        self.script = Path(js_path).read_text(encoding="utf-8")
        root = Path(__file__).resolve().parents[1]
        self.base_template = (
            root / "aastha_cms" / "templates" / "base.html"
        ).read_text(encoding="utf-8")

    def test_corrective_assets_load_after_the_base_visual_system(self):
        self.assertIn("css/site-visual-layout-fixes.css", self.base_template)
        self.assertIn("js/site-visual-layout-fixes.js", self.base_template)
        self.assertLess(
            self.base_template.index("css/site-visual-cues.css"),
            self.base_template.index("css/site-visual-layout-fixes.css"),
        )
        self.assertLess(
            self.base_template.index("js/site-visual-cues.js"),
            self.base_template.index("js/site-visual-layout-fixes.js"),
        )

    def test_repetitive_examples_receive_distinct_semantic_cues(self):
        expected_pairs = {
            "doctor led care": "plan",
            "diagnosis first": "diagnosis",
            "fungal and recurrent infections": "clinical",
            "allergy eczema and itching": "complete",
            "acne pimples and breakouts": "acne",
            "pigmentation and colour changes": "pigmentation",
            "hair scalp and unwanted hair": "hair",
        }
        for phrase, cue in expected_pairs.items():
            with self.subTest(phrase=phrase, cue=cue):
                self.assertIn(f"'{phrase}'", self.script)
                self.assertIn(f"cue: '{cue}'", self.script)

        self.assertIn(
            "const PROCESS_FALLBACKS = ['plan', 'diagnosis', 'complete', 'experience']",
            self.script,
        )
        self.assertIn("removeOwnedDuplicates", self.script)

    def test_hub_icons_reserve_space_and_stack_on_mobile(self):
        self.assertIn(".hub-category-heading--clay", self.stylesheet)
        self.assertIn(
            "grid-template-columns: 96px minmax(0, 1fr) !important",
            self.stylesheet,
        )
        self.assertIn("@media (max-width: 720px)", self.stylesheet)
        self.assertIn(
            "grid-template-columns: minmax(0, 1fr) !important",
            self.stylesheet,
        )
        self.assertIn("hubHeading.insertBefore", self.script)

    def test_managed_cards_never_use_overlay_positioning(self):
        for marker in (
            "position: relative !important",
            "inset: auto !important",
            "float: none !important",
            "align-self: flex-start !important",
            "background: transparent !important",
        ):
            self.assertIn(marker, self.stylesheet)
        self.assertIn("owner.insertBefore(host, owner.firstElementChild)", self.script)

    def test_failed_assets_disappear_instead_of_leaving_blank_boxes(self):
        self.assertIn("message-visual--failed", self.script)
        self.assertIn("host.setAttribute('hidden', '')", self.script)
        self.assertIn(".message-visual[hidden]", self.stylesheet)

    def test_desktop_about_and_clinic_panels_are_equal_height(self):
        for selector in (
            ".about-story-grid",
            ".clinic-location-grid",
            ".location-contact-grid",
            ".hours-grid",
            ".location-pro-grid",
            ".clinic-choice-grid",
        ):
            self.assertIn(selector, self.stylesheet)
        self.assertIn("grid-auto-rows: 1fr", self.stylesheet)
        self.assertIn("height: 100% !important", self.stylesheet)
        self.assertIn("margin-top: auto !important", self.stylesheet)
