from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class BrandParityNormalizationTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(settings.BASE_DIR)

    def read(self, relative_path: str) -> str:
        return (self.root / relative_path).read_text(encoding="utf-8")

    def test_legacy_screenshot_wrapper_normalizes_only_selected_logo_marks(self):
        audit = self.read("tools/audit_browser_parity_brand_normalized.py")

        self.assertIn("audit_browser_parity_hydrated", audit)
        self.assertIn(".brand-mark.brand-mark--image", audit)
        self.assertIn("mark.classList.remove('brand-mark--image')", audit)
        self.assertIn("mark.replaceChildren(document.createTextNode('A'))", audit)
        self.assertNotIn("document.querySelectorAll('img')", audit)

    def test_prelaunch_workflow_uses_brand_normalization_locally_and_deployed(self):
        workflow = self.read(".github/workflows/prelaunch-parity.yml")

        self.assertEqual(
            workflow.count("python tools/audit_browser_parity_brand_normalized.py"),
            2,
        )
        self.assertNotIn(
            "python tools/audit_browser_parity_hydrated.py",
            workflow,
        )
