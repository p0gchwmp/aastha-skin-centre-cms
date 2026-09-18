from __future__ import annotations

import os
from collections import Counter
from urllib.parse import urlparse

from bs4 import BeautifulSoup
from django.conf import settings
from django.contrib.staticfiles import finders
from django.core.management.base import BaseCommand, CommandError
from django.test import Client
from wagtail.models import Page, Site

from home.context_processors import _env_flag
from home.local_search import LOCAL_SEARCH_AREA_SLUGS
from home.templatetags.editorial_v37 import (
    EDITORIAL_V37_GUIDES,
    EDITORIAL_V37_TEMPLATES,
)
from home.templatetags.editorial_v37_imported import (
    is_editorial_v37_importable,
)


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
    "/areas/",
)

SKIP_SCHEMES = ("mailto:", "tel:", "sms:", "javascript:", "data:")
SKIP_PATH_PREFIXES = ("/admin/", "/assets/", "/media/", "/static/")
NATIVE_PAGE_MODELS = {"homepage", "contentindexpage"}
LEGACY_RUNTIME_MARKERS = (
    "premium-v3-preview.css",
    "premium-system-v11.css",
    "premium-v3-preview.js",
    "premium-system-v11.js",
    "pastel-clay-sprite",
)


def _published_pages(site: Site) -> list[tuple[str, Page]]:
    result: list[tuple[str, Page]] = []
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
        result.append((path, page))
    return sorted(result, key=lambda item: item[0])


def _renderer_kind(path: str, page: Page) -> str:
    slug = getattr(page, "slug", "") or ""
    model = getattr(getattr(page, "content_type", None), "model", "") or ""
    if model in NATIVE_PAGE_MODELS:
        return "native"
    if slug in EDITORIAL_V37_TEMPLATES or slug in EDITORIAL_V37_GUIDES:
        return "native"
    if slug in LOCAL_SEARCH_AREA_SLUGS:
        parent = page.get_parent().specific
        if getattr(parent, "slug", "") == "areas":
            return "native"
    if is_editorial_v37_importable(page, path):
        return "native-imported"
    return "legacy-fallback"


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

        required_ui_assets = (
            "ui/kokonut-explore.js",
            "ui/bklit-insights.js",
            "css/editorial-v37-kokonut.css",
            "ui/motion-runtime.js",
        )
        missing_ui_assets = [
            asset for asset in required_ui_assets if not finders.find(asset)
        ]
        if missing_ui_assets:
            raise CommandError(
                "Editorial UI build is incomplete; missing: "
                + ", ".join(missing_ui_assets)
            )
        secure = not settings.DEBUG
        client = Client(HTTP_HOST=host)
        failures: list[str] = []
        warnings: list[str] = []
        discovered_links: set[str] = set()

        site = Site.objects.filter(is_default_site=True).select_related("root_page").first()
        if site is None:
            raise CommandError("Editorial v37 audit cannot run without a default Wagtail Site.")

        published_pages = _published_pages(site)
        published_routes = [path for path, _page in published_pages]
        audit_routes = sorted(set(published_routes).union(PRIORITY_ROUTES))

        native_routes: list[str] = []
        fallback_routes: list[str] = []
        imported_routes: list[str] = []
        for path, page in published_pages:
            renderer = _renderer_kind(path, page)
            if renderer == "native":
                native_routes.append(path)
            elif renderer == "native-imported":
                native_routes.append(path)
                imported_routes.append(path)
            else:
                fallback_routes.append(path)

        self.stdout.write(
            "Editorial v37 renderer coverage: "
            f"{len(native_routes)}/{len(published_pages)} live pages native; "
            f"{len(fallback_routes)} legacy fallback"
            + (f"; {len(imported_routes)} use semantic import." if imported_routes else ".")
        )
        if fallback_routes:
            self.stdout.write(
                self.style.WARNING(
                    "Legacy fallback routes still requiring migration:\n  - "
                    + "\n  - ".join(fallback_routes)
                )
            )
            failures.append(
                "renderer coverage is incomplete: "
                f"{len(fallback_routes)} public route(s) still use legacy fallback"
            )

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
            leaked_runtime = [
                marker for marker in LEGACY_RUNTIME_MARKERS if marker in html
            ]
            if leaked_runtime:
                failures.append(
                    f"{route}: legacy runtime leaked under v37: "
                    + ", ".join(leaked_runtime)
                )

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

        insights = client.get(
            "/admin/website-insights/", secure=secure, follow=False
        )
        if insights.status_code not in {301, 302}:
            failures.append(
                "/admin/website-insights/: expected login redirect, "
                f"got {insights.status_code}"
            )
        insights_location = insights.headers.get("Location", "")
        if insights.status_code in {301, 302} and "/admin/login/" not in insights_location:
            failures.append(
                "/admin/website-insights/: unexpected redirect target "
                f"{insights_location!r}"
            )

        control_centre = client.get(
            "/admin/aastha-control-centre/", secure=secure, follow=False
        )
        if control_centre.status_code not in {301, 302}:
            failures.append(
                "/admin/aastha-control-centre/: expected login redirect, "
                f"got {control_centre.status_code}"
            )
        control_location = control_centre.headers.get("Location", "")
        if control_centre.status_code in {301, 302} and "/admin/login/" not in control_location:
            failures.append(
                "/admin/aastha-control-centre/: unexpected redirect target "
                f"{control_location!r}"
            )

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
                f"{len(native_routes)} native renderers, "
                "booking/admin contracts, UI island assets and document-integrity checks."
            )
        )
