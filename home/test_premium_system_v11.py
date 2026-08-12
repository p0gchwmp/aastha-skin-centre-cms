from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class PremiumSystemV11ContractTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(settings.BASE_DIR)

    def read(self, relative_path: str) -> str:
        return (self.root / relative_path).read_text(encoding="utf-8")

    def test_global_template_loads_v11_after_previous_systems(self):
        base = self.read("aastha_cms/templates/base.html")

        self.assertLess(
            base.index("premium-system-v10.css"),
            base.index("premium-system-v11.css"),
        )
        self.assertIn("premium-system-v11.js", base)

    def test_article_toc_collects_second_and_third_level_headings(self):
        script = self.read("home/static/js/premium-system-v8.js")

        self.assertIn('.article-section > :is(h2, h3)', script)

    def test_v11_restores_comparison_and_question_alignment(self):
        script = self.read("home/static/js/premium-system-v11.js")
        styles = self.read("home/static/css/premium-system-v11.css")

        self.assertIn("clinical-before-after__range", script)
        self.assertIn("Compare before and after clinical photograph", script)
        self.assertIn('node.nodeValue.replace(/\\s*\\?/g, "\\u202f?")', script)
        self.assertIn("grid-template-columns: minmax(0, 1fr) 30px", styles)
        self.assertIn("clip-path: inset(0 calc(100% - var(--clinical-compare))", styles)

    def test_responsive_and_architectural_overrides_are_explicit(self):
        styles = self.read("home/static/css/premium-system-v11.css")

        self.assertIn("@media (min-width: 761px) and (max-width: 1100px)", styles)
        self.assertIn("grid-template-columns: minmax(0, 1fr) !important", styles)
        self.assertIn("--v11-edge: 2px", styles)
