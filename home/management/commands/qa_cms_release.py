from __future__ import annotations

from collections import Counter
from html.parser import HTMLParser
import re
from urllib.parse import urlsplit
from uuid import uuid4
from pathlib import Path

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import connection, transaction
from django.test import Client
from wagtail.models import Page, Site

from home.blocks import PageBodyStreamBlock
from home.local_search import LOCAL_SEARCH_AREAS
from home.models import (
    BlogPage,
    ClinicLocation,
    Doctor,
    SiteSettings,
    TreatmentPage,
)


EXPECTED_BLOG_PATHS = {
    "/blog/blackheads/",
    "/blog/whiteheads/",
    "/blog/acne-papules/",
    "/blog/acne-pustules/",
    "/blog/acne-nodules/",
    "/blog/cystic-acne/",
    "/blog/oily-skin-and-acne/",
    "/blog/post-acne-red-marks/",
    "/blog/post-acne-dark-marks/",
    "/blog/acne-like-eruptions/",
}

EXPECTED_ACNE_DESTINATIONS = EXPECTED_BLOG_PATHS | {
    "/treatments/acne-scar-treatment/",
}

EXPECTED_BLOCKS = {
    "hero",
    "text",
    "image",
    "video",
    "carousel",
    "gallery",
    "card_grid",
    "faq",
    "accordion",
    "cta",
    "related_pages",
    "doctors",
    "clinics",
    "pricing",
    "reusable",
    "spacer",
    "advanced_html",
}

FORBIDDEN_PUBLIC_TEXT = {
    "website verification file",
    "content-ready template",
    "starter policy",
    "implementation note",
}

UNRESOLVED_TEMPLATE_PATTERN = re.compile(
    r"{{\s*[A-Za-z_][^{}]*}}|{%\s*[^%]+%}"
)

HARDCODED_GLOBAL_FACTS = {
    "₹500",
    "7006613362",
    "9796676541",
    "within 10 days",
    "aasthaskinsurgs@gmail.com",
}


def normalise_path(value):
    path = urlsplit(value).path or "/"
    if not path.startswith("/"):
        path = "/" + path
    if "." not in path.rsplit("/", 1)[-1] and not path.endswith("/"):
        path += "/"
    return path


class PublicHTMLAudit(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.main_depth = 0
        self.links: list[tuple[str, bool]] = []
        self.ids: list[str] = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        if tag == "main":
            self.main_depth += 1
        if values.get("id"):
            self.ids.append(values["id"])
        if tag == "a" and values.get("href"):
            self.links.append((values["href"], self.main_depth > 0))

    def handle_endtag(self, tag):
        if tag == "main" and self.main_depth:
            self.main_depth -= 1


class Command(BaseCommand):
    help = "Run release-level checks against the imported Aastha CMS site."

    def handle(self, *args, **options):
        errors: list[str] = []
        site = Site.objects.filter(is_default_site=True).first()
        if site is None:
            raise CommandError("No default Wagtail site exists.")

        client = Client(HTTP_HOST=site.hostname)
        get = lambda path: client.get(path, secure=True)

        if connection.vendor == "sqlite":
            with connection.cursor() as cursor:
                cursor.execute("PRAGMA integrity_check")
                integrity = cursor.fetchone()[0]
            if integrity != "ok":
                raise CommandError(
                    "SQLite integrity check failed; rebuild the disposable "
                    "local verification database."
                )

        pages = list(
            site.root_page.get_descendants(inclusive=True)
            .live()
            .public()
            .specific()
        )
        expected_public_pages = 77 + 1 + len(LOCAL_SEARCH_AREAS)
        if len(pages) != expected_public_pages:
            errors.append(
                f"Expected {expected_public_pages} public CMS pages; "
                f"found {len(pages)}."
            )
        expected_area_paths = {
            "/areas/",
            *{
                f"/areas/{area['slug']}/"
                for area in LOCAL_SEARCH_AREAS
            },
        }
        actual_area_paths = {
            page.get_url()
            for page in pages
            if (page.get_url() or "").startswith("/areas/")
        }
        if actual_area_paths != expected_area_paths:
            errors.append(
                "Local-search area route set differs from the approved "
                "patient-useful locality graph."
            )
        if TreatmentPage.objects.live().public().count() != 52:
            errors.append("Expected 52 imported clinical treatment pages.")
        if BlogPage.objects.live().public().count() != 10:
            errors.append("Expected 10 dedicated blog pages.")
        if ClinicLocation.objects.filter(is_active=True, live=True).count() != 2:
            errors.append("Expected two active clinic snippets.")
        if Doctor.objects.filter(is_active=True, live=True).count() != 1:
            errors.append("Expected one active doctor snippet.")
        if ClinicLocation.objects.filter(
            latest_revision__isnull=True
        ).exists():
            errors.append("A clinic snippet has no recoverable revision.")
        if Doctor.objects.filter(latest_revision__isnull=True).exists():
            errors.append("A doctor snippet has no recoverable revision.")

        actual_blocks = set(PageBodyStreamBlock().child_blocks)
        missing_blocks = EXPECTED_BLOCKS - actual_blocks
        if missing_blocks:
            errors.append(
                "Page builder is missing blocks: "
                + ", ".join(sorted(missing_blocks))
            )

        rendered: dict[str, str] = {}
        internal_targets: set[str] = set()
        for page in pages:
            path = page.get_url() or "/"
            response = get(path)
            if response.status_code != 200:
                errors.append(f"{path} returned HTTP {response.status_code}.")
                continue
            body = response.content.decode(response.charset)
            rendered[path] = body

            lowered = body.casefold()
            for phrase in FORBIDDEN_PUBLIC_TEXT:
                if phrase in lowered:
                    errors.append(f"{path} contains forbidden text: {phrase}")
            if UNRESOLVED_TEMPLATE_PATTERN.search(body):
                errors.append(f"{path} contains an unresolved template token.")

            audit = PublicHTMLAudit()
            audit.feed(body)
            duplicate_ids = [
                identifier
                for identifier, count in Counter(audit.ids).items()
                if count > 1
            ]
            if duplicate_ids:
                errors.append(
                    f"{path} has duplicate IDs: {', '.join(duplicate_ids[:5])}"
                )

            for href, inside_main in audit.links:
                parts = urlsplit(href)
                if (
                    parts.scheme
                    or href.startswith(("#", "mailto:", "tel:"))
                    or parts.path.startswith(
                        ("/assets/", "/media/", "/documents/", "/admin/")
                    )
                ):
                    continue
                target = normalise_path(href)
                internal_targets.add(target)
                if inside_main and target == normalise_path(path):
                    errors.append(f"{path} contains a main-content self-link.")

            page_body = getattr(page, "body", None)
            if page_body is not None:
                stored = str(page_body.raw_data)
                for fact in HARDCODED_GLOBAL_FACTS:
                    if fact in stored:
                        errors.append(
                            f"{path} hard-codes global fact {fact!r} "
                            "inside page content."
                        )

        for target in sorted(internal_targets):
            status = get(target).status_code
            if status not in {200, 301, 302}:
                errors.append(
                    f"Internal link target {target} returned HTTP {status}."
                )

        operational_routes = {
            "/healthz/": "status",
            "/robots.txt": "User-agent",
            "/sitemap.xml": "<urlset",
            "/search/?query=acne": "Search the website",
        }
        for route, expected_text in operational_routes.items():
            response = get(route)
            body = response.content.decode(response.charset)
            if response.status_code != 200 or expected_text not in body:
                errors.append(f"Operational route {route} failed its check.")

        home_response = get("/")
        if home_response.get("X-Robots-Tag") != "noindex, nofollow":
            errors.append("Development/staging noindex response header is absent.")

        actual_blog_paths = {
            page.get_url() for page in BlogPage.objects.live().public()
        }
        if actual_blog_paths != EXPECTED_BLOG_PATHS:
            errors.append(
                "Dedicated blog path set differs from the v28 content graph."
            )

        acne_body = rendered.get("/treatments/acne-treatment/", "")
        acne_audit = PublicHTMLAudit()
        acne_audit.feed(acne_body)
        acne_targets = {
            normalise_path(href)
            for href, inside_main in acne_audit.links
            if inside_main and href.startswith("/")
        }
        missing_acne_links = EXPECTED_ACNE_DESTINATIONS - acne_targets
        if missing_acne_links:
            errors.append(
                "Acne page is missing dedicated destinations: "
                + ", ".join(sorted(missing_acne_links))
            )

        dark_lips = rendered.get(
            "/treatments/dark-lips-treatment/",
            "",
        )
        if dark_lips.count("Dr. Cheena Langer’s timings") > 1:
            errors.append("Dark Lips page repeats the doctor timings heading.")

        appointment = rendered.get("/book-appointment/", "")
        required_appointment_markup = {
            "appointment form": "data-appointment-form",
            "dynamic WhatsApp destination": "data-whatsapp-url=",
            "appointment interaction script": "appointment-form-controller",
        }
        for label, marker in required_appointment_markup.items():
            if marker not in appointment:
                errors.append(
                    f"Book Appointment page is missing {label}: {marker}"
                )

        cms_script = (
            Path(__file__).resolve().parents[3]
            / "aastha_cms"
            / "static"
            / "js"
            / "aastha_cms.js"
        ).read_text(encoding="utf-8")
        if '[data-appointment-form]' not in cms_script:
            errors.append("CMS JavaScript does not initialise the appointment form.")
        for hardcoded_phone in {"7006613362", "9796676541"}:
            if hardcoded_phone in cms_script:
                errors.append(
                    "CMS JavaScript hard-codes a clinic phone number."
                )

        settings = SiteSettings.for_site(site)
        if len(settings.header_navigation) < 6:
            errors.append("Header navigation was not imported as page links.")
        if len(settings.footer_navigation) < 4:
            errors.append("Footer navigation was not imported as page links.")

        # Prove that one global edit changes text and action destinations.
        with transaction.atomic():
            settings.consultation_fee = 650
            settings.follow_up_days = 14
            settings.primary_mobile = "9999911111"
            settings.whatsapp_mobile = "9999922222"
            settings.save()
            changed = get("/book-appointment/").content.decode()
            checks = {
                "fee": "₹650" in changed and "₹500" not in changed,
                "follow-up": "within 14 days" in changed,
                "phone": "9999911111" in changed,
                "WhatsApp destination": (
                    "https://wa.me/919999922222" in changed
                ),
            }
            for label, passed in checks.items():
                if not passed:
                    errors.append(
                        f"Global {label} did not update across the page."
                    )
            transaction.set_rollback(True)

        # Exercise the real no-code dashboard and the largest page editor.
        with transaction.atomic():
            user = get_user_model().objects.create_superuser(
                username=f"qa-{uuid4().hex}",
                email="cms-qa@example.invalid",
                password=uuid4().hex,
            )
            client.force_login(user)
            acne_page = TreatmentPage.objects.get(slug="acne-treatment")
            admin_urls = [
                "/admin/",
                f"/admin/pages/{acne_page.pk}/edit/",
                f"/admin/settings/home/sitesettings/{site.pk}/",
                "/admin/snippets/",
            ]
            for url in admin_urls:
                response = get(url)
                if response.status_code != 200:
                    errors.append(
                        f"Admin route {url} returned HTTP "
                        f"{response.status_code}."
                    )
            dashboard = get("/admin/").content.decode()
            if "Website control centre" not in dashboard:
                errors.append("Custom editor dashboard panel did not render.")
            control_centre = get("/admin/aastha-control-centre/")
            if control_centre.status_code != 200:
                errors.append(
                    "Authenticated SEO control centre returned HTTP "
                    f"{control_centre.status_code}."
                )
            else:
                control_html = control_centre.content.decode()
                if "Verification &amp; indexation readiness" not in control_html:
                    errors.append("SEO verification dashboard did not render.")
                if "Clinical content review queue" not in control_html:
                    errors.append("Medical review queue did not render.")
                if "No bulk approval:" not in control_html:
                    errors.append("Medical review queue guardrail did not render.")
            transaction.set_rollback(True)

        self.stdout.write(
            f"Public pages: {len(pages)}\n"
            f"Clinical pages: {TreatmentPage.objects.live().public().count()}\n"
            f"Dedicated blog pages: {BlogPage.objects.live().public().count()}\n"
            f"Page-builder blocks: {len(actual_blocks)}\n"
            f"Internal targets checked: {len(internal_targets)}"
        )
        if errors:
            for error in errors:
                self.stderr.write(self.style.ERROR(f"ERROR: {error}"))
            raise CommandError(
                f"CMS release QA failed with {len(errors)} error(s)."
            )
        self.stdout.write(
            self.style.SUCCESS("CMS release QA passed with 0 errors.")
        )
