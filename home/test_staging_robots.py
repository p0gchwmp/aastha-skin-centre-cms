from django.test import TestCase, override_settings
from wagtail.models import Site


class StagingRobotsTests(TestCase):
    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)

    @override_settings(
        DEBUG=False,
        PUBLIC_SITE_URL="https://aastha-skin-centre-cms.onrender.com",
        PUBLIC_SITE_HOST="aastha-skin-centre-cms.onrender.com",
    )
    def test_render_host_stays_noindex_even_if_configured_as_public(self):
        self.site.hostname = "aastha-skin-centre-cms.onrender.com"
        self.site.port = 443
        self.site.save(update_fields=["hostname", "port"])

        response = self.client.get(
            "/",
            HTTP_HOST="aastha-skin-centre-cms.onrender.com",
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")
        self.assertContains(
            response,
            '<meta name="robots" content="noindex,nofollow">',
            html=True,
        )
        self.assertContains(
            response,
            '<link rel="canonical" href="https://aastha-skin-centre-cms.onrender.com/">',
            html=True,
        )

    @override_settings(
        DEBUG=False,
        PUBLIC_SITE_URL="https://www.aasthaskincentre.in",
        PUBLIC_SITE_HOST="www.aasthaskincentre.in",
    )
    def test_final_custom_domain_can_be_indexable(self):
        self.site.hostname = "www.aasthaskincentre.in"
        self.site.port = 443
        self.site.save(update_fields=["hostname", "port"])

        response = self.client.get(
            "/",
            HTTP_HOST="www.aasthaskincentre.in",
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("X-Robots-Tag", response)
        self.assertContains(
            response,
            '<meta name="robots" content="index,follow">',
            html=True,
        )
        self.assertContains(
            response,
            '<link rel="canonical" href="https://www.aasthaskincentre.in/">',
            html=True,
        )

    @override_settings(
        DEBUG=False,
        PUBLIC_SITE_URL="https://www.aasthaskincentre.in",
        PUBLIC_SITE_HOST="www.aasthaskincentre.in",
    )
    def test_render_alias_is_noindex_when_custom_domain_is_public(self):
        response = self.client.get(
            "/",
            HTTP_HOST="aastha-skin-centre-cms.onrender.com",
            secure=True,
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")
        self.assertContains(
            response,
            '<meta name="robots" content="noindex,nofollow">',
            html=True,
        )
        self.assertContains(
            response,
            '<link rel="canonical" href="https://www.aasthaskincentre.in/">',
            html=True,
        )