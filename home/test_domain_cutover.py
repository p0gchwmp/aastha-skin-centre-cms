from io import StringIO

from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase, override_settings
from wagtail.models import Site


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


class LaunchConfigurationCommandTests(TestCase):
    @override_settings(
        PUBLIC_SITE_URL="",
        PUBLIC_SITE_HOST="",
        CANONICAL_REDIRECT_HOSTS=set(),
    )
    def test_staging_configuration_passes_without_enabling_indexing(self):
        output = StringIO()
        call_command("check_launch_config", stdout=output)

        self.assertIn("Staging configuration is safe", output.getvalue())

    @override_settings(
        PUBLIC_SITE_URL="",
        PUBLIC_SITE_HOST="",
        CANONICAL_REDIRECT_HOSTS={APEX_HOST},
    )
    def test_staging_rejects_active_redirect_hosts(self):
        with self.assertRaisesMessage(
            CommandError,
            "CANONICAL_REDIRECT_HOSTS must remain blank",
        ):
            call_command("check_launch_config")

    @override_settings(
        PUBLIC_SITE_URL=PUBLIC_URL,
        PUBLIC_SITE_HOST=PUBLIC_HOST,
        CANONICAL_REDIRECT_HOSTS={APEX_HOST},
        ALLOWED_HOSTS=[PUBLIC_HOST, APEX_HOST, ".onrender.com"],
        CSRF_TRUSTED_ORIGINS=[PUBLIC_URL, f"https://{APEX_HOST}"],
        WAGTAILADMIN_BASE_URL=PUBLIC_URL,
        SECURE_SSL_REDIRECT=True,
        SESSION_COOKIE_SECURE=True,
        CSRF_COOKIE_SECURE=True,
    )
    def test_complete_public_configuration_passes(self):
        site = Site.objects.get(is_default_site=True)
        site.hostname = PUBLIC_HOST
        site.port = 443
        site.save(update_fields=["hostname", "port"])
        output = StringIO()

        call_command("check_launch_config", "--require-public", stdout=output)

        self.assertIn("Public-domain launch configuration passed", output.getvalue())

    @override_settings(
        PUBLIC_SITE_URL=PUBLIC_URL,
        PUBLIC_SITE_HOST=PUBLIC_HOST,
        CANONICAL_REDIRECT_HOSTS={APEX_HOST},
        ALLOWED_HOSTS=[PUBLIC_HOST, APEX_HOST],
        CSRF_TRUSTED_ORIGINS=[PUBLIC_URL, f"https://{APEX_HOST}"],
        WAGTAILADMIN_BASE_URL="https://wrong.example",
        SECURE_SSL_REDIRECT=True,
        SESSION_COOKIE_SECURE=True,
        CSRF_COOKIE_SECURE=True,
    )
    def test_public_configuration_rejects_wrong_admin_origin(self):
        site = Site.objects.get(is_default_site=True)
        site.hostname = PUBLIC_HOST
        site.port = 443
        site.save(update_fields=["hostname", "port"])

        with self.assertRaisesMessage(
            CommandError,
            "WAGTAILADMIN_BASE_URL must equal PUBLIC_SITE_URL",
        ):
            call_command("check_launch_config", "--require-public")
