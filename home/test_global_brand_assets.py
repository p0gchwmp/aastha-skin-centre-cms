from __future__ import annotations

from io import BytesIO
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

    def test_selected_logo_is_exposed_as_an_optimized_public_asset(self):
        logo = self._image("updated-clinic-logo")
        self.site_settings.logo = logo
        self.site_settings.save(update_fields=["logo"])

        response = self._homepage()
        expected = logo.get_rendition("max-480x160")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, f'data-logo-url="{expected.url}"')
        self.assertContains(response, f'data-logo-width="{expected.width}"')
        self.assertContains(response, f'data-logo-height="{expected.height}"')

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

    def test_empty_logo_keeps_the_existing_placeholder_fallback(self):
        self.site_settings.logo = None
        self.site_settings.save(update_fields=["logo"])

        response = self._homepage()

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'data-logo-url=""')
