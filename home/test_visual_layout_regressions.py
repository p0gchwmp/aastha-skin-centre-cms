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

    def test_rebuild_uses_the_existing_css_and_js_request_budget(self):
        self.assertEqual(self.base_template.count("css/site-visual-cues.css"), 1)
        self.assertEqual(self.base_template.count("js/site-visual-cues.js"), 1)
        self.assertNotIn("site-visual-layout-fixes", self.base_template)
        self.assertIn("Aastha semantic visual cues", self.stylesheet)
        self.assertIn("EXACT_LABEL_CUES", self.script)

    def test_known_repetitive_sections_receive_distinct_relevant_cues(self):
        expected_pairs = {
            "medical dermatology": "clinical",
            "procedural and aesthetic care": "laser",
            "hair and scalp treatments": "hair",
            "aesthetic and anti ageing": "complete",
            "acne scars and resurfacing": "acne",
            "pigmentation and laser treatments": "pigmentation",
            "doctor led care": "plan",
            "diagnosis first": "diagnosis",
            "fungal and recurrent infections": "clinical",
            "allergy eczema and itching": "complete",
        }
        for phrase, cue in expected_pairs.items():
            with self.subTest(phrase=phrase, cue=cue):
                self.assertIn(f"['{phrase}', '{cue}']", self.script)

    def test_heading_only_matching_prevents_child_links_from_hijacking_parent_icon(self):
        self.assertIn("const headingLabel", self.script)
        self.assertIn(".hub-category-heading", self.script)
        self.assertIn("querySelector('h1, h2, h3, h4, strong')", self.script)
        self.assertNotIn("owner.textContent", self.script)
        self.assertNotIn("context.textContent", self.script)

    def test_icons_never_create_or_reposition_layout_nodes(self):
        for forbidden in (
            "createElement('span')",
            "insertBefore",
            "visual-cue-card--managed",
            "hub-category-heading--clay",
            "owner.classList.add",
        ):
            self.assertNotIn(forbidden, self.script)

    def test_hub_icons_keep_the_static_54px_desktop_and_46px_mobile_slot(self):
        self.assertIn(".hub-icon.message-visual", self.stylesheet)
        self.assertIn("width: 54px !important", self.stylesheet)
        self.assertIn("height: 54px !important", self.stylesheet)
        self.assertIn("@media (max-width: 700px)", self.stylesheet)
        self.assertIn("width: 46px !important", self.stylesheet)
        self.assertNotIn("grid-template-columns: 96px", self.stylesheet)

    def test_visual_layer_does_not_change_card_or_clinic_geometry(self):
        for forbidden in (
            ".about-story-grid",
            ".clinic-location-grid",
            ".location-contact-grid",
            ".hours-grid",
            ".location-pro-grid",
            ".clinic-choice-grid",
            "grid-auto-rows",
            "height: 100% !important",
            "margin-top: auto !important",
            "display: flex !important",
        ):
            self.assertNotIn(forbidden, self.stylesheet)

    def test_failed_asset_restores_the_original_glyph(self):
        self.assertIn("const restoreOriginal", self.script)
        self.assertIn("image.addEventListener('error'", self.script)
        self.assertNotIn("setAttribute('hidden'", self.script)

    def test_parity_audit_restores_original_markup_and_removes_visual_stylesheet(self):
        self.assertIn("data-visual-original-html", self.parity_audit)
        self.assertIn("site-visual-cues.css", self.parity_audit)
        self.assertIn("icon.innerHTML = originalHtml", self.parity_audit)
