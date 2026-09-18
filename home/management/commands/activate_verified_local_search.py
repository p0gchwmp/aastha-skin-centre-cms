"""Safely activate verified local-search pages for indexing."""

from __future__ import annotations

from django.core.management.base import BaseCommand
from wagtail.models import Page

from home.local_search import AREA_BY_SLUG, LOCAL_SEARCH_AREAS
from seo_support.models import ClinicSEOProfile


def verified_service_area_names() -> set[str]:
    return {
        area.casefold()
        for profile in ClinicSEOProfile.objects.filter(
            facts_verified_on__isnull=False
        )
        for area in profile.service_areas
    }


def local_search_activation_plan() -> dict[str, object]:
    verified = verified_service_area_names()
    areas_index = Page.objects.live().public().filter(slug="areas").specific().first()
    activate = []
    pending = []

    if areas_index is None:
        return {
            "index": None,
            "activate": [],
            "pending": [area["slug"] for area in LOCAL_SEARCH_AREAS],
        }

    for area in LOCAL_SEARCH_AREAS:
        page = (
            areas_index.get_children()
            .live()
            .public()
            .filter(slug=area["slug"])
            .specific()
            .first()
        )
        if page is None:
            pending.append(area["slug"])
            continue
        if area["name"].casefold() in verified:
            activate.append(
                {
                    "slug": area["slug"],
                    "name": area["name"],
                    "page_id": page.pk,
                    "path": page.get_url() or page.url_path,
                    "currently_noindex": bool(getattr(page, "noindex", True)),
                }
            )
        else:
            pending.append(area["slug"])

    return {
        "index": {
            "page_id": areas_index.pk,
            "path": areas_index.get_url() or areas_index.url_path,
            "currently_noindex": bool(getattr(areas_index, "noindex", True)),
        },
        "activate": activate,
        "pending": pending,
    }


class Command(BaseCommand):
    help = (
        "Preview or apply indexation for local-search pages whose service-area "
        "facts have a dated Clinic SEO verification."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--apply",
            action="store_true",
            help="Apply the verified-only indexation plan. Default is dry-run.",
        )

    def handle(self, *args, **options):
        plan = local_search_activation_plan()
        activate = plan["activate"]
        pending = plan["pending"]
        index = plan["index"]

        self.stdout.write(
            f"Verified local-search activation plan: {len(activate)} ready, "
            f"{len(pending)} pending verification."
        )
        for item in activate:
            self.stdout.write(f"READY — {item['path']} ({item['name']})")
        for slug in pending:
            self.stdout.write(self.style.WARNING(f"PENDING — /areas/{slug}/"))

        if not options["apply"]:
            self.stdout.write("Dry run only; no indexation settings changed.")
            return

        if index is None:
            self.stdout.write(
                self.style.WARNING("Areas index does not exist; nothing changed.")
            )
            return

        changed = []
        for item in activate:
            page = Page.objects.get(pk=item["page_id"]).specific
            if getattr(page, "noindex", True):
                page.noindex = False
                page.save(update_fields=["noindex"])
                changed.append(item["path"])

        areas_index = Page.objects.get(pk=index["page_id"]).specific
        should_index_hub = bool(activate)
        if should_index_hub and getattr(areas_index, "noindex", True):
            areas_index.noindex = False
            areas_index.save(update_fields=["noindex"])
            changed.append(index["path"])

        self.stdout.write(
            self.style.SUCCESS(
                f"Activated {len(changed)} verified local-search route(s)."
            )
        )
