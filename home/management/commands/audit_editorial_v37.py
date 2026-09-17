from __future__ import annotations

import os
from collections import Counter
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.test import Client
from wagtail.models import Page, Site

from home.context_processors import _env_flag


PRIORITY_ROUTES = (
    "/",
    "/conditions/",
    "/treatments/",
    "/treatments/acne-treatment/",
    "/treatments/acne-scar-treatment/",
    "/treatments/pigmentation-treatment/",
    "/treatments/melasma-treatment/",
    "/treatments/hair-fall-treatment/",
    "/treatments/hair-transplant/",
    "/treatments/fungal-infection-treatment/",
    "/treatments/laser-hair-reduction/",
    "/treatments/mnrf-treatment/",
    "/treatments/fractional-co2-laser/",
    "/treatments/chemical-peels/",
    "/treatments/q-switched-laser-toning/",
    "/treatments/prp-gfc-hair-treatment/",
    "/treatments/laser-tattoo-removal/",
    "/treatments/eczema-atopic-dermatitis-treatment/",
    "/treatments/psoriasis-treatment/",
    "/treatments/urticaria-hives-treatment/",
    "/treatments/alopecia-areata-treatment/",
    "/treatments/seborrheic-dermatitis-dandruff/",
    "/treatments/vitiligo-treatment/",
    "/treatments/hifu-treatment/",
    "/treatments/hydrafacial-medifacial/",
    "/treatments/wart-mole-skin-tag-removal/",
    "/dr-cheena-langer/",
    "/locations/karan-nagar/",
    "/locations/paloura/",
    "/book-appointment/",
    "/contact/",
)

SKIP_SCHEMES = ("mailto:", "tel:", "sms:", "javascript:", "data:")
SKIP_PATH_PREFIXES = ("/admin/", "/assets/", "/media/", "/static/")


def _published_routes(site: Site) -> list[str]:
    routes: set[str] = set()
    pages = (
        Page.objects.live()
        .public()
        .descendant_of(site.root_page, inclusive=True)
        .specific()
    )
    for page in pages:
        raw_url = page.get_url(current_site=site)
        if not raw_url:
            continue
        path = urlparse(raw_url).path or "/"
        if not path.startswith("/"):
            path = f"/{path}"
        routes.add(path)
    return sorted(routes)


def _internal_link_path(href: str, allowed_hosts: set[str]) -> str | None:
    value = (href or "").strip()
    if not value or value == "#" or value.startswith(SKIP_SCHEMES):
        return None
    if value.startswith("#"):
        return None

    parsed = urlparse(value)
    if parsed.scheme and parsed.scheme not in {"http", "https"}:
        return None
    if parsed.netloc and parsed.netloc.lower() not in allowed_hosts:
        return None

    path = parsed.path or "/"
    if path.startswith(SKIP_PATH_PREFIXES):
        return None
    return path


class Command(BaseCommand):
    help = "Render every public page and block an unsafe Editorial v37 deployment."

    def handle(self, *args, **options):
        if not _env_flag("AASTHA_EDITORIAL_V37", False):
            self.stdout.write("Editorial v37 audit skipped: rollout flag is off.")
            return

        host = (
            os.environ.get("SITE_HOSTNAME")
            or os.environ.get("RENDER_EXTERNAL_HOSTNAME")
            or "localhost"
        ).split(":", 1)[0].lower()
        secure = not settings.DEBUG
        client = Client(HTTP_HOST=host)
        failures: list[str] = []
        warnings: list[str] = []
        discovered_links: set[str] = set()

        site = Site.objects.filter(is_default_site=True).select_related("root_page").first()
        if site is None:
            raise CommandError("Editorial v37 audit cannot run without a default Wagtail Site.")

        published_routes = _published_routes(site)
        audit_routes = sorted(set(published_routes).union(PRIORITY_ROUTES))

        public_host = (getattr(settings, "PUBLIC_SITE_HOST", "") or "").lower()
        allowed_hosts = {host, site.hostname.lower()}
        if public_host:
            allowed_hosts.add(public_host)
        allowed_hosts.update({"aasthaskincentre.in", "www.aasthaskincentre.in"})

        for route in audit_routes:
            response = client.get(route, secure=secure, follow=False)
            if response.status_code != 200:
                failures.append(f"{route}: expected 200, got {response.status_code}")
                continue

            html = response.content.decode("utf-8", errors="replace")
            lowered = html.lower()
            if "editorial-v37" not in html:
                failures.append(f"{route}: editorial v37 assets/class missing")
            if "/concept/" in html:
                failures.append(f"{route}: leaked /concept/ URL")

            soup = BeautifulSoup(html, "html.parser")
            if soup.title is None or not soup.title.get_text(strip=True):
                failures.append(f"{route}: missing document title")
            if soup.find("meta", attrs={"name": "description"}) is None:
                failures.append(f"{route}: missing meta description")
            if soup.find("link", attrs={"rel": "canonical"}) is None:
                failures.append(f"{route}: missing canonical link")

            ids = [node.get("id") for node in soup.find_all(attrs={"id": True})]
            duplicate_ids = sorted(key for key, count in Counter(ids).items() if key and count > 1)
            if duplicate_ids:
                failures.append(
                    f"{route}: duplicate id(s): {', '.join(duplicate_ids[:8])}"
                )

            dead_hash_links = [
                node for node in soup.find_all("a", href=True) if node.get("href", "").strip() == "#"
            ]
            if dead_hash_links:
                failures.append(f"{route}: contains {len(dead_hash_links)} dead href='#' link(s)")

            if host.endswith(".onrender.com"):
                robots_header = response.headers.get("X-Robots-Tag", "")
                robots_meta = soup.find("meta", attrs={"name": "robots"})
                robots_value = robots_meta.get("content", "") if robots_meta else ""
                if "noindex" not in robots_header.lower() and "noindex" not in robots_value.lower():
                    failures.append(f"{route}: Render staging route is not noindex")

            for anchor in soup.find_all("a", href=True):
                href = anchor.get("href", "")
                path = _internal_link_path(href, allowed_hosts)
                if path:
                    discovered_links.add(path)

            if "lorem ipsum" in lowered or "placeholder text" in lowered:
                warnings.append(f"{route}: possible placeholder copy remains")

        for path in sorted(discovered_links):
            response = client.get(path, secure=secure, follow=False)
            if response.status_code not in {200, 301, 302}:
                failures.append(
                    f"internal link {path}: expected 200/301/302, got {response.status_code}"
                )

        booking = client.get("/book-appointment/", secure=secure, follow=False)
        booking_html = booking.content.decode("utf-8", errors="replace") if booking.status_code == 200 else ""
        for marker in (
            "data-appointment-form",
            'name="name"',
            'name="mobile"',
            'name="concern"',
            "Continue on WhatsApp",
        ):
            if marker not in booking_html:
                failures.append(f"/book-appointment/: missing {marker}")

        admin = client.get("/admin/", secure=secure, follow=False)
        if admin.status_code not in {301, 302}:
            failures.append(f"/admin/: expected login redirect, got {admin.status_code}")
        location = admin.headers.get("Location", "")
        if admin.status_code in {301, 302} and "/admin/login/" not in location:
            failures.append(f"/admin/: unexpected redirect target {location!r}")

        for warning in warnings:
            self.stdout.write(self.style.WARNING(f"WARN: {warning}"))

        if failures:
            for failure in failures:
                self.stderr.write(f"FAIL: {failure}")
            raise CommandError(f"Editorial v37 audit failed with {len(failures)} issue(s).")

        self.stdout.write(
            self.style.SUCCESS(
                "Editorial v37 audit passed: "
                f"{len(audit_routes)} public routes, {len(discovered_links)} internal links, "
                "booking/admin contracts and document-integrity checks."
            )
        )
