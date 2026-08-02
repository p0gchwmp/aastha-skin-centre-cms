from pathlib import Path
import subprocess
import sys

from django.contrib.staticfiles import finders
from django.test import SimpleTestCase
from PIL import Image


class SiteVisualCueTests(SimpleTestCase):
    ASSETS = {
        "acne": "acne-care",
        "pigmentation": "pigmentation-care",
        "hair": "hair-scalp-care",
        "diagnosis": "dermatologist-diagnosis",
        "experience": "medical-experience",
        "locations": "two-clinic-locations",
        "complete": "complete-care",
        "plan": "personalised-plan",
        "laser": "advanced-laser-care",
        "clinical": "clinical-skin-care",
        "allergy": "allergy-inflammatory-rashes",
        "growths": "moles-growths-nails",
        "scars": "scars-texture-skin-quality",
        "children": "childrens-dermatology",
        "dermatosurgery": "minor-dermatosurgery",
        "ageing": "skin-quality-ageing",
        "infection": "fungal-infection-care",
    }
    SIZES = (64, 128, 256, 512)

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.root = Path(__file__).resolve().parents[1]
        for script in (
            "build_visual_cue_assets.py",
            "install_curated_visual_cue_assets.py",
        ):
            subprocess.run(
                [sys.executable, str(cls.root / "tools" / script)],
                cwd=cls.root,
                check=True,
                capture_output=True,
                text=True,
            )

    def setUp(self):
        css_path = finders.find("css/site-visual-cues.css")
        js_path = finders.find("js/site-visual-cues.js")
        self.assertIsNotNone(css_path)
        self.assertIsNotNone(js_path)
        self.stylesheet = Path(css_path).read_text(encoding="utf-8")
        self.script = Path(js_path).read_text(encoding="utf-8")

        self.base_template = (
            self.root / "aastha_cms" / "templates" / "base.html"
        ).read_text(encoding="utf-8")
        self.asset_manifest = (
            self.root
            / "home"
            / "templates"
            / "home"
            / "partials"
            / "pastel_clay_sprite.html"
        ).read_text(encoding="utf-8")
        self.generator = (
            self.root / "tools" / "build_visual_cue_assets.py"
        ).read_text(encoding="utf-8")
        self.installer = (
            self.root / "tools" / "install_curated_visual_cue_assets.py"
        ).read_text(encoding="utf-8")
        self.dark_mode_audit = (
            self.root / "tools" / "audit_dark_mode_readability.py"
        ).read_text(encoding="utf-8")

    def test_global_template_loads_one_visual_system(self):
        self.assertEqual(
            self.base_template.count("css/site-visual-cues.css"),
            1,
        )
        self.assertEqual(
            self.base_template.count("js/site-visual-cues.js"),
            1,
        )
        self.assertIn(
            "home/partials/pastel_clay_sprite.html",
            self.base_template,
        )
        self.assertIn('id="visual-cue-assets"', self.asset_manifest)
        self.assertNotIn("<svg", self.asset_manifest)
        self.assertLess(
            self.base_template.index("css/mobile-layout-qa.css"),
            self.base_template.index("css/site-visual-cues.css"),
        )

    def test_build_restores_original_core_then_installs_curated_specialists(self):
        self.assertIn("SOURCE_DIR", self.generator)
        self.assertIn("STANDALONE_SOURCES", self.generator)
        self.assertIn("SPRITE_SOURCES", self.generator)
        self.assertIn("group-a-128.webp", self.generator)
        self.assertIn("group-b-128.webp", self.generator)
        self.assertIn("Image.Resampling.LANCZOS", self.generator)
        self.assertIn("lossless=True", self.generator)
        self.assertNotIn("ImageDraw", self.generator)
        self.assertNotIn("ImageFilter", self.generator)

        self.assertIn("CURATED_CUES", self.installer)
        curated_block = self.installer.split("CURATED_CUES = {", 1)[1].split(
            "}", 1
        )[0]
        self.assertNotIn('"hair"', curated_block)

        for cue, slug in self.ASSETS.items():
            for size in self.SIZES:
                with self.subTest(cue=cue, size=size):
                    relative = f"images/visual-cues/{slug}-{size}.webp"
                    asset_path = finders.find(relative)
                    self.assertIsNotNone(asset_path)
                    with Image.open(asset_path) as image:
                        self.assertEqual(image.format, "WEBP")
                        self.assertEqual(image.size, (size, size))
                        self.assertIn("A", image.getbands())
                        alpha = image.getchannel("A")
                        self.assertEqual(alpha.getextrema(), (0, 255))
                        self.assertEqual(alpha.getpixel((0, 0)), 0)
                        transparent = sum(pixel == 0 for pixel in alpha.getdata())
                        self.assertGreater(transparent, size * size * 0.20)
                    self.assertIn(relative, self.asset_manifest)

    def test_original_approved_core_asset_names_are_preserved(self):
        for slug in (
            "clinical-skin-care",
            "hair-scalp-care",
            "dermatologist-diagnosis",
            "medical-experience",
            "two-clinic-locations",
            "complete-care",
            "personalised-plan",
        ):
            self.assertIn(slug, self.generator)

    def test_script_uses_responsive_images_and_fallbacks(self):
        self.assertIn("message-visual__img", self.script)
        self.assertIn("image.srcset", self.script)
        self.assertIn("64w", self.script)
        self.assertIn("128w", self.script)
        self.assertIn("256w", self.script)
        self.assertIn("512w", self.script)
        self.assertIn("image.sizes", self.script)
        self.assertIn("image.loading = 'lazy'", self.script)
        self.assertNotIn("image.loading = 'eager'", self.script)
        self.assertIn("decoding = 'async'", self.script)
        self.assertIn("element.replaceChildren(image)", self.script)
        self.assertIn("restoreOriginal(element)", self.script)
        self.assertNotIn("createElementNS", self.script)
        self.assertNotIn("message-visual__svg", self.script)

    def test_existing_placeholders_only_are_upgraded(self):
        self.assertIn("const PLACEHOLDER_SELECTOR", self.script)
        self.assertIn("'.hub-icon'", self.script)
        self.assertIn(
            "document.querySelectorAll(PLACEHOLDER_SELECTOR)",
            self.script,
        )
        self.assertNotIn("createElement('span')", self.script)
        self.assertNotIn("insertBefore", self.script)
        self.assertNotIn("visual-cue-card--managed", self.script)
        self.assertNotIn("hub-category-heading--clay", self.script)

    def test_requested_headings_have_distinct_cues(self):
        expected = {
            "itching allergy and inflammatory rashes": "allergy",
            "moles growths nails and minor procedures": "growths",
            "scars texture and skin quality": "scars",
            "childrens dermatology": "children",
            "minor procedures and dermato surgery": "dermatosurgery",
            "skin quality and ageing": "ageing",
            "fungal and recurrent infections": "infection",
            "acne pimples and scars": "acne",
            "pigmentation and uneven tone": "pigmentation",
            "hair fall and scalp concerns": "hair",
        }
        for label, cue in expected.items():
            with self.subTest(label=label, cue=cue):
                self.assertIn(
                    f"['{label}', '{cue}']",
                    self.script,
                )

    def test_category_meaning_comes_from_nearest_heading(self):
        self.assertIn("const headingLabel", self.script)
        self.assertIn(".hub-category-heading", self.script)
        self.assertIn("'h1, h2, h3, h4, strong'", self.script)
        self.assertNotIn("context.textContent", self.script)

    def test_homepage_credential_icons_keep_explicit_order(self):
        for cue in (
            "diagnosis",
            "experience",
            "locations",
            "complete",
            "plan",
        ):
            self.assertIn(f"'{cue}'", self.script)
        self.assertIn(".trust-item .trust-icon", self.script)

    def test_css_removes_forced_tile_treatment(self):
        self.assertIn(
            "background: transparent !important",
            self.stylesheet,
        )
        self.assertIn("border: 0 !important", self.stylesheet)
        self.assertIn("box-shadow: none !important", self.stylesheet)
        self.assertIn(
            'html[data-theme="dark"] .release-v24 .message-visual',
            self.stylesheet,
        )
        self.assertNotIn("brightness(.92)", self.stylesheet)
        self.assertNotIn("saturate(.92)", self.stylesheet)

    def test_mobile_credential_ribbon_is_compact_and_left_aligned(self):
        self.assertIn(
            "grid-template-columns: 48px minmax(0, 1fr)",
            self.stylesheet,
        )
        self.assertIn("grid-row: 1 / span 2", self.stylesheet)
        self.assertIn("height: auto", self.stylesheet)
        self.assertIn("text-align: left", self.stylesheet)
        self.assertIn("padding: 15px 17px", self.stylesheet)

    def test_dark_mode_audit_validates_decorative_images_not_text_contrast(self):
        self.assertIn("DECORATIVE_ICON_CHECKS", self.dark_mode_audit)
        self.assertIn(
            '".trust-ribbon .trust-icon.message-visual"',
            self.dark_mode_audit,
        )
        self.assertIn('"aria-hidden"', self.dark_mode_audit)
        self.assertIn('"presentation role"', self.dark_mode_audit)
        self.assertIn('"transparent background"', self.dark_mode_audit)
        self.assertIn('"image loaded"', self.dark_mode_audit)
        self.assertNotIn(
            '("/", ".trust-ribbon .trust-icon", 4.5)',
            self.dark_mode_audit,
        )

    def test_visual_css_keeps_slot_sizes_without_card_reflow(self):
        for size in ("54px", "42px", "46px"):
            self.assertIn(size, self.stylesheet)
        self.assertIn(".hub-icon.message-visual", self.stylesheet)
        self.assertIn(".icon-bubble.message-visual", self.stylesheet)
        self.assertIn(".trust-icon.message-visual", self.stylesheet)

        for forbidden in (
            "grid-auto-rows",
            "height: 100% !important",
            "margin-top: auto !important",
            ".clinic-location-grid",
            ".location-contact-grid",
            ".clinic-choice-grid",
            "grid-template-columns: 96px",
        ):
            self.assertNotIn(forbidden, self.stylesheet)

    def test_reduced_motion_preserves_artwork(self):
        self.assertIn("prefers-reduced-motion", self.stylesheet)
