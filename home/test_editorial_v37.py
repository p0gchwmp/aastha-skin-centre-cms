from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

from django.contrib.staticfiles import finders
from django.template.loader import get_template, render_to_string
from django.test import SimpleTestCase

from home.context_processors import _env_flag
from home.templatetags.editorial_v37 import EDITORIAL_V37_TEMPLATES


class EditorialV37RolloutTests(SimpleTestCase):
    def test_flag_defaults_off(self):
        with patch.dict(os.environ, {}, clear=False):
            os.environ.pop("AASTHA_EDITORIAL_V37", None)
            self.assertFalse(_env_flag("AASTHA_EDITORIAL_V37"))

    def test_flag_accepts_explicit_truthy_values_only(self):
        for value in ("1", "true", "TRUE", "yes", "on"):
            with self.subTest(value=value), patch.dict(
                os.environ, {"AASTHA_EDITORIAL_V37": value}
            ):
                self.assertTrue(_env_flag("AASTHA_EDITORIAL_V37"))

        for value in ("0", "false", "off", "no", "banana"):
            with self.subTest(value=value), patch.dict(
                os.environ, {"AASTHA_EDITORIAL_V37": value}
            ):
                self.assertFalse(_env_flag("AASTHA_EDITORIAL_V37"))

    def test_asset_partial_is_empty_when_flag_is_off(self):
        markup = render_to_string(
            "home/partials/editorial_v37_assets.html",
            {"editorial_v37_enabled": False},
        )
        self.assertNotIn("editorial-v37", markup)
        self.assertNotIn("editorialVersion", markup)

    def test_asset_partial_loads_versioned_skin_when_flag_is_on(self):
        markup = render_to_string(
            "home/partials/editorial_v37_assets.html",
            {"editorial_v37_enabled": True},
        )
        for asset in (
            "editorial-v37",
            "editorial-v37-home",
            "editorial-v37-detail",
            "editorial-v37-conversion",
            "editorial-v37-shell",
            "editorial-v37-index",
        ):
            self.assertRegex(markup, rf"{asset}(?:\.[0-9a-f]+)?\.css")
        for asset in (
            "editorial-v37",
            "editorial-v37-home",
            "editorial-v37-detail",
            "editorial-v37-shell",
            "editorial-v37-index",
        ):
            self.assertRegex(markup, rf"{asset}(?:\.[0-9a-f]+)?\.js")
        self.assertIn("editorialVersion='37'", markup)
        self.assertIn("Cormorant+Garamond", markup)
        self.assertIn("Manrope", markup)

    def test_editorial_assets_exist_and_are_scoped(self):
        assets = {
            "css/editorial-v37.css": "html.editorial-v37",
            "css/editorial-v37-home.css": "html.editorial-v37",
            "css/editorial-v37-detail.css": "html.editorial-v37",
            "css/editorial-v37-conversion.css": "html.editorial-v37",
            "css/editorial-v37-shell.css": "html.editorial-v37",
            "css/editorial-v37-index.css": "html.editorial-v37",
            "js/editorial-v37.js": 'classList.contains("editorial-v37")',
            "js/editorial-v37-home.js": 'classList.contains("editorial-v37")',
            "js/editorial-v37-detail.js": 'classList.contains("editorial-v37")',
            "js/editorial-v37-shell.js": 'classList.contains("editorial-v37")',
            "js/editorial-v37-index.js": 'classList.contains("editorial-v37")',
        }
        for path, scope in assets.items():
            with self.subTest(path=path):
                file_path = finders.find(path)
                self.assertTrue(file_path)
                source = Path(file_path).read_text(encoding="utf-8")
                self.assertIn(scope, source)

        css = Path(finders.find("css/editorial-v37.css")).read_text(encoding="utf-8")
        detail_css = Path(finders.find("css/editorial-v37-detail.css")).read_text(encoding="utf-8")
        shell_js = Path(finders.find("js/editorial-v37-shell.js")).read_text(encoding="utf-8")
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn("clinical-result", css)
        self.assertIn("prefers-reduced-motion", detail_css)
        self.assertIn("Find your route", shell_js)
        self.assertIn("Book consultation", shell_js)
        self.assertIn("data-v37-explore-trigger", shell_js)

    def test_homepage_switch_preserves_legacy_renderer_as_rollback(self):
        root = Path(__file__).resolve().parents[1] / "home" / "templates" / "home"
        source = (root / "home_page.html").read_text(encoding="utf-8")
        self.assertIn("{% if editorial_v37_enabled %}", source)
        self.assertIn('home/editorial_v37/homepage.html', source)
        self.assertIn("{% exact_page_main as exact_main %}", source)
        self.assertIn("premium-minimal-preview.js", source)
        self.assertIn("{% if not editorial_v37_enabled %}", source)

    def test_flexible_renderer_keeps_legacy_fallback_for_unmigrated_routes(self):
        root = Path(__file__).resolve().parents[1] / "home" / "templates" / "home"
        source = (root / "flexible_page.html").read_text(encoding="utf-8")
        self.assertIn("editorial_v37_template_for page", source)
        self.assertIn("editorial_v37_enabled and editorial_v37_template", source)
        self.assertIn("{% exact_page_main as exact_main %}", source)
        self.assertIn("exact_page_with_editor_sections", source)

    def test_content_indexes_use_editorial_directory_when_enabled(self):
        root = Path(__file__).resolve().parents[1] / "home" / "templates" / "home"
        source = (root / "content_index_page.html").read_text(encoding="utf-8")
        directory = (root / "editorial_v37" / "index.html").read_text(encoding="utf-8")
        self.assertIn("{% if editorial_v37_enabled %}", source)
        self.assertIn('home/editorial_v37/index.html', source)
        self.assertIn("data-v37-directory-search", directory)
        self.assertIn("data-v37-directory-card", directory)
        self.assertIn("{% pageurl entry %}", directory)

    def test_priority_routes_have_dedicated_editorial_templates(self):
        expected = {
            "acne-treatment",
            "acne-scar-treatment",
            "pigmentation-treatment",
            "melasma-treatment",
            "fungal-infection-treatment",
            "hair-fall-treatment",
            "hair-transplant",
            "laser-hair-reduction",
            "botulinum-toxin-dermal-fillers",
            "book-appointment",
            "contact",
            "dr-cheena-langer",
            "karan-nagar",
            "paloura",
        }
        self.assertTrue(expected.issubset(EDITORIAL_V37_TEMPLATES))
        for slug in expected:
            with self.subTest(slug=slug):
                template_name = EDITORIAL_V37_TEMPLATES[slug]
                self.assertIsNotNone(get_template(template_name))

    def test_migrated_templates_use_production_routes_and_keep_cms_tail(self):
        root = Path(__file__).resolve().parents[1] / "home" / "templates" / "home" / "editorial_v37"
        templates = [
            root / "doctor.html",
            root / "clinic.html",
            root / "booking.html",
            root / "contact.html",
            root / "treatments" / "acne-treatment.html",
            root / "treatments" / "acne-scar-treatment.html",
            root / "treatments" / "pigmentation-treatment.html",
            root / "treatments" / "melasma-treatment.html",
            root / "treatments" / "fungal-infection-treatment.html",
            root / "treatments" / "hair-fall-treatment.html",
            root / "treatments" / "hair-transplant.html",
            root / "treatments" / "laser-hair-reduction.html",
            root / "treatments" / "botulinum-toxin-dermal-fillers.html",
        ]
        for template_path in templates:
            source = template_path.read_text(encoding="utf-8")
            with self.subTest(template=template_path.name):
                self.assertNotIn("/concept/", source)
                self.assertIn("home/editorial_v37/partials/cms_tail.html", source)
                self.assertIn('id="main-content"', source)
                self.assertIn("v37-detail", source)

    def test_booking_template_preserves_whatsapp_form_contract(self):
        root = Path(__file__).resolve().parents[1] / "home" / "templates" / "home" / "editorial_v37"
        source = (root / "booking.html").read_text(encoding="utf-8")
        for contract in (
            "data-appointment-form",
            'name="name"',
            'name="mobile"',
            'name="clinic"',
            'name="concern"',
            'name="patient_type"',
            'name="date"',
            'name="time"',
            'name="consent"',
            "data-appointment-date",
            "data-form-status",
            "Continue on WhatsApp",
        ):
            with self.subTest(contract=contract):
                self.assertIn(contract, source)

    def test_editorial_homepage_uses_production_routes_and_restored_care_story(self):
        root = Path(__file__).resolve().parents[1] / "home" / "templates" / "home"
        source = (root / "editorial_v37" / "homepage.html").read_text(encoding="utf-8")
        self.assertNotIn("/concept/", source)
        self.assertIn('/treatments/acne-treatment/', source)
        self.assertIn('/dr-cheena-langer/', source)
        self.assertIn('/book-appointment/', source)
        self.assertIn('id="approach"', source)
        self.assertIn('class="process-stage"', source)
        self.assertIn("The treatment should follow the diagnosis.", source)
        self.assertIn("Educational navigation only", source)

    def test_editorial_templates_avoid_prohibited_marketing_claims(self):
        root = Path(__file__).resolve().parents[1] / "home" / "templates" / "home" / "editorial_v37"
        sources = [path.read_text(encoding="utf-8").lower() for path in root.rglob("*.html")]
        combined = "\n".join(sources)
        for prohibited in ("best dermatologist", "no. 1", "number 1", "guaranteed", "100% success"):
            with self.subTest(prohibited=prohibited):
                self.assertNotIn(prohibited, combined)

    def test_specialised_templates_keep_parent_extra_head(self):
        root = Path(__file__).resolve().parents[1] / "home" / "templates" / "home"
        for filename in ("blog_page.html", "doctor_page.html", "clinic_page.html"):
            source = (root / filename).read_text(encoding="utf-8")
            with self.subTest(filename=filename):
                self.assertIn("{{ block.super }}", source)
