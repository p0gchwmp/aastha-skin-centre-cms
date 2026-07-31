import html
import json
import re
from datetime import date

from django.test import override_settings
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from home.models import (
    BlogPage,
    ClinicLocation,
    ClinicPage,
    ConditionPage,
    ContentIndexPage,
    Doctor,
    DoctorPage,
    HomePage,
    SiteSettings,
    TreatmentPage,
)


PUBLIC_URL = "https://www.aasthaskincentre.in"
PUBLIC_HOST = "www.aasthaskincentre.in"
RENDER_HOST = "aastha-skin-centre-cms.onrender.com"


def json_ld_payloads(response):
    source = response.content.decode("utf-8")
    scripts = re.findall(
        r'<script\s+type=["\']application/ld\+json["\'][^>]*>(.*?)</script>',
        source,
        flags=re.IGNORECASE | re.DOTALL,
    )
    return [json.loads(html.unescape(script.strip())) for script in scripts]


def schema_graph(response):
    payloads = json_ld_payloads(response)
    for payload in payloads:
        if isinstance(payload, dict) and isinstance(payload.get("@graph"), list):
            graph = payload["@graph"]
            if any(entity.get("@type") == "Organization" for entity in graph):
                return graph
    raise AssertionError(f"No SEO schema graph found in {payloads!r}")


def entities_of_type(graph, entity_type):
    return [
        entity
        for entity in graph
        if entity.get("@type") == entity_type
        or (
            isinstance(entity.get("@type"), list)
            and entity_type in entity.get("@type")
        )
    ]


@override_settings(
    PUBLIC_SITE_URL=PUBLIC_URL,
    PUBLIC_SITE_HOST=PUBLIC_HOST,
    ALLOWED_HOSTS=[PUBLIC_HOST, RENDER_HOST, "testserver"],
)
class SEOFoundationTests(WagtailPageTestCase):
    def setUp(self):
        self.home = HomePage.objects.first()
        if self.home is None:
            root = Page.get_first_root_node()
            self.home = HomePage(title="Home", slug="seo-test-home")
            root.add_child(instance=self.home)

        Site.objects.all().delete()
        self.site = Site.objects.create(
            hostname=PUBLIC_HOST,
            port=443,
            root_page=self.home,
            is_default_site=True,
        )
        SiteSettings.objects.create(
            site=self.site,
            facebook_url="https://www.facebook.com/aasthaskincentre/",
            instagram_url="https://www.instagram.com/aastha_skin_centre/",
            youtube_url="https://www.youtube.com/@aasthaskincentre",
        )

        Doctor.objects.update(is_active=False)
        ClinicLocation.objects.update(is_active=False)
        self.doctor = Doctor.objects.create(
            name="Dr. Cheena Langer SEO Test",
            slug="seo-test-cheena-langer",
            qualifications="MD Dermatology",
            role="Consultant Dermatologist",
            short_bio="Dermatologist providing skin, hair and laser care in Jammu.",
            phone="7006613362",
        )
        self.karan_nagar = ClinicLocation.objects.create(
            name="Karan Nagar SEO Test",
            slug="seo-test-karan-nagar",
            address="Amphalla Chowk, Karan Nagar, Jammu",
            locality="Jammu",
            postal_code="180005",
            mobile="7006613362",
            google_maps_url="https://maps.google.com/?q=Karan+Nagar+Jammu",
            sort_order=1,
        )
        self.paloura = ClinicLocation.objects.create(
            name="Paloura SEO Test",
            slug="seo-test-paloura",
            address="Paloura Chowk, Jammu",
            locality="Jammu",
            postal_code="181121",
            mobile="9796676541",
            google_maps_url="https://maps.google.com/?q=Paloura+Jammu",
            sort_order=2,
        )

        self.doctor_page = DoctorPage(
            title="Dr. Cheena Langer SEO Test",
            slug="seo-test-doctor",
            doctor=self.doctor,
            search_description="Meet Dr. Cheena Langer, consultant dermatologist in Jammu.",
        )
        self.home.add_child(instance=self.doctor_page)

        self.karan_page = ClinicPage(
            title="Karan Nagar Skin Clinic SEO Test",
            slug="seo-test-karan-clinic",
            clinic=self.karan_nagar,
            search_description="Visit Aastha Skin Centre in Karan Nagar, Jammu.",
        )
        self.home.add_child(instance=self.karan_page)
        self.paloura_page = ClinicPage(
            title="Paloura Skin Clinic SEO Test",
            slug="seo-test-paloura-clinic",
            clinic=self.paloura,
            search_description="Visit Aastha Skin Centre in Paloura, Jammu.",
        )
        self.home.add_child(instance=self.paloura_page)

        conditions = ContentIndexPage(
            title="Conditions SEO Test",
            slug="seo-test-conditions",
            index_kind="conditions",
            search_description="Dermatology conditions treated in Jammu.",
        )
        self.home.add_child(instance=conditions)
        self.condition = ConditionPage(
            title="Acne SEO Test",
            slug="acne",
            seo_title="Acne Treatment in Jammu",
            search_description="Diagnosis-led acne treatment and dermatologist advice in Jammu.",
            review_status="approved",
            reviewed_by=self.doctor,
            medical_review_date=date(2026, 7, 30),
        )
        conditions.add_child(instance=self.condition)

        treatments = ContentIndexPage(
            title="Treatments SEO Test",
            slug="seo-test-treatments",
            index_kind="treatments",
            search_description="Dermatology treatments available in Jammu.",
        )
        self.home.add_child(instance=treatments)
        self.treatment = TreatmentPage(
            title="Laser Hair Reduction SEO Test",
            slug="laser-hair-reduction",
            search_description="Dermatologist-supervised laser hair reduction in Jammu.",
            review_status="approved",
            reviewed_by=self.doctor,
            medical_review_date=date(2026, 7, 30),
        )
        treatments.add_child(instance=self.treatment)

        blog = ContentIndexPage(
            title="Blog SEO Test",
            slug="seo-test-blog",
            index_kind="blog",
            search_description="Medically reviewed skin and hair guidance.",
        )
        self.home.add_child(instance=blog)
        self.article = BlogPage(
            title="How dermatologists assess acne SEO Test",
            slug="how-dermatologists-assess-acne",
            search_description="What happens during a dermatologist acne assessment.",
            published_date=date(2026, 7, 30),
            author=self.doctor,
            review_status="approved",
            reviewed_by=self.doctor,
            medical_review_date=date(2026, 7, 30),
        )
        blog.add_child(instance=self.article)

    def get_public(self, path, host=PUBLIC_HOST):
        return self.client.get(path, HTTP_HOST=host, secure=True)

    def test_condition_page_has_distinct_branch_and_medical_entities(self):
        response = self.get_public(self.condition.url)
        self.assertEqual(response.status_code, 200)
        graph = schema_graph(response)

        self.assertEqual(len(entities_of_type(graph, "Organization")), 1)
        self.assertEqual(len(entities_of_type(graph, "WebSite")), 1)
        clinics = entities_of_type(graph, "MedicalClinic")
        self.assertEqual(len(clinics), 2)
        self.assertEqual(len({clinic["@id"] for clinic in clinics}), 2)
        self.assertTrue(all(not isinstance(clinic["address"], list) for clinic in clinics))

        physicians = entities_of_type(graph, "Physician")
        self.assertEqual(len(physicians), 1)
        self.assertEqual(len(physicians[0]["worksFor"]), 2)

        breadcrumbs = entities_of_type(graph, "BreadcrumbList")
        self.assertEqual(len(breadcrumbs), 1)
        self.assertEqual(
            breadcrumbs[0]["itemListElement"][-1]["item"],
            f"{PUBLIC_URL}{self.condition.url}",
        )

        medical_pages = entities_of_type(graph, "MedicalWebPage")
        self.assertEqual(len(medical_pages), 1)
        self.assertEqual(medical_pages[0]["about"]["@type"], "MedicalCondition")
        self.assertEqual(medical_pages[0]["lastReviewed"], "2026-07-30")

    def test_treatment_page_uses_medical_procedure_entity(self):
        graph = schema_graph(self.get_public(self.treatment.url))
        medical_page = entities_of_type(graph, "MedicalWebPage")[0]
        self.assertEqual(medical_page["about"]["@type"], "MedicalProcedure")

    def test_blog_page_has_article_author_and_reviewer(self):
        graph = schema_graph(self.get_public(self.article.url))
        article = entities_of_type(graph, "BlogPosting")[0]
        physician_id = entities_of_type(graph, "Physician")[0]["@id"]
        self.assertEqual(article["author"]["@id"], physician_id)
        self.assertEqual(article["reviewedBy"]["@id"], physician_id)
        self.assertEqual(article["datePublished"], "2026-07-30")

    def test_doctor_page_is_a_profile_page(self):
        graph = schema_graph(self.get_public(self.doctor_page.url))
        profile = entities_of_type(graph, "ProfilePage")[0]
        physician = entities_of_type(graph, "Physician")[0]
        self.assertEqual(profile["mainEntity"]["@id"], physician["@id"])

    def test_organization_uses_verified_social_profiles(self):
        graph = schema_graph(self.get_public(self.condition.url))
        organization = entities_of_type(graph, "Organization")[0]
        self.assertEqual(
            organization["sameAs"],
            [
                "https://www.facebook.com/aasthaskincentre/",
                "https://www.instagram.com/aastha_skin_centre/",
                "https://www.youtube.com/@aasthaskincentre",
            ],
        )

    def test_render_alias_schema_still_uses_canonical_origin(self):
        graph = schema_graph(self.get_public(self.condition.url, host=RENDER_HOST))
        serialized = json.dumps(graph)
        self.assertIn(PUBLIC_URL, serialized)
        self.assertNotIn(f"https://{RENDER_HOST}", serialized)

    def test_homepage_emits_one_canonical_global_graph(self):
        response = self.get_public("/")
        payloads = json_ld_payloads(response)
        self.assertEqual(len(payloads), 1)
        graph = schema_graph(response)
        self.assertEqual(len(entities_of_type(graph, "Organization")), 1)
        self.assertEqual(len(entities_of_type(graph, "WebSite")), 1)
        self.assertEqual(len(entities_of_type(graph, "WebPage")), 1)
        self.assertEqual(
            entities_of_type(graph, "WebPage")[0]["url"],
            f"{PUBLIC_URL}/",
        )

    def test_internal_search_is_noindex_follow_on_public_domain(self):
        response = self.get_public("/search/?query=acne")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["X-Robots-Tag"], "noindex, follow")
        self.assertContains(response, '<meta name="robots" content="noindex,follow">')
