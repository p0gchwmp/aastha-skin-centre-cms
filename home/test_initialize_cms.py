from django.test import TestCase
from wagtail.models import Site

from home.management.commands.initialize_cms import (
    APPROVED_FACEBOOK_URL,
    sync_approved_site_settings,
)
from home.models import SiteSettings


class ApprovedSiteSettingsTests(TestCase):
    def setUp(self):
        self.site = Site.objects.get(is_default_site=True)
        SiteSettings.objects.filter(site=self.site).delete()

    def test_blank_facebook_url_is_upgraded(self):
        site_settings = SiteSettings.objects.create(
            site=self.site,
            facebook_url="",
        )

        changed = sync_approved_site_settings(self.site)

        self.assertTrue(changed)
        site_settings.refresh_from_db()
        self.assertEqual(site_settings.facebook_url, APPROVED_FACEBOOK_URL)

    def test_generic_facebook_homepage_is_upgraded(self):
        site_settings = SiteSettings.objects.create(
            site=self.site,
            facebook_url="https://www.facebook.com/",
        )

        changed = sync_approved_site_settings(self.site)

        self.assertTrue(changed)
        site_settings.refresh_from_db()
        self.assertEqual(site_settings.facebook_url, APPROVED_FACEBOOK_URL)

    def test_explicit_future_facebook_page_is_preserved(self):
        future_url = "https://www.facebook.com/future-clinic-page/"
        site_settings = SiteSettings.objects.create(
            site=self.site,
            facebook_url=future_url,
        )

        changed = sync_approved_site_settings(self.site)

        self.assertFalse(changed)
        site_settings.refresh_from_db()
        self.assertEqual(site_settings.facebook_url, future_url)
