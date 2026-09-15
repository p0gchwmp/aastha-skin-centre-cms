from __future__ import annotations

import os
from pathlib import Path
from unittest.mock import patch

from django.contrib.staticfiles import finders
from django.template.loader import render_to_string
from django.test import SimpleTestCase

from home.context_processors import _env_flag


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
        # Production static storage fingerprints filenames, e.g.
        # editorial-v37.<hash>.css, so assert the logical stem + extension.
        self.assertRegex(markup, r"editorial-v37(?:\.[0-9a-f]+)?\.css")
        self.assertRegex(markup, r"editorial-v37-home(?:\.[0-9a-f]+)?\.css")
        self.assertRegex(markup, r"editorial-v37(?:\.[0-9a-f]+)?\.js")
        self.assertRegex(markup, r"editorial-v37-home(?:\.[0-9a-f]+)?\.js")
        self.assertIn("editorialVersion='37'", markup)
        self.assertIn("Cormorant+Garamond", markup)
        self.assertIn("Manrope", markup)

    def test_editorial_assets_exist_and_are_scoped(self):
        assets = {
            "css/editorial-v37.css": "html.editorial-v37",
            "css/editorial-v37-home.css": "html.editorial-v37",
            "js/editorial-v37.js": 'classList.contains("editorial-v37")',
            "js/editorial-v37-home.js": 'classList.contains("editorial-v37")',
        }
        for path, scope in assets.items():
            with self.subTest(path=path):
                file_path = finders.find(path)
                self.assertTrue(file_path)
                source = Path(file_path).read_text(encoding="utf-8")
                self.assertIn(scope, source)

        css = Path(finders.find("css/editorial-v37.css")).read_text(encoding="utf-8")
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn("clinical-result", css)

    def test_homepage_switch_preserves_legacy_renderer_as_rollback(self):
        root = Path(__file__).resolve().parents[1] / "home" / "templates" / "home"
        source = (root / "home_page.html").read_text(encoding="utf-8")
        self.assertIn("{% if editorial_v37_enabled %}", source)
        self.assertIn('home/editorial_v37/homepage.html', source)
        self.assertIn("{% exact_page_main as exact_main %}", source)
        self.assertIn("premium-minimal-preview.js", source)
        self.assertIn("{% if not editorial_v37_enabled %}", source)

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

    def test_editorial_homepage_avoids_prohibited_marketing_claims(self):
        root = Path(__file__).resolve().parents[1] / "home" / "templates" / "home"
        source = (root / "editorial_v37" / "homepage.html").read_text(encoding="utf-8").lower()
        for prohibited in ("best dermatologist", "no. 1", "number 1", "guaranteed", "100% success"):
            with self.subTest(prohibited=prohibited):
                self.assertNotIn(prohibited, source)

    def test_specialised_templates_keep_parent_extra_head(self):
        root = Path(__file__).resolve().parents[1] / "home" / "templates" / "home"
        for filename in ("blog_page.html", "doctor_page.html", "clinic_page.html"):
            source = (root / filename).read_text(encoding="utf-8")
            with self.subTest(filename=filename):
                self.assertIn("{{ block.super }}", source)
