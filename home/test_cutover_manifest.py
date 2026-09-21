from django.core.management import call_command
from django.core.management.base import CommandError
from django.test import TestCase

from home.management.commands.build_cutover_manifest import build_cutover_manifest
from home.management.commands.initialize_cms import sync_local_search_pages
from home.models import HomePage


class CutoverManifestTests(TestCase):
    def setUp(self):
        self.home = HomePage.objects.first()
        self.assertIsNotNone(self.home)

    def test_manifest_is_read_only_and_reports_current_blockers(self):
        before_pages = self.home.get_descendants(inclusive=True).count()

        manifest = build_cutover_manifest()

        after_pages = self.home.get_descendants(inclusive=True).count()
        self.assertEqual(before_pages, after_pages)
        self.assertIn("technical_ready", manifest)
        self.assertIn("human_ready", manifest)
        self.assertIn("production_activation_ready", manifest)
        self.assertEqual(len(manifest["manifest_fingerprint"]), 64)
        self.assertTrue(manifest["explicit_go_live_required"])
        self.assertEqual(
            manifest["rollback"]["feature_flag"],
            "AASTHA_EDITORIAL_V37=0",
        )
        self.assertFalse(manifest["production_activation_ready"])

    def test_unverified_indexable_locality_is_a_technical_blocker(self):
        sync_local_search_pages()
        self.home.refresh_from_db()
        areas = self.home.get_children().filter(slug="areas").specific().first()
        page = areas.get_children().filter(slug="gandhi-nagar").specific().first()
        page.noindex = False
        page.save(update_fields=["noindex"])

        manifest = build_cutover_manifest()

        self.assertIn(
            "one or more locality pages are indexable without verified service-area facts",
            manifest["technical_blockers"],
        )
        unsafe_slugs = {
            item["slug"] for item in manifest["unsafe_indexable_localities"]
        }
        self.assertIn("gandhi-nagar", unsafe_slugs)

    def test_require_ready_is_opt_in_and_fails_closed(self):
        call_command("build_cutover_manifest")
        with self.assertRaises(CommandError):
            call_command("build_cutover_manifest", require_ready=True)
