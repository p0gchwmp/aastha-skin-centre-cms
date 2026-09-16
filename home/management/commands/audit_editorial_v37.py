from __future__ import annotations

import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.test import Client

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


class Command(BaseCommand):
    help = "Render priority routes and block an unsafe Editorial v37 deployment."

    def handle(self, *args, **options):
        if not _env_flag("AASTHA_EDITORIAL_V37", False):
            self.stdout.write("Editorial v37 audit skipped: rollout flag is off.")
            return

        host = (
            os.environ.get("SITE_HOSTNAME")
            or os.environ.get("RENDER_EXTERNAL_HOSTNAME")
            or "localhost"
        )
        secure = not settings.DEBUG
        client = Client(HTTP_HOST=host)
        failures: list[str] = []

        for route in PRIORITY_ROUTES:
            response = client.get(route, secure=secure, follow=False)
            if response.status_code != 200:
                failures.append(f"{route}: expected 200, got {response.status_code}")
                continue
            html = response.content.decode("utf-8", errors="replace")
            if "editorial-v37" not in html:
                failures.append(f"{route}: editorial v37 assets/class missing")
            if "/concept/" in html:
                failures.append(f"{route}: leaked /concept/ URL")
            if host.endswith(".onrender.com"):
                robots = response.headers.get("X-Robots-Tag", "")
                if "noindex" not in robots.lower() and 'content="noindex,nofollow"' not in html.lower():
                    failures.append(f"{route}: Render staging route is not noindex")

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

        if failures:
            for failure in failures:
                self.stderr.write(f"FAIL: {failure}")
            raise CommandError(f"Editorial v37 audit failed with {len(failures)} issue(s).")

        self.stdout.write(
            self.style.SUCCESS(
                f"Editorial v37 audit passed: {len(PRIORITY_ROUTES)} public routes + booking/admin contracts."
            )
        )
