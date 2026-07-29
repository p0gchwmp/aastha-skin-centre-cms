import os

from django.core.management import call_command
from django.core.management.base import BaseCommand
from wagtail.models import Site

from home.models import BlogPage, HomePage, TreatmentPage


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
