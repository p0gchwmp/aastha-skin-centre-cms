from decimal import Decimal
from types import SimpleNamespace

from django.test import SimpleTestCase, TestCase

from home.models import ExactPageLayout, HomePage, SiteSettings
from home.templatetags.exact_pages import (
    apply_global_facts,
    normalise_path,
    repair_orphaned_list_items,
)
from wagtail.models import Site


class ExactPageFactTests(SimpleTestCase):
    def test_normalise_path(self):
        self.assertEqual(
            normalise_path("treatments/acne-treatment"),
            "/treatments/acne-treatment/",
        )
        self.assertEqual(
            normalise_path(
                "https://aastha-skin-centre-cms.onrender.com/about/"
            ),
            "/about/",
        )
        self.assertEqual(normalise_path("/"), "/")

    def test_global_facts_update_without_changing_structure_or_claims(self):
        site_settings = SimpleNamespace(
            primary_phone_digits="9123456789",
            secondary_phone_digits="9987654321",
            primary_mobile="9123456789",
            secondary_mobile="9987654321",
            whatsapp_mobile="9000011111",
            email="clinic@example.com",
            currency_symbol="₹",
            consultation_fee=Decimal("700"),
            follow_up_days=14,
        )
        source = (
            '<main id="main-content"><h1>Page</h1>'
            '<a href="https://wa.me/917006613362">WhatsApp</a>'
            '<a href="tel:+917006613362">7006613362</a>'
            '<a href="mailto:aasthaskinsurgs@gmail.com">Email</a>'
            '<p>₹500 · one visit within 10 days</p>'
            '<strong>20+ years</strong>'
            '<span>More than 20 years in medicine</span>'
            "</main>"
        )

        rendered = apply_global_facts(source, site_settings)

        self.assertIn('href="https://wa.me/919000011111"', rendered)
        self.assertIn('href="tel:+919123456789"', rendered)
        self.assertIn(">9123456789</a>", rendered)
        self.assertIn('href="mailto:clinic@example.com"', rendered)
        self.assertIn("₹700 · one visit within 14 days", rendered)
        self.assertIn("<strong>20+ years</strong>", rendered)
        self.assertIn("More than 20 years in medicine", rendered)
        self.assertNotIn("25+ years", rendered)
        self.assertEqual(rendered.count("<main"), 1)
        self.assertEqual(rendered.count("<h1"), 1)

    def test_orphaned_list_paragraphs_become_semantic_bullets(self):
        source = (
            '<section class="article-section">'
            '<ul class="clean-list"><li>Existing item</li></ul>'
            "<p>The patient has a history of keloids</p>"
            "<p>Active acne is still recurring</p>"
            "</section>"
        )

        rendered = repair_orphaned_list_items(source)

        self.assertIn(
            "<li>The patient has a history of keloids</li>",
            rendered,
        )
        self.assertIn("<li>Active acne is still recurring</li>", rendered)
        self.assertNotIn(
            "<p>The patient has a history of keloids</p>",
            rendered,
        )
        self.assertNotIn("<p>Active acne is still recurring</p>", rendered)

    def test_list_repair_leaves_normal_prose_untouched(self):
        source = (
            '<ul class="clean-list"><li>Existing item</li></ul>'
            "<p>This is a complete explanatory sentence.</p>"
        )

        self.assertEqual(repair_orphaned_list_items(source), source)


class ExactPageRenderTests(TestCase):
    def setUp(self):
        self.homepage = HomePage.objects.get(slug="home")
        self.site = Site.objects.get(is_default_site=True)
        self.site.hostname = "testserver"
        self.site.port = 80
        self.site.root_page = self.homepage
        self.site.save(
            update_fields=["hostname", "port", "root_page"],
        )
        SiteSettings.objects.create(
            site=self.site,
            consultation_fee=Decimal("700"),
            follow_up_days=14,
        )

    def test_public_route_uses_exact_layout_and_current_settings(self):
        ExactPageLayout.objects.update_or_create(
            path="/",
            defaults={
                "html": (
                    '<main id="main-content">'
                    "<h1>Exact homepage</h1>"
                    "<p>₹500 · one visit within 10 days</p>"
                    "</main>"
                ),
                "enabled": True,
            },
        )

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "<h1>Exact homepage</h1>", html=True)
        self.assertContains(
            response,
            "<p>₹700 · one visit within 14 days</p>",
            html=True,
        )
        self.assertNotContains(response, "Website editor ready")

    def test_persistent_legacy_layout_gets_runtime_list_repair(self):
        ExactPageLayout.objects.update_or_create(
            path="/",
            defaults={
                "html": (
                    '<main id="main-content">'
                    "<h1>Exact homepage</h1>"
                    '<ul class="clean-list"><li>Existing item</li></ul>'
                    "<p>The patient has a history of keloids</p>"
                    "<p>Active acne is still recurring</p>"
                    "</main>"
                ),
                "enabled": True,
            },
        )

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertContains(
            response,
            "<li>The patient has a history of keloids</li>",
            html=True,
        )
        self.assertContains(
            response,
            "<li>Active acne is still recurring</li>",
            html=True,
        )
        self.assertNotContains(
            response,
            "<p>The patient has a history of keloids</p>",
            html=True,
        )

    def test_disabled_layout_returns_to_wagtail_fallback(self):
        ExactPageLayout.objects.update_or_create(
            path="/",
            defaults={
                "html": (
                    '<main id="main-content">'
                    "<h1>Should not render</h1>"
                    "</main>"
                ),
                "enabled": False,
            },
        )

        response = self.client.get("/")

        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, "Should not render")
        self.assertContains(response, "Website editor ready")
