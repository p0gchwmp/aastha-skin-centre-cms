from pathlib import Path

from django.test import SimpleTestCase


class VisualLayoutRegressionTests(SimpleTestCase):
    def setUp(self):
        root = Path(__file__).resolve().parents[1]
        self.stylesheet = (
            root / "aastha_cms" / "static" / "css" / "site-visual-cues.css"
        ).read_text(encoding="utf-8")
        self.script = (
            root / "home" / "static" / "js" / "site-visual-cues.js"
        ).read_text(encoding="utf-8")
        self.base_template = (
            root / "aastha_cms" / "templates" / "base.html"
        ).read_text(encoding="utf-8")
        self.parity_audit = (
            root / "tools" / "audit_browser_parity_hydrated.py"
        ).read_text(encoding="utf-8")

    def test_corrections_use_existing_asset_requests(self):
        self.assertEqual(self.base_template.count("css/site-visual-cues.css"), 1)
        self.assertEqual(self.base_template.count("js/site-visual-cues.js"), 1)
        self.assertNotIn("visual_layout_fixes_css.html", self.base_template)
        self.assertNotIn("visual_layout_fixes_js.html", self.base_template)
        self.assertNotIn("site-visual-layout-fixes", self.base_template)
        self.assertNotIn("css/site-visual-layout-fixes.css", self.base_template)
        self.assertNotIn("js/site-visual-layout-fixes.js", self.base_template)
        self.assertIn("Visual-cue layout corrections", self.stylesheet)
        self.assertIn("Semantic correction pass", self.script)

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
        self.assertIn("visuals.slice(1)", self.script)

    def test_hyphenated_headings_are_normalised_before_matching(self):
        self.assertIn(".replace(/[^a-z0-9\\s]/g, ' ')", self.script)
        self.assertIn("'doctor led care'", self.script)

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

    def test_parity_audit_removes_combined_clay_stylesheet(self):
        self.assertIn("site-visual-cues.css", self.parity_audit)
        self.assertIn("visual-cue-card--managed", self.parity_audit)
        self.assertIn("hub-category-heading--clay", self.parity_audit)
