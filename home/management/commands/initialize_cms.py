import os

from django.core.management import call_command
from django.core.management.base import BaseCommand
from wagtail.models import Site

from home.models import BlogPage, HomePage, SiteSettings, TreatmentPage


APPROVED_FACEBOOK_URL = "https://www.facebook.com/aasthaskincentre/"
LEGACY_FACEBOOK_URLS = {
    "",
    "https://facebook.com",
    "https://facebook.com/",
    "https://www.facebook.com",
    "https://www.facebook.com/",
}


def sync_approved_site_settings(site):
    """Upgrade blank/placeholder social settings without overwriting later edits."""
    if site is None:
        return False

    site_settings, _ = SiteSettings.objects.get_or_create(site=site)
    current_facebook_url = (site_settings.facebook_url or "").strip()
    if current_facebook_url not in LEGACY_FACEBOOK_URLS:
        return False

    site_settings.facebook_url = APPROVED_FACEBOOK_URL
    site_settings.save(update_fields=["facebook_url"])
    return True


class Command(BaseCommand):
    help = "Import the v28 starter site only when the CMS is genuinely empty."

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

        if sync_approved_site_settings(site):
            self.stdout.write("Approved Facebook page applied to site settings.")

        home = HomePage.objects.first()
        has_content = (
            TreatmentPage.objects.exists()
            or BlogPage.objects.exists()
            or (home is not None and home.get_children().exists())
        )
        if has_content:
            self.stdout.write(
                "CMS already contains pages; starter import skipped."
            )
            return
        call_command("import_v28_site")

        # A fresh import creates the site-specific settings record.
        site = Site.objects.filter(is_default_site=True).first()
        sync_approved_site_settings(site)
