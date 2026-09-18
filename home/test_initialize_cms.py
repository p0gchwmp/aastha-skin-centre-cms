from django.test import TestCase
from wagtail.models import Site

from home.management.commands.initialize_cms import (
    APPROVED_ANALYTICS_ID,
    APPROVED_FACEBOOK_URL,
    APPROVED_HOMEPAGE_META_DESCRIPTION,
    APPROVED_HOMEPAGE_SEO_TITLE,
    APPROVED_LOCATIONS_META_DESCRIPTION,
    APPROVED_SEARCH_CONSOLE_VERIFICATION,
    LEGACY_LOCATIONS_META_DESCRIPTION,
    sync_approved_homepage_seo,
    sync_approved_locations_seo,
    sync_approved_site_settings,
    sync_non_indexable_utility_pages,
)
from home.models import ContentIndexPage, HomePage, SiteSettings, StandardPage


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


class ApprovedLocationsSeoTests(TestCase):
    def setUp(self):
        self.home = HomePage.objects.first()
        self.assertIsNotNone(self.home)
        self.locations = ContentIndexPage(
            title="Clinic Locations in Jammu",
            slug="locations",
            index_kind="clinics",
            search_description=LEGACY_LOCATIONS_META_DESCRIPTION,
        )
        self.home.add_child(instance=self.locations)

    def test_legacy_locations_description_is_upgraded(self):
        changed = sync_approved_locations_seo()

        self.assertTrue(changed)
        self.locations.refresh_from_db()
        self.assertEqual(
            self.locations.search_description,
            APPROVED_LOCATIONS_META_DESCRIPTION,
        )

    def test_editor_authored_locations_description_is_preserved(self):
        custom = (
            "Custom editor-approved description for the Jammu clinic locations page."
        )
        self.locations.search_description = custom
        self.locations.save(update_fields=["search_description"])

        changed = sync_approved_locations_seo()

        self.assertFalse(changed)
        self.locations.refresh_from_db()
        self.assertEqual(self.locations.search_description, custom)


class UtilityPageIndexingTests(TestCase):
    def setUp(self):
        self.home = HomePage.objects.first()
        self.assertIsNotNone(self.home)
        self.confirmation = StandardPage(
            title="Appointment request received",
            slug="appointment-request-received",
            noindex=False,
            search_description="Appointment request received.",
        )
        self.home.add_child(instance=self.confirmation)

    def test_confirmation_page_is_forced_noindex(self):
        changed = sync_non_indexable_utility_pages()

        self.assertEqual(changed, ["/appointment-request-received/"])
        self.confirmation.refresh_from_db()
        self.assertTrue(self.confirmation.noindex)

    def test_noindex_confirmation_page_is_idempotent(self):
        self.confirmation.noindex = True
        self.confirmation.save(update_fields=["noindex"])

        changed = sync_non_indexable_utility_pages()

        self.assertEqual(changed, [])
