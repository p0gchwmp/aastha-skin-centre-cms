import importlib.util
import sys
import tempfile
from pathlib import Path

from PIL import Image
from django.conf import settings
from django.test import SimpleTestCase


MODULE_PATH = (
    Path(settings.BASE_DIR) / "tools" / "generate_responsive_clinical_images.py"
)
SPEC = importlib.util.spec_from_file_location(
    "generate_responsive_clinical_images",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
responsive_images = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = responsive_images
SPEC.loader.exec_module(responsive_images)


class ResponsiveClinicalImageGenerationTests(SimpleTestCase):
    def test_generates_expected_webp_dimensions_and_smaller_payloads(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "source.webp"
            Image.effect_noise((1200, 900), 64).convert("RGB").save(
                source,
                "WEBP",
                quality=95,
            )
            source_bytes = source.stat().st_size

            records = []
            expected = ((384, 288), (640, 480), (768, 576))
            for width, expected_height in expected:
                destination = root / f"source-{width}w.webp"
                record = responsive_images.generate_variant(
                    source,
                    destination,
                    width,
                )
                records.append(record)

                self.assertTrue(destination.is_file())
                self.assertLess(destination.stat().st_size, source_bytes)
                with Image.open(destination) as generated:
                    self.assertEqual(generated.format, "WEBP")
                    self.assertEqual(generated.size, (width, expected_height))

            self.assertEqual(
                [record["width"] for record in records],
                [384, 640, 768],
            )

    def test_variant_path_preserves_source_and_adds_width_suffix(self):
        source = Path("clinical/acne-scar-treatment-01.webp")
        self.assertEqual(
            responsive_images.variant_asset_path(source, 384),
            Path("clinical/acne-scar-treatment-01-384w.webp"),
        )

    def test_rejects_upscaling_and_invalid_widths(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "small.webp"
            Image.new("RGB", (320, 240), "white").save(source, "WEBP")

            with self.assertRaises(ValueError):
                responsive_images.generate_variant(
                    source,
                    root / "invalid.webp",
                    384,
                )
            with self.assertRaises(ValueError):
                responsive_images.generate_variant(
                    source,
                    root / "zero.webp",
                    0,
                )
