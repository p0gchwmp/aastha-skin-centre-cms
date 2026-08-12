from pathlib import Path
import subprocess
import sys

from django.test import SimpleTestCase
from PIL import Image


class CuratedVisualCueTests(SimpleTestCase):
    CUES = {
        "growths": "moles-growths-nails",
        "scars": "scars-texture-skin-quality",
        "children": "childrens-dermatology",
        "dermatosurgery": "minor-dermatosurgery",
    }
    SIZES = (128, 256, 512)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.root = Path(__file__).resolve().parents[1]
        cls.sources = cls.root / "home" / "static_src" / "visual-cues" / "approved-2026"
        cls.outputs = cls.root / "home" / "static" / "images" / "visual-cues"
        cls.generator = cls.root / "tools" / "build_visual_cue_assets.py"
        subprocess.run(
            [sys.executable, str(cls.generator)],
            cwd=cls.root,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_build_uses_one_approved_generator(self):
        build = (self.root / "build.sh").read_text(encoding="utf-8")
        generator = "python tools/build_visual_cue_assets.py"
        self.assertIn(generator, build)

        compatibility = (
            self.root / "tools" / "install_curated_visual_cue_assets.py"
        ).read_text(encoding="utf-8")
        self.assertIn("Compatibility no-op", compatibility)
        self.assertNotIn("CURATED_CUES", compatibility)

    def test_specialists_are_generated_from_high_resolution_sources(self):
        generator = self.generator.read_text(encoding="utf-8")
        for slug in self.CUES.values():
            self.assertIn(f'"{slug}"', generator)

    def test_curated_sources_and_responsive_outputs_are_transparent(self):
        generator_source = self.generator.read_text(encoding="utf-8")
        self.assertIn("_remove_connected_white_canvas", generator_source)
        self.assertIn("Image.Resampling.LANCZOS", generator_source)

        for cue, slug in self.CUES.items():
            for size in self.SIZES:
                with self.subTest(cue=cue, size=size):
                    output = self.outputs / f"{slug}-{size}.webp"
                    self.assertTrue(output.is_file())
                    with Image.open(output) as image:
                        self.assertEqual(image.size, (size, size))
                        self.assertIn("A", image.getbands())
                        alpha = image.getchannel("A")
                        self.assertEqual(alpha.getextrema(), (0, 255))
                        self.assertEqual(alpha.getpixel((0, 0)), 0)
