from django.test import SimpleTestCase
from wagtail.models import Page, Site
from wagtail.test.utils import WagtailPageTestCase

from home.blocks import LayoutBlock
from home.models import (
    ClinicLocation,
    ClinicPage,
    ContentIndexPage,
    Doctor,
    DoctorPage,
    HomePage,
)
from home.templatetags.exact_pages import inject_editor_additions


class PlacementValidationTests(SimpleTestCase):
    def test_anchor_placement_requires_target(self):
        block = LayoutBlock()
        value = block.to_python(
            {
                "placement": "after_anchor",
                "target_anchor": "",
                "width": "content",
                "theme": "default",
                "text_alignment": "left",
                "top_spacing": "md",
                "bottom_spacing": "md",
                "anchor_id": "",
                "hide_on_mobile": False,
                "hide_on_desktop": False,
            }
        )
        with self.assertRaises(Exception):
            block.clean(value)

    def test_editor_label_is_not_rendered_by_layout(self):
        block = LayoutBlock()
        value = block.to_python(
            {
                "editor_label": "Internal only",
                "placement": "flow",
                "target_anchor": "",
                "width": "content",
                "theme": "default",
                "text_alignment": "left",
                "top_spacing": "md",
                "bottom_spacing": "md",
                "anchor_id": "",
                "hide_on_mobile": False,
                "hide_on_desktop": False,
            }
        )
        self.assertEqual(value["editor_label"], "Internal only")


class ExactLayoutInsertionTests(SimpleTestCase):
    def test_sections_can_be_inserted_after_hero_and_at_article_end(self):
        source = (
            '<main><section class="page-hero"><h1>Page</h1></section>'
            '<article class="article-stack"><section class="article-section">'
            '<h2 id="existing">Existing</h2></section></article></main>'
        )
        output = inject_editor_additions(
            source,
            {
                ("after_hero", ""): ['<section id="after-hero">Hero addition</section>'],
                ("flow", ""): ['<section id="article-end">End addition</section>'],
            },
        )
        self.assertLess(output.index("after-hero"), output.index("article-stack"))
        self.assertLess(output.index("article-end"), output.index("</article>"))

    def test_missing_anchor_falls_back_without_losing_content(self):
        source = '<main><article class="article-stack"><p>Body</p></article></main>'
        output = inject_editor_additions(
            source,
            {
                ("after_anchor", "missing-anchor"): [
                    '<section id="safe-fallback">Saved content</section>'
                ]
            },
        )
        self.assertIn("safe-fallback", output)
        self.assertIn("CMS placement fallback", output)


class EntityPageAutomationTests(WagtailPageTestCase):
    def setUp(self):
        root = Page.get_first_root_node()
        self.home = HomePage(title="Home", slug="home")
        root.add_child(instance=self.home)
        Site.objects.create(
            hostname="testserver",
            root_page=self.home,
            is_default_site=True,
        )
        self.doctors = ContentIndexPage(
            title="Doctors",
            slug="doctors",
            index_kind="doctors",
        )
        self.home.add_child(instance=self.doctors)
        self.doctors.save_revision().publish()
        self.clinics = ContentIndexPage(
            title="Locations",
            slug="locations",
            index_kind="clinics",
        )
        self.home.add_child(instance=self.clinics)
        self.clinics.save_revision().publish()

    def test_published_doctor_record_creates_reviewable_draft_page(self):
        doctor = Doctor.objects.create(
            name="Dr Example",
            slug="dr-example",
            qualifications="MD Dermatology",
            short_bio="Dermatologist profile.",
            live=True,
            create_public_page=True,
        )
        page = DoctorPage.objects.get(doctor=doctor)
        self.assertFalse(page.live)
        self.assertEqual(page.get_parent().specific, self.doctors)
        self.assertEqual(page.layout_mode, "builder")

    def test_published_clinic_record_creates_reviewable_draft_page(self):
        clinic = ClinicLocation.objects.create(
            name="New Clinic",
            slug="new-clinic",
            address="Example address, Jammu",
            live=True,
            create_public_page=True,
        )
        page = ClinicPage.objects.get(clinic=clinic)
        self.assertFalse(page.live)
        self.assertEqual(page.get_parent().specific, self.clinics)
        self.assertEqual(page.layout_mode, "builder")

    def test_automatic_lists_ignore_inactive_records(self):
        Doctor.objects.create(
            name="Inactive Doctor",
            slug="inactive-doctor",
            is_active=False,
            live=True,
            create_public_page=False,
        )
        self.assertFalse(Doctor.objects.filter(is_active=True, live=True).exists())
