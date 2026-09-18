import os

from django.core.management import call_command
from django.core.management.base import BaseCommand
from wagtail.models import Site

from home.exact_editor_sync import (
    sync_all_exact_layout_editor_fields,
    sync_uploaded_homepage_images,
)
from home.models import BlogPage, HomePage, SiteSettings, TreatmentPage


APPROVED_FACEBOOK_URL = "https://www.facebook.com/aasthaskincentre/"
APPROVED_ANALYTICS_ID = "G-G5DQPDJ53P"
APPROVED_SEARCH_CONSOLE_VERIFICATION = (
    "LejmOPRWDnzDg6WWoVLxvPwjRBWkflLm_P81L0EbEkE"
)
APPROVED_HOMEPAGE_SEO_TITLE = "Dermatologist-led Skin, Hair & Laser Care in Jammu"
APPROVED_HOMEPAGE_META_DESCRIPTION = (
    "Dermatologist-led skin, hair, laser and cosmetic care in Jammu at Aastha "
    "Skin & Dermato-Cosmetic Centre. Book a consultation with Dr. Cheena Langer."
)
LEGACY_FACEBOOK_URLS = {
    "",
    "https://facebook.com",
    "https://facebook.com/",
    "https://www.facebook.com",
    "https://www.facebook.com/",
}


def sync_approved_homepage_seo(home):
    """Fill approved homepage metadata only when editors have left it blank."""
    if home is None:
        return []

    updates = {}
    if not (home.seo_title or "").strip():
        updates["seo_title"] = APPROVED_HOMEPAGE_SEO_TITLE
    if not (home.search_description or "").strip():
        updates["search_description"] = APPROVED_HOMEPAGE_META_DESCRIPTION

    if not updates:
        return []

    for field_name, value in updates.items():
        setattr(home, field_name, value)
    home.save(update_fields=list(updates))
    return list(updates)


def sync_approved_site_settings(site):
    """Fill approved blank/placeholder settings without overwriting later edits."""
    if site is None:
        return []

    site_settings, _ = SiteSettings.objects.get_or_create(site=site)
    updates = {}

    current_facebook_url = (site_settings.facebook_url or "").strip()
    if current_facebook_url in LEGACY_FACEBOOK_URLS:
        updates["facebook_url"] = APPROVED_FACEBOOK_URL

    if not (site_settings.analytics_id or "").strip():
        updates["analytics_id"] = APPROVED_ANALYTICS_ID

    if not (site_settings.search_console_verification or "").strip():
        updates[
            "search_console_verification"
        ] = APPROVED_SEARCH_CONSOLE_VERIFICATION

    if not updates:
        return []

    for field_name, value in updates.items():
        setattr(site_settings, field_name, value)
    site_settings.save(update_fields=list(updates))
    return list(updates)


class Command(BaseCommand):
    help = "Import the v28 starter site only when the CMS is genuinely empty."

    def sync_editor_state(self):
        exact_layouts = sync_all_exact_layout_editor_fields()
        if exact_layouts:
            self.stdout.write(
                f"Prepared simple text/image/link editing for {exact_layouts} pages."
            )

        image_updates = sync_uploaded_homepage_images()
        if image_updates:
            self.stdout.write(
                "Connected uploaded Dr. Cheena Langer photos to: "
                + ", ".join(image_updates)
                + "."
            )

    def handle(self, *args, **options):
        configured_host = (
            os.environ.get("SITE_HOSTNAME")
            or os.environ.get("RENDER_EXTERNAL_HOSTNAME")
        )
        site = Site.objects.filter(is_default_site=True).first()
        if configured_host and site and site.hostname != configured_host:
            site.hostname = configured_host
            site.port = 443
            site.save(update_fields=["hostname", "port"])
            self.stdout.write(
                f"Default site hostname updated to {configured_host}."
            )

        updated_fields = sync_approved_site_settings(site)
        if updated_fields:
            self.stdout.write(
                "Approved site settings applied: "
                + ", ".join(updated_fields)
                + "."
            )

        home = HomePage.objects.first()
        homepage_seo_updates = sync_approved_homepage_seo(home)
        if homepage_seo_updates:
            self.stdout.write(
                "Approved homepage SEO applied: "
                + ", ".join(homepage_seo_updates)
                + "."
            )

        has_content = (
            TreatmentPage.objects.exists()
            or BlogPage.objects.exists()
            or (home is not None and home.get_children().exists())
        )
        if has_content:
            self.sync_editor_state()
            self.stdout.write(
                "CMS already contains pages; starter import skipped."
            )
            return
        call_command("import_v28_site")

        # A fresh import creates the site-specific settings record.
        site = Site.objects.filter(is_default_site=True).first()
        sync_approved_site_settings(site)
        sync_approved_homepage_seo(HomePage.objects.first())
        self.sync_editor_state()
