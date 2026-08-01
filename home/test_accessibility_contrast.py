from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AccessibilityContrastContractTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(settings.BASE_DIR)

    def read(self, relative_path: str) -> str:
        return (self.root / relative_path).read_text(encoding="utf-8")

    @staticmethod
    def contrast_ratio(foreground: str, background: str) -> float:
        def luminance(value: str) -> float:
            channels = [
                int(value[index : index + 2], 16) / 255
                for index in (1, 3, 5)
            ]
            linear = [
                channel / 12.92
                if channel <= 0.04045
                else ((channel + 0.055) / 1.055) ** 2.4
                for channel in channels
            ]
            return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]

        first, second = sorted(
            (luminance(foreground), luminance(background)), reverse=True
        )
        return (first + 0.05) / (second + 0.05)

    def test_contrast_layer_loads_after_visual_styles_without_new_request(self):
        base = self.read("aastha_cms/templates/base.html")
        visual_css = "{% static 'css/site-visual-cues.css' %}"
        contrast_include = (
            '{% include "home/partials/accessibility_contrast_styles.html" %}'
        )

        self.assertIn(contrast_include, base)
        self.assertLess(base.index(visual_css), base.index(contrast_include))
        self.assertNotIn("accessibility-contrast.css", base)

    def test_reported_selectors_have_accessible_overrides(self):
        styles = self.read(
            "home/templates/home/partials/accessibility_contrast_styles.html"
        )

        for selector in (
            ".why-number",
            ".value-card > span",
            ".section-kicker",
            ".quiet-label",
            ".contact-number",
            ".clinical-results__hero-label",
            ".treatment-card .text-link",
            ".mobile-actions",
        ):
            self.assertIn(selector, styles)

    def test_accent_palette_meets_w3c_contrast_math(self):
        self.assertGreaterEqual(self.contrast_ratio("#856600", "#ffffff"), 3.0)
        self.assertGreaterEqual(self.contrast_ratio("#e8c978", "#0f0b0d"), 4.5)
        self.assertGreaterEqual(self.contrast_ratio("#e8c978", "#1b1217"), 4.5)
        self.assertGreaterEqual(self.contrast_ratio("#f2a8c0", "#1b1519"), 4.5)
        self.assertGreaterEqual(self.contrast_ratio("#f2a8c0", "#21191c"), 4.5)
        self.assertGreaterEqual(self.contrast_ratio("#ffffff", "#9a1f49"), 4.5)
