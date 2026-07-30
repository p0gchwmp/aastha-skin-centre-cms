from pathlib import Path

from django.conf import settings
from django.contrib.staticfiles import finders
from django.test import SimpleTestCase


class VisualPolishAssetTests(SimpleTestCase):
    def test_visual_polish_stylesheet_is_discoverable(self):
        asset = finders.find("css/visual-polish.css")

        self.assertIsNotNone(asset)
        self.assertTrue(Path(asset).is_file())

    def test_visual_polish_loads_after_existing_design_layers(self):
        template = (settings.PROJECT_DIR / "templates" / "base.html").read_text(
            encoding="utf-8"
        )

        cms_position = template.index("css/aastha_cms.css")
        polish_position = template.index("css/visual-polish.css")
        self.assertGreater(polish_position, cms_position)

    def test_stylesheet_balances_directory_and_journal_orphans(self):
        asset = Path(finders.find("css/visual-polish.css"))
        stylesheet = asset.read_text(encoding="utf-8")

        self.assertIn(".hub-link:last-child:nth-child(odd)", stylesheet)
        self.assertIn(".journal-card:last-child:nth-child(3n + 1)", stylesheet)
        self.assertIn("grid-auto-rows: 1fr", stylesheet)
        self.assertIn("@media (max-width: 700px)", stylesheet)
