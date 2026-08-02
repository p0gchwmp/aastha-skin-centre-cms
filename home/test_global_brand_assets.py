from __future__ import annotations

from io import BytesIO
from pathlib import Path
import shutil
import tempfile

from django.core.files.base import ContentFile
from django.test import TestCase, override_settings
from PIL import Image as PillowImage
from wagtail.images import get_image_model
from wagtail.models import Site

from home.models import SiteSettings


class GlobalBrandAssetTests(TestCase):
    def setUp(self):
        self.media_root = tempfile.mkdtemp(prefix="aastha-brand-test-")
        self.media_override = override_settings(MEDIA_ROOT=self.media_root)
        self.media_override.enable()
        self.addCleanup(self.media_override.disable)
        self.addCleanup(shutil.rmtree, self.media_root, True)

        self.site = Site.objects.get(is_default_site=True)
        self.site_settings = SiteSettings.for_site(self.site)

    def _image(self, name: str, size=(720, 240)):
        stream = BytesIO()
        PillowImage.new("RGBA", size, (123, 30, 58, 255)).save(
            stream,
            format="PNG",
        )
        stream.seek(0)
        image_model = get_image_model()
        return image_model.objects.create(
            title=name,
            file=ContentFile(stream.read(), name=f"{name}.png"),
        )

    def _homepage(self):
        return self.client.get(
            "/",
            HTTP_HOST=self.site.hostname,
            follow=True,
        )

    def test_selected_logo_exposes_standard_and_high_density_webp_assets(self):
        logo = self._image("updated-clinic-logo")
        self.site_settings.logo = logo
        self.site_settings.save(update_fields=["logo"])

        response = self._homepage()
        standard = logo.get_rendition("max-160x54|format-webp")
        high_density = logo.get_rendition("max-320x108|format-webp")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'data-logo-url="{standard.url}"')
        self.assertContains(response, f'data-logo-width="{standard.width}"')
        self.assertContains(response, f'data-logo-height="{standard.height}"')
        self.assertContains(
            response,
            f'data-logo-large-url="{high_density.url}"',
        )
        self.assertContains(
            response,
            f'data-logo-large-width="{high_density.width}"',
        )
        self.assertContains(
            response,
            f'data-logo-large-height="{high_density.height}"',
        )
        self.assertTrue(standard.url.endswith(".webp"))
        self.assertTrue(high_density.url.endswith(".webp"))
        self.assertLess(standard.width, high_density.width)

    def test_logo_hydrator_builds_truthful_responsive_markup(self):
        script = (
            Path(__file__).resolve().parents[1]
            / "aastha_cms"
            / "static"
            / "js"
            / "aastha_cms.js"
        ).read_text(encoding="utf-8")

        self.assertIn("dataset.logoLargeUrl", script)
        self.assertIn("dataset.logoLargeWidth", script)
        self.assertIn("image.srcset = responsiveCandidates", script)
        self.assertIn('"(max-width: 700px) 105px, 150px"', script)
        self.assertIn('? "150px"', script)
        self.assertIn("image.src = logoUrl", script)

    def test_selected_logo_keeps_footer_geometry_stable(self):
        logo = self._image("stable-footer-logo")
        self.site_settings.logo = logo
        self.site_settings.save(update_fields=["logo"])

        response = self._homepage()
        html = response.content.decode("utf-8")
        footer_rule = html.split(
            ".brand-footer .brand-mark.brand-mark--image {",
            1,
        )[1].split("}", 1)[0]

        self.assertIn("height: 44px;", footer_rule)
        self.assertNotIn("height: 58px;", footer_rule)

    def test_selected_favicon_is_rendered_in_document_head(self):
        favicon = self._image("updated-favicon", size=(128, 128))
        self.site_settings.favicon = favicon
        self.site_settings.save(update_fields=["favicon"])

        response = self._homepage()
        expected = favicon.get_rendition("fill-64x64")

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            f'<link rel="icon" href="{expected.url}" sizes="64x64">',
            html=True,
        )
        self.assertContains(
            response,
            f'<link rel="apple-touch-icon" href="{expected.url}">',
            html=True,
        )

    def test_conventional_favicon_path_redirects_to_selected_asset(self):
        favicon = self._image("browser-favicon", size=(128, 128))
        self.site_settings.favicon = favicon
        self.site_settings.save(update_fields=["favicon"])

        response = self.client.get(
            "/favicon.ico",
            HTTP_HOST=self.site.hostname,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, favicon.file.url)
        self.assertEqual(response["Cache-Control"], "no-cache")

    def test_conventional_favicon_path_is_successful_without_selected_asset(self):
        self.site_settings.favicon = None
        self.site_settings.save(update_fields=["favicon"])

        response = self.client.get(
            "/favicon.ico",
            HTTP_HOST=self.site.hostname,
        )

        self.assertEqual(response.status_code, 204)
        self.assertEqual(response["Cache-Control"], "no-cache")

    def test_empty_logo_keeps_the_existing_placeholder_fallback(self):
        self.site_settings.logo = None
        self.site_settings.save(update_fields=["logo"])

        response = self._homepage()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-logo-url=""')
        self.assertContains(response, 'data-logo-large-url=""')
