from datetime import date

from django.core.management import call_command
from django.test import RequestFactory, SimpleTestCase, TestCase
from wagtail.models import Site

from home.local_search import (
    LOCAL_SEARCH_AREAS,
    LOCAL_SEARCH_AREA_SLUGS,
    PRIORITY_TREATMENT_SLUGS,
    area_title,
)
from home.management.commands.activate_verified_local_search import (
    local_search_activation_plan,
)
from home.management.commands.initialize_cms import sync_local_search_pages
from home.models import (
    ClinicLocation,
    ContentIndexPage,
    HomePage,
    SiteSettings,
    TreatmentPage,
)
from home.seo import build_structured_data
from home.templatetags.editorial_v37 import verified_local_area_pages
from seo_support.models import ClinicSEOProfile


class LocalSearchTaxonomyTests(SimpleTestCase):
    def test_slugs_are_unique_and_titles_avoid_unsupported_best_claims(self):
        self.assertEqual(len(LOCAL_SEARCH_AREAS), len(LOCAL_SEARCH_AREA_SLUGS))
        self.assertEqual(
            len(LOCAL_SEARCH_AREA_SLUGS),
            len({area["slug"] for area in LOCAL_SEARCH_AREAS}),
        )
        for area in LOCAL_SEARCH_AREAS:
            title = area_title(area)
            self.assertNotIn("best", title.casefold())
            self.assertIn("Jammu", title)

    def test_regional_titles_do_not_claim_a_branch_or_nearby_presence(self):
        regional = [area for area in LOCAL_SEARCH_AREAS if area["kind"] == "regional"]
        self.assertTrue(regional)
        for area in regional:
            title = area_title(area)
            self.assertIn("for patients from", title)
            self.assertNotIn("near ", title.casefold())


class LocalSearchActivationTests(TestCase):
    def setUp(self):
        self.home = HomePage.objects.first()
        self.assertIsNotNone(self.home)
        sync_local_search_pages()
        self.home.refresh_from_db()

        self.clinic = ClinicLocation.objects.create(
            name="Local SEO Verification Clinic",
            slug="local-seo-verification-clinic",
            address="Jammu",
            is_active=True,
        )

    def test_activation_is_dry_run_and_requires_complete_service_area_verification(self):
        before = local_search_activation_plan()
        self.assertEqual(before["activate"], [])
        self.assertEqual(len(before["pending"]), len(LOCAL_SEARCH_AREAS))

        first = LOCAL_SEARCH_AREAS[0]
        profile = ClinicSEOProfile.objects.create(
            clinic=self.clinic,
            service_area=first["name"],
            facts_verified_on=date(2026, 9, 18),
        )

        date_only = local_search_activation_plan()
        self.assertEqual(date_only["activate"], [])

        profile.verification_reviewer = "SEO reviewer"
        profile.verification_notes = "Checked against current branch service-area records."
        profile.save(update_fields=["verification_reviewer", "verification_notes"])

        ready = local_search_activation_plan()
        self.assertEqual([item["slug"] for item in ready["activate"]], [first["slug"]])

        call_command("activate_verified_local_search")
        areas = self.home.get_children().filter(slug="areas").specific().first()
        page = areas.get_children().filter(slug=first["slug"]).specific().first()
        page.refresh_from_db()
        areas.refresh_from_db()
        self.assertTrue(page.noindex)
        self.assertTrue(areas.noindex)

    def test_verified_area_links_exclude_noindex_pages(self):
        first = LOCAL_SEARCH_AREAS[0]
        ClinicSEOProfile.objects.create(
            clinic=self.clinic,
            service_area=first["name"],
            verification_reviewer="SEO reviewer",
            verification_notes="Checked against current branch service-area records.",
            facts_verified_on=date(2026, 9, 18),
        )

        self.assertEqual(verified_local_area_pages(), [])
        call_command("activate_verified_local_search", apply=True)

        links = verified_local_area_pages()
        self.assertEqual([page.slug for page in links], [first["slug"]])
        self.assertTrue(all(not page.noindex for page in links))

    def test_apply_indexes_only_verified_area_and_hub(self):
        first = LOCAL_SEARCH_AREAS[0]
        second = LOCAL_SEARCH_AREAS[1]
        ClinicSEOProfile.objects.create(
            clinic=self.clinic,
            service_area=first["name"],
            verification_reviewer="SEO reviewer",
            verification_notes="Checked against current branch service-area records.",
            facts_verified_on=date(2026, 9, 18),
        )

        call_command("activate_verified_local_search", apply=True)

        areas = self.home.get_children().filter(slug="areas").specific().first()
        first_page = areas.get_children().filter(slug=first["slug"]).specific().first()
        second_page = areas.get_children().filter(slug=second["slug"]).specific().first()
        areas.refresh_from_db()
        first_page.refresh_from_db()
        second_page.refresh_from_db()

        self.assertFalse(areas.noindex)
        self.assertFalse(first_page.noindex)
        self.assertTrue(second_page.noindex)


class LocalSearchSchemaTests(TestCase):
    def setUp(self):
        self.home = HomePage.objects.first()
        self.assertIsNotNone(self.home)
        sync_local_search_pages()
        self.home.refresh_from_db()
        self.site = Site.objects.get(is_default_site=True)
        self.settings, _ = SiteSettings.objects.get_or_create(site=self.site)

        treatments = ContentIndexPage(
            title="Local SEO treatments",
            slug="local-seo-treatments",
            index_kind="treatments",
            search_description="Treatment directory for local SEO schema testing.",
        )
        self.home.add_child(instance=treatments)
        treatments.save_revision().publish()

        self.treatment = TreatmentPage(
            title="Acne Treatment",
            slug=PRIORITY_TREATMENT_SLUGS[0],
            search_description=(
                "Dermatologist-led acne treatment information in Jammu for "
                "local-search schema testing."
            ),
        )
        treatments.add_child(instance=self.treatment)
        self.treatment.save_revision().publish()

    def test_area_page_schema_contains_place_and_visible_service_itemlist(self):
        area = LOCAL_SEARCH_AREAS[0]
        areas = self.home.get_children().filter(slug="areas").specific().first()
        page = areas.get_children().filter(slug=area["slug"]).specific().first()
        path = page.get_url() or f"/areas/{area['slug']}/"
        origin = "https://www.aasthaskincentre.in"
        request = RequestFactory().get(path, HTTP_HOST="www.aasthaskincentre.in")

        payload = build_structured_data(
            page=page,
            request=request,
            origin=origin,
            canonical_url=f"{origin}{path}",
            site_settings=self.settings,
            clinics=[],
            doctors=[],
        )
        collection = next(
            entity
            for entity in payload["@graph"]
            if entity.get("@type") == "CollectionPage"
        )

        self.assertEqual(collection["about"], {"@type": "Place", "name": area["name"]})
        item_list = collection["mainEntity"]
        self.assertEqual(item_list["@type"], "ItemList")
        self.assertEqual(
            item_list["itemListElement"][0]["name"],
            self.treatment.title,
        )
        self.assertEqual(
            item_list["itemListElement"][0]["url"],
            f"{origin}{self.treatment.get_url()}",
        )
