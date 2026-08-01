from pathlib import Path

from django.test import SimpleTestCase


class IOSMobileRegressionTests(SimpleTestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.root = Path(__file__).resolve().parents[1]
        cls.mobile_css = (
            cls.root / "aastha_cms" / "static" / "css" / "mobile-layout-qa.css"
        ).read_text(encoding="utf-8")
        cls.visual_css = (
            cls.root / "aastha_cms" / "static" / "css" / "site-visual-cues.css"
        ).read_text(encoding="utf-8")
        cls.audit = (
            cls.root / "tools" / "audit_mobile_layout.py"
        ).read_text(encoding="utf-8")
        cls.workflow = (
            cls.root / ".github" / "workflows" / "mobile-layout-qa.yml"
        ).read_text(encoding="utf-8")

    def test_ios_text_autosizing_is_pinned(self):
        self.assertIn("-webkit-text-size-adjust: 100%", self.mobile_css)
        self.assertIn("text-size-adjust: 100%", self.mobile_css)
        self.assertIn("white-space: normal", self.mobile_css)
        self.assertIn("overflow-wrap: anywhere", self.mobile_css)

    def test_reported_mobile_components_are_width_constrained(self):
        for selector in (
            ".trust-ribbon",
            ".trust-item",
            ".concern-card",
            ".hub-category-grid",
            ".hub-category",
            ".hub-category-heading",
            ".hub-link-grid",
            ".hub-link",
        ):
            self.assertIn(selector, self.mobile_css + self.visual_css)
        self.assertIn("grid-template-columns: 46px minmax(0, 1fr)", self.visual_css)
        self.assertIn("white-space: normal !important", self.visual_css)

    def test_dark_mode_never_filters_the_icon_container(self):
        self.assertIn("filter: none !important", self.visual_css)
        self.assertIn("opacity: 1 !important", self.visual_css)
        self.assertIn("html[data-theme=\"dark\"]", self.visual_css)

    def test_mobile_qa_runs_real_webkit_contract(self):
        self.assertIn('choices=("chromium", "webkit")', self.audit)
        self.assertIn("IOS_USER_AGENT", self.audit)
        self.assertIn("TEXT_CHECKS", self.audit)
        self.assertIn("text crosses viewport", self.audit)
        self.assertIn("clips ${element.scrollWidth - element.clientWidth}px of text", self.audit)
        self.assertIn("has container filter", self.audit)
        self.assertIn("chromium webkit", self.workflow)
        self.assertIn("--engine webkit", self.workflow)
        self.assertIn("--color-scheme dark", self.workflow)
