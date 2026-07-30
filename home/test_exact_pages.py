from decimal import Decimal
from types import SimpleNamespace

from django.test import SimpleTestCase

from home.templatetags.exact_pages import (
    apply_global_facts,
    normalise_path,
)


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

    def test_global_facts_update_without_changing_structure(self):
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
        self.assertIn("<strong>25+ years</strong>", rendered)
        self.assertIn("Over 25 years of clinical excellence", rendered)
        self.assertEqual(rendered.count("<main"), 1)
        self.assertEqual(rendered.count("<h1"), 1)
