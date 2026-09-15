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
        self.assertNotIn("editorial-v37.css", markup)
        self.assertNotIn("editorial-v37.js", markup)
        self.assertNotIn("editorialVersion", markup)

    def test_asset_partial_loads_versioned_skin_when_flag_is_on(self):
        markup = render_to_string(
            "home/partials/editorial_v37_assets.html",
            {"editorial_v37_enabled": True},
        )
        self.assertIn("editorial-v37.css", markup)
        self.assertIn("editorial-v37.js", markup)
        self.assertIn("editorialVersion='37'", markup)
        self.assertIn("Cormorant+Garamond", markup)
        self.assertIn("Manrope", markup)

    def test_editorial_assets_exist_and_are_scoped(self):
        css_path = finders.find("css/editorial-v37.css")
        js_path = finders.find("js/editorial-v37.js")
        self.assertTrue(css_path)
        self.assertTrue(js_path)

        css = Path(css_path).read_text(encoding="utf-8")
        js = Path(js_path).read_text(encoding="utf-8")
        self.assertIn("html.editorial-v37", css)
        self.assertIn('classList.contains("editorial-v37")', js)
        self.assertIn("prefers-reduced-motion", css)
        self.assertIn("clinical-result", css)

    def test_specialised_templates_keep_parent_extra_head(self):
        root = Path(__file__).resolve().parents[1] / "home" / "templates" / "home"
        for filename in ("blog_page.html", "doctor_page.html", "clinic_page.html"):
            source = (root / filename).read_text(encoding="utf-8")
            with self.subTest(filename=filename):
                self.assertIn("{{ block.super }}", source)
