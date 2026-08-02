from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class ContentRhythmTests(SimpleTestCase):
    def setUp(self):
        template = (
            Path(settings.BASE_DIR)
            / "home"
            / "templates"
            / "home"
            / "partials"
            / "content_rhythm_styles.html"
        )
        self.assertTrue(template.exists())
        self.stylesheet = template.read_text(encoding="utf-8")

    def test_long_bullet_lists_use_balanced_columns(self):
        self.assertIn("columns: 2;", self.stylesheet)
        self.assertIn("column-fill: balance;", self.stylesheet)
        self.assertIn("break-inside: avoid-column;", self.stylesheet)
        self.assertIn("text-wrap: pretty;", self.stylesheet)

    def test_mobile_lists_return_to_one_column(self):
        self.assertIn("@media (max-width: 700px)", self.stylesheet)
        self.assertIn("grid-template-columns: minmax(0, 1fr);", self.stylesheet)

    def test_three_column_cards_are_excluded_from_editorial_columns(self):
        self.assertIn(".clean-list:not(.clean-list--three)", self.stylesheet)

    def test_dark_faq_open_state_has_distinct_surface_and_border(self):
        self.assertIn("details[open]", self.stylesheet)
        self.assertIn("background: #291923 !important;", self.stylesheet)
        self.assertIn("border-color: #a66b83 !important;", self.stylesheet)

    def test_dark_faq_answer_cannot_inherit_legacy_opacity(self):
        self.assertIn("color: #f0e4e9 !important;", self.stylesheet)
        self.assertIn("opacity: 1 !important;", self.stylesheet)
        self.assertIn("background: transparent !important;", self.stylesheet)
