from django.test import TestCase
from wagtail.models import Site

from home.management.commands.initialize_cms import (
    APPROVED_ANALYTICS_ID,
    APPROVED_FACEBOOK_URL,
    APPROVED_HOMEPAGE_META_DESCRIPTION,
    APPROVED_HOMEPAGE_SEO_TITLE,
    APPROVED_SEARCH_CONSOLE_VERIFICATION,
    sync_approved_homepage_seo,
    sync_approved_site_settings,
)
from home.models import HomePage, SiteSettings


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


class ApprovedHomepageSeoTests(TestCase):
    def setUp(self):
        self.home = HomePage.objects.first()
        self.assertIsNotNone(self.home)

    def test_blank_homepage_metadata_is_filled(self):
        self.home.seo_title = ""
        self.home.search_description = ""
        self.home.save(update_fields=["seo_title", "search_description"])

        changed = sync_approved_homepage_seo(self.home)

        self.assertEqual(set(changed), {"seo_title", "search_description"})
        self.home.refresh_from_db()
        self.assertEqual(self.home.seo_title, APPROVED_HOMEPAGE_SEO_TITLE)
        self.assertEqual(
            self.home.search_description,
            APPROVED_HOMEPAGE_META_DESCRIPTION,
        )

    def test_editor_authored_homepage_metadata_is_preserved(self):
        self.home.seo_title = "Custom homepage SEO title"
        self.home.search_description = "Custom editor-authored homepage description."
        self.home.save(update_fields=["seo_title", "search_description"])

        changed = sync_approved_homepage_seo(self.home)

        self.assertFalse(changed)
        self.home.refresh_from_db()
        self.assertEqual(self.home.seo_title, "Custom homepage SEO title")
        self.assertEqual(
            self.home.search_description,
            "Custom editor-authored homepage description.",
        )
