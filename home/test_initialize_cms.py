from django.test import TestCase
from wagtail.models import Site

from home.management.commands.initialize_cms import (
    APPROVED_ANALYTICS_ID,
    APPROVED_FACEBOOK_URL,
    APPROVED_SEARCH_CONSOLE_VERIFICATION,
    sync_approved_site_settings,
)
from home.models import SiteSettings


class ApprovedSiteSettingsTests(TestCase):
    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        SiteSettings.objects.filter(site=self.site).delete()

    def test_blank_approved_settings_are_upgraded(self):
        site_settings = SiteSettings.objects.create(
            site=self.site,
            facebook_url="",
            analytics_id="",
            search_console_verification="",
        )

        changed = sync_approved_site_settings(self.site)

        self.assertTrue(changed)
        site_settings.refresh_from_db()
        self.assertEqual(site_settings.facebook_url, APPROVED_FACEBOOK_URL)
        self.assertEqual(site_settings.analytics_id, APPROVED_ANALYTICS_ID)
        self.assertEqual(
            site_settings.search_console_verification,
            APPROVED_SEARCH_CONSOLE_VERIFICATION,
        )

    def test_generic_facebook_homepage_is_upgraded(self):
        site_settings = SiteSettings.objects.create(
            site=self.site,
            facebook_url="https://www.facebook.com/",
        )

        changed = sync_approved_site_settings(self.site)

        self.assertTrue(changed)
        site_settings.refresh_from_db()
        self.assertEqual(site_settings.facebook_url, APPROVED_FACEBOOK_URL)

    def test_explicit_future_settings_are_preserved(self):
        future_url = "https://www.facebook.com/future-clinic-page/"
        future_analytics_id = "G-FUTURE1234"
        future_verification = "future-verification-token"
        site_settings = SiteSettings.objects.create(
            site=self.site,
            facebook_url=future_url,
            analytics_id=future_analytics_id,
            search_console_verification=future_verification,
        )

        changed = sync_approved_site_settings(self.site)

        self.assertFalse(changed)
        site_settings.refresh_from_db()
        self.assertEqual(site_settings.facebook_url, future_url)
        self.assertEqual(site_settings.analytics_id, future_analytics_id)
        self.assertEqual(
            site_settings.search_console_verification,
            future_verification,
        )

    def test_blank_measurement_fields_are_filled_with_explicit_facebook(self):
        future_url = "https://www.facebook.com/future-clinic-page/"
        site_settings = SiteSettings.objects.create(
            site=self.site,
            facebook_url=future_url,
            analytics_id="",
            search_console_verification="",
        )

        changed = sync_approved_site_settings(self.site)

        self.assertTrue(changed)
        site_settings.refresh_from_db()
        self.assertEqual(site_settings.facebook_url, future_url)
        self.assertEqual(site_settings.analytics_id, APPROVED_ANALYTICS_ID)
        self.assertEqual(
            site_settings.search_console_verification,
            APPROVED_SEARCH_CONSOLE_VERIFICATION,
        )
