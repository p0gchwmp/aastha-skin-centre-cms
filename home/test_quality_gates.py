from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class FrontendQualityGateContractTests(SimpleTestCase):
    def setUp(self):
        self.root = Path(settings.BASE_DIR)

    def read(self, relative_path: str) -> str:
        return (self.root / relative_path).read_text(encoding="utf-8")

    def test_workflow_uses_pinned_tools_and_both_form_factors(self):
        workflow = self.read(".github/workflows/quality-gates.yml")

        self.assertIn("@lhci/cli@0.15.1", workflow)
        self.assertIn("playwright@1.62.0", workflow)
        self.assertIn("@axe-core/playwright@4.12.1", workflow)
        self.assertIn("LHCI_FORM_FACTOR: mobile", workflow)
        self.assertIn("LHCI_FORM_FACTOR: desktop", workflow)
        self.assertIn("tools/audit_accessibility.mjs", workflow)
        self.assertIn("npm --prefix frontend install --no-audit --no-fund", workflow)
        self.assertIn("npm --prefix frontend run build", workflow)
        self.assertIn("home/static/js/editorial-v37*.js", workflow)
        self.assertIn("python manage.py test", workflow)
        self.assertIn("retention-days: 1", workflow)

    def test_workflow_matches_render_asset_build_before_collectstatic(self):
        workflow = self.read(".github/workflows/quality-gates.yml")
        build_visuals = workflow.index("python tools/build_visual_cue_assets.py")
        responsive_clinical = workflow.index(
            "python tools/generate_responsive_clinical_images.py"
        )
        audit_clinical = workflow.index(
            "python tools/audit_clinical_result_images.py"
        )
        verify_snapshots = workflow.index(
            "python tools/verify_exact_page_snapshots.py"
        )
        collectstatic = workflow.index("python manage.py collectstatic --no-input")

        self.assertLess(build_visuals, responsive_clinical)
        self.assertLess(responsive_clinical, audit_clinical)
        self.assertLess(audit_clinical, verify_snapshots)
        self.assertLess(verify_snapshots, collectstatic)
        self.assertIn("DJANGO_SETTINGS_MODULE: aastha_cms.settings.quality", workflow)
        self.assertIn("gunicorn aastha_cms.wsgi:application", workflow)

    def test_production_build_generates_and_audits_frontend_assets(self):
        build = self.read("build.sh")
        responsive_clinical = build.index(
            "python tools/generate_responsive_clinical_images.py"
        )
        audit_clinical = build.index(
            "python tools/audit_clinical_result_images.py"
        )
        frontend_build = build.index("npm --prefix frontend run build")
        js_syntax_gate = build.index("node --check")
        collectstatic = build.index("python manage.py collectstatic --no-input")

        self.assertLess(responsive_clinical, audit_clinical)
        self.assertLess(audit_clinical, collectstatic)
        self.assertLess(frontend_build, collectstatic)
        self.assertLess(js_syntax_gate, collectstatic)

    def test_lighthouse_config_covers_representative_pages_and_strict_targets(self):
        config = self.read("lighthouserc.cjs")

        for route in (
            '"/"',
            '"/book-appointment/"',
            '"/dr-cheena-langer/"',
            '"/locations/karan-nagar/"',
            '"/treatments/acne-scar-treatment/"',
            '"/blog/"',
        ):
            self.assertIn(route, config)

        self.assertIn('"categories:performance": ["error", { minScore: 0.95 }]', config)
        self.assertIn('"categories:accessibility": ["error", { minScore: 1 }]', config)
        self.assertIn('"categories:best-practices": ["error", { minScore: 1 }]', config)
        self.assertIn('"categories:seo": ["error", { minScore: 1 }]', config)
        self.assertIn(
            '"largest-contentful-paint": ["error", { maxNumericValue: 2500 }]',
            config,
        )
        self.assertIn('"uses-responsive-images": "error"', config)
        self.assertIn('"cumulative-layout-shift"', config)
        self.assertIn('"total-blocking-time"', config)

    def test_accessibility_gate_enforces_modern_wcag_aa(self):
        audit = self.read("tools/audit_accessibility.mjs")

        for tag in ("wcag2a", "wcag2aa", "wcag21a", "wcag21aa", "wcag22aa"):
            self.assertIn(f'"{tag}"', audit)

        self.assertIn('"desktop-light"', audit)
        self.assertIn('"mobile-dark"', audit)
        self.assertIn("blockingViolations", audit)
        self.assertNotIn("disableRules", audit)

    def test_clickable_cards_keep_native_anchor_semantics(self):
        script = self.read("home/static/js/professional.js")

        self.assertIn('document.querySelectorAll("[data-card-link]")', script)
        self.assertIn('card.querySelector("a[href]")', script)
        self.assertNotIn('setAttribute("role", "link")', script)
        self.assertNotIn("card.tabIndex", script)

    def test_ga4_is_queued_immediately_but_loaded_after_render(self):
        base = self.read("aastha_cms/templates/base.html")

        self.assertIn('window.gtag("config", measurementId, { send_page_view: true })', base)
        self.assertIn("window.setTimeout(loadAnalytics, 4000)", base)
        self.assertIn('["pointerdown", "touchstart", "keydown"]', base)
        self.assertIn("document.createElement(\"script\")", base)
        self.assertNotIn(
            '<script async src="https://www.googletagmanager.com/gtag/js',
            base,
        )
