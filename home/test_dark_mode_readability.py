from pathlib import Path

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase


def relative_luminance(hex_colour: str) -> float:
    channels = [int(hex_colour[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    converted = [
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in channels
    ]
    return 0.2126 * converted[0] + 0.7152 * converted[1] + 0.0722 * converted[2]


def contrast_ratio(first: str, second: str) -> float:
    one = relative_luminance(first)
    two = relative_luminance(second)
    return (max(one, two) + 0.05) / (min(one, two) + 0.05)


class DarkModeReadabilityTests(SimpleTestCase):
    def setUp(self):
        asset = finders.find("css/layout-balance.css")
        self.assertIsNotNone(asset)
        self.stylesheet = Path(asset).read_text(encoding="utf-8")

    def test_problem_components_have_final_dark_mode_overrides(self):
        self.assertIn(
            'html[data-theme="dark"] .release-v24 .trust-item span',
            self.stylesheet,
        )
        self.assertIn(
            'html[data-theme="dark"] .release-v24 .faq-answer p',
            self.stylesheet,
        )
        self.assertIn("--dark-readable-muted: #d3c1ca", self.stylesheet)
        self.assertIn("--dark-readable-body: #eadde3", self.stylesheet)

    def test_dark_palette_meets_normal_text_contrast(self):
        background = "#1b1217"
        for foreground in ("#d3c1ca", "#eadde3", "#ef84ac", "#f3a8c3"):
            with self.subTest(foreground=foreground):
                self.assertGreaterEqual(contrast_ratio(foreground, background), 4.5)

    def test_warning_copy_remains_readable(self):
        self.assertGreaterEqual(contrast_ratio("#f3e5ae", "#2b2515"), 4.5)
