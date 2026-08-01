import importlib.util
import sys
from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


MODULE_PATH = (
    Path(settings.BASE_DIR) / "tools" / "audit_google_measurement_readiness.py"
)
SPEC = importlib.util.spec_from_file_location(
    "audit_google_measurement_readiness",
    MODULE_PATH,
)
assert SPEC and SPEC.loader
measurement_audit = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = measurement_audit
SPEC.loader.exec_module(measurement_audit)


BASE = "https://www.aasthaskincentre.in"


def results_by_name(checks):
    return {item.name: item for item in checks}


class GoogleMeasurementReadinessTests(SimpleTestCase):
    def valid_homepage(self):
        return f"""
        <!doctype html>
        <html>
          <head>
            <link rel="canonical" href="{BASE}/">
            <meta name="google-site-verification" content="abcDEF_123456">
          </head>
          <body data-analytics-enabled="true">
            <script src="/static/js/analytics-events.abc123.js" defer></script>
            <script>
              const measurementId = "G\\u002DABC1234567";
              const script = document.createElement("script");
              script.src = `https://www.googletagmanager.com/gtag/js?id=${{measurementId}}`;
              window.setTimeout(loadAnalytics, 4000);
            </script>
          </body>
        </html>
        """

    def test_canonical_homepage_exposes_required_google_signals(self):
        checks, bundle_url = measurement_audit.inspect_homepage(
            self.valid_homepage(),
            BASE,
        )

        self.assertTrue(all(item.passed for item in checks), checks)
        self.assertEqual(
            bundle_url,
            f"{BASE}/static/js/analytics-events.abc123.js",
        )

    def test_django_escapejs_measurement_id_is_decoded(self):
        ids, configured = measurement_audit.extract_measurement_ids(
            'const measurementId = "G\\u002DG5DQPDJ53P";'
        )

        self.assertEqual(ids, ["G-G5DQPDJ53P"])
        self.assertEqual(configured, ["G-G5DQPDJ53P"])

    def test_homepage_rejects_missing_token_and_eager_gtag(self):
        source = self.valid_homepage().replace(
            '<meta name="google-site-verification" content="abcDEF_123456">',
            "",
        ).replace(
            '<script src="/static/js/analytics-events.abc123.js" defer></script>',
            '<script src="https://www.googletagmanager.com/gtag/js?id=G-ABC1234567"></script>'
            '<script src="/static/js/analytics-events.abc123.js" defer></script>',
        )

        checks, _ = measurement_audit.inspect_homepage(source, BASE)
        results = results_by_name(checks)

        self.assertFalse(results["search_console_html_token"].passed)
        self.assertFalse(results["ga4_deferred_loader"].passed)

    def test_generate_lead_bundle_uses_only_non_patient_parameters(self):
        source = """
        document.addEventListener("aastha:appointment-request-opened", event => {
          const detail = event.detail || {};
          track("generate_lead", {
            lead_source: "appointment_form",
            clinic_branch: normaliseBranch(detail.clinic),
            has_preferred_date: Boolean(detail.hasPreferredDate),
            has_preferred_time: Boolean(detail.hasPreferredTime)
          });
        });
        """

        checks = measurement_audit.inspect_analytics_bundle(source)
        self.assertTrue(all(item.passed for item in checks), checks)

    def test_generate_lead_bundle_rejects_patient_fields(self):
        source = """
        const mobile = document.querySelector('[name="mobile"]');
        track("generate_lead", {
          lead_source: "appointment_form",
          clinic_branch: "karan_nagar",
          has_preferred_date: true,
          has_preferred_time: false,
          mobile_number: mobile.value
        });
        """

        checks = results_by_name(
            measurement_audit.inspect_analytics_bundle(source)
        )
        self.assertFalse(checks["generate_lead_parameter_allowlist"].passed)
        self.assertFalse(checks["analytics_bundle_excludes_patient_fields"].passed)

    def test_sitemap_and_robots_use_canonical_origin(self):
        sitemap = f"""<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <url><loc>{BASE}/</loc></url>
          <url><loc>{BASE}/book-appointment/</loc></url>
        </urlset>
        """.encode()
        robots = f"""User-agent: *
        Allow: /
        Sitemap: {BASE}/sitemap.xml
        """

        sitemap_checks = measurement_audit.inspect_sitemap(sitemap, BASE)
        robots_checks = measurement_audit.inspect_robots(robots, BASE)

        self.assertTrue(all(item.passed for item in sitemap_checks))
        self.assertTrue(all(item.passed for item in robots_checks))

    def test_noncanonical_sitemap_url_is_rejected(self):
        sitemap = b"""<?xml version="1.0" encoding="UTF-8"?>
        <urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
          <url><loc>https://aastha-skin-centre-cms.onrender.com/</loc></url>
        </urlset>
        """

        checks = results_by_name(
            measurement_audit.inspect_sitemap(sitemap, BASE)
        )
        self.assertFalse(checks["sitemap_uses_canonical_origin"].passed)

    def test_base_must_be_a_bare_https_origin(self):
        with self.assertRaises(ValueError):
            measurement_audit.canonical_origin("http://example.com")
        with self.assertRaises(ValueError):
            measurement_audit.canonical_origin(
                "https://www.aasthaskincentre.in/path"
            )
