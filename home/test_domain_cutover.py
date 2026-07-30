from django.test import TestCase, override_settings


PUBLIC_URL = "https://www.aasthaskincentre.in"
PUBLIC_HOST = "www.aasthaskincentre.in"
APEX_HOST = "aasthaskincentre.in"
RENDER_HOST = "aastha-skin-centre-cms.onrender.com"


class CanonicalHostRedirectTests(TestCase):
    @override_settings(
        DEBUG=False,
        PUBLIC_SITE_URL=PUBLIC_URL,
        PUBLIC_SITE_HOST=PUBLIC_HOST,
        CANONICAL_REDIRECT_HOSTS={APEX_HOST},
    )
    def test_approved_alternate_host_redirects_with_path_and_query(self):
        response = self.client.get(
            "/treatments/acne-treatment/?source=old-domain",
            HTTP_HOST=APEX_HOST,
            secure=True,
        )

        self.assertEqual(response.status_code, 308)
        self.assertEqual(
            response["Location"],
            f"{PUBLIC_URL}/treatments/acne-treatment/?source=old-domain",
        )
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")

    @override_settings(
        DEBUG=False,
        PUBLIC_SITE_URL=PUBLIC_URL,
        PUBLIC_SITE_HOST=PUBLIC_HOST,
        CANONICAL_REDIRECT_HOSTS={APEX_HOST},
    )
    def test_redirect_uses_308_to_preserve_post_method(self):
        response = self.client.post(
            "/book-appointment/?source=old-domain",
            {"name": "Website QA"},
            HTTP_HOST=APEX_HOST,
            secure=True,
        )

        self.assertEqual(response.status_code, 308)
        self.assertEqual(
            response["Location"],
            f"{PUBLIC_URL}/book-appointment/?source=old-domain",
        )

    @override_settings(
        DEBUG=False,
        PUBLIC_SITE_URL=PUBLIC_URL,
        PUBLIC_SITE_HOST=PUBLIC_HOST,
        CANONICAL_REDIRECT_HOSTS={PUBLIC_HOST},
    )
    def test_canonical_host_is_never_redirected_to_itself(self):
        response = self.client.get("/", HTTP_HOST=PUBLIC_HOST, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Location", response)
        self.assertNotIn("X-Robots-Tag", response)

    @override_settings(
        DEBUG=False,
        PUBLIC_SITE_URL=PUBLIC_URL,
        PUBLIC_SITE_HOST=PUBLIC_HOST,
        CANONICAL_REDIRECT_HOSTS={RENDER_HOST},
    )
    def test_render_alias_is_never_redirected(self):
        response = self.client.get("/healthz/", HTTP_HOST=RENDER_HOST, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Location", response)
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")

    @override_settings(
        DEBUG=False,
        PUBLIC_SITE_URL=PUBLIC_URL,
        PUBLIC_SITE_HOST=PUBLIC_HOST,
        CANONICAL_REDIRECT_HOSTS=set(),
    )
    def test_redirect_is_disabled_until_hosts_are_explicitly_configured(self):
        response = self.client.get("/", HTTP_HOST=APEX_HOST, secure=True)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Location", response)
        self.assertEqual(response["X-Robots-Tag"], "noindex, nofollow")
