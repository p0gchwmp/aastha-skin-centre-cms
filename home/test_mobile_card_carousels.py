from pathlib import Path

from django.test import SimpleTestCase


class MobileCardCarouselTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.root = Path(__file__).resolve().parents[1]
        cls.base = (
            cls.root / "aastha_cms" / "templates" / "base.html"
        ).read_text(encoding="utf-8")
        partials = (
            cls.root / "home" / "templates" / "home" / "partials"
        )
        cls.css = (partials / "mobile_card_carousel_styles.html").read_text(
            encoding="utf-8"
        )
        cls.script = (partials / "mobile_card_carousel_script.html").read_text(
            encoding="utf-8"
        )

    def test_inline_partials_are_loaded_once_without_extra_requests(self):
        style_partial = "home/partials/mobile_card_carousel_styles.html"
        script_partial = "home/partials/mobile_card_carousel_script.html"
        self.assertEqual(self.base.count(style_partial), 1)
        self.assertEqual(self.base.count(script_partial), 1)
        self.assertNotIn("css/mobile-card-carousels.css", self.base)
        self.assertNotIn("js/mobile-card-carousels.js", self.base)
        self.assertLess(
            self.base.index("css/mobile-layout-qa.css"),
            self.base.index(style_partial),
        )
        self.assertLess(
            self.base.index("js/site-visual-cues.js"),
            self.base.index(script_partial),
        )
        self.assertIn('<style id="mobile-card-carousel-styles">', self.css)
        self.assertIn('<script id="mobile-card-carousel-script">', self.script)

    def test_only_promotional_and_editorial_grids_are_targeted(self):
        for selector in (
            ".concern-grid",
            ".treatment-grid",
            ".why-grid",
            ".journal-grid",
            ".article-grid",
            ".guide-grid",
            ".care-path-grid",
            ".value-grid",
        ):
            self.assertIn(f"'{selector}'", self.script)

        for excluded in (
            ".treatment-directory",
            ".hub-category",
            ".directory-grid",
            ".clinic-choice-grid",
            ".process-grid",
            "[data-no-carousel]",
        ):
            self.assertIn(f"'{excluded}'", self.script)

        self.assertNotIn(".hub-link-grid'", self.script)
        self.assertNotIn(".condition-grid'", self.script)

    def test_carousel_is_mobile_only_progressive_enhancement(self):
        self.assertIn("window.matchMedia('(max-width: 700px)')", self.script)
        self.assertIn("slides.length < 3", self.script)
        self.assertIn("slides.length > 12", self.script)
        self.assertIn("slide.hidden = !selected", self.script)
        self.assertIn("slide.hidden = false", self.script)
        self.assertIn('@media (max-width: 700px)', self.css)
        self.assertIn('[data-mobile-card-carousel="true"] > [hidden]', self.css)

    def test_controls_support_touch_keyboard_and_screen_readers(self):
        self.assertIn("aria-roledescription", self.script)
        self.assertIn("aria-live", self.script)
        self.assertIn("Previous ${this.label} card", self.script)
        self.assertIn("Next ${this.label} card", self.script)
        self.assertIn("event.key === 'ArrowLeft'", self.script)
        self.assertIn("event.key === 'ArrowRight'", self.script)
        self.assertIn("onPointerDown", self.script)
        self.assertIn("onPointerUp", self.script)
        self.assertIn("Swipe or use the arrows", self.script)

    def test_carousel_never_autoplays(self):
        for forbidden in (
            "setInterval(",
            "setTimeout(",
            "autoplay",
            "requestAnimationFrame(",
        ):
            self.assertNotIn(forbidden, self.script)

    def test_dark_mode_and_reduced_motion_are_supported(self):
        self.assertIn('html[data-theme="dark"] .card-carousel-button', self.css)
        self.assertIn("prefers-reduced-motion: reduce", self.css)
        self.assertIn("animation: none", self.css)
