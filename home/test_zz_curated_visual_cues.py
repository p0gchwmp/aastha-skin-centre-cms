from pathlib import Path
import subprocess
import sys

from django.test import SimpleTestCase
from PIL import Image


class CuratedVisualCueTests(SimpleTestCase):
    CUES = {
        "acne": "acne-care",
        "pigmentation": "pigmentation-care",
        "hair": "hair-scalp-care",
        "infection": "fungal-infection-care",
        "allergy": "allergy-inflammatory-rashes",
        "growths": "moles-growths-nails",
        "scars": "scars-texture-skin-quality",
        "children": "childrens-dermatology",
        "dermatosurgery": "minor-dermatosurgery",
        "ageing": "skin-quality-ageing",
    }
    SIZES = (128, 256, 512)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.root = Path(__file__).resolve().parents[1]
        cls.sources = (
            cls.root / "home" / "static" / "images" / "visual-cue-sources"
        )
        cls.outputs = cls.root / "home" / "static" / "images" / "visual-cues"
        cls.installer = (
            cls.root / "tools" / "install_curated_visual_cue_assets.py"
        )
        subprocess.run(
            [sys.executable, str(cls.installer)],
            cwd=cls.root,
            check=True,
            capture_output=True,
            text=True,
        )

    def test_build_runs_curated_pass_after_fallback_generator(self):
        build = (self.root / "build.sh").read_text(encoding="utf-8")
        generator = "python tools/build_visual_cue_assets.py"
        installer = "python tools/install_curated_visual_cue_assets.py"
        self.assertIn(generator, build)
        self.assertIn(installer, build)
        self.assertLess(build.index(generator), build.index(installer))

    def test_curated_sources_and_responsive_outputs_are_transparent(self):
        installer_source = self.installer.read_text(encoding="utf-8")
        self.assertIn("CURATED_CUES", installer_source)
        self.assertIn("Image.Resampling.LANCZOS", installer_source)
        self.assertIn("lossless=True", installer_source)

        for cue, slug in self.CUES.items():
            with self.subTest(cue=cue, kind="source"):
                source = self.sources / f"{cue}.webp"
                self.assertTrue(source.is_file())
                with Image.open(source) as image:
                    self.assertEqual(image.format, "WEBP")
                    self.assertIn("A", image.getbands())
                    alpha = image.getchannel("A")
                    self.assertEqual(alpha.getextrema(), (0, 255))
                    self.assertEqual(alpha.getpixel((0, 0)), 0)

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
