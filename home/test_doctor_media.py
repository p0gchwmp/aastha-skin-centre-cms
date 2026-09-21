from django.test import SimpleTestCase

from home.doctor_media import DOCTOR_MEDIA_RECORDS, doctor_media_markup
from home.exact_editor_setup import inject_doctor_media_section


class DoctorMediaTests(SimpleTestCase):
    def test_media_records_are_unique_https_sources(self):
        self.assertGreaterEqual(len(DOCTOR_MEDIA_RECORDS), 8)
        urls = [item["url"] for item in DOCTOR_MEDIA_RECORDS]
        self.assertEqual(len(urls), len(set(urls)))
        self.assertTrue(all(url.startswith("https://") for url in urls))
        self.assertTrue(
            all(
                item.get("secondary_url", "https://").startswith("https://")
                for item in DOCTOR_MEDIA_RECORDS
            )
        )

    def test_public_markup_links_out_without_republishing_articles(self):
        markup = doctor_media_markup()
        self.assertIn("Professional work, publications &amp; media", markup)
        self.assertIn("View original source", markup)
        self.assertIn('rel="noopener noreferrer"', markup)
        self.assertIn("Emerging role of apremilast in hand dermatoses", markup)
        self.assertIn("Combating Winter Acne Woes", markup)
        self.assertNotIn("<img", markup)

    def test_injector_places_media_before_clinic_section_and_is_idempotent(self):
        source = (
            '<main id="main-content">'
            '<section><h2>Academic and professional background</h2></section>'
            '<section id="clinics"><h2>Choose a clinic in Jammu</h2></section>'
            '</main>'
        )
        updated = inject_doctor_media_section(source, "/dr-cheena-langer/")
        self.assertIn('id="professional-work-media"', updated)
        self.assertLess(
            updated.index('id="professional-work-media"'),
            updated.index('id="clinics"'),
        )
        self.assertEqual(
            inject_doctor_media_section(updated, "/dr-cheena-langer/"),
            updated,
        )

    def test_injector_does_not_touch_other_routes(self):
        source = '<section><h2>Choose a clinic in Jammu</h2></section>'
        self.assertEqual(inject_doctor_media_section(source, "/"), source)
