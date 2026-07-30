from __future__ import annotations

from urllib.parse import urlparse

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from wagtail.models import Site


class Command(BaseCommand):
    help = "Validate staging or production custom-domain launch configuration."

    def add_arguments(self, parser):
        parser.add_argument(
            "--require-public",
            action="store_true",
            help="Fail unless a complete, indexable custom-domain configuration is active.",
        )

    def handle(self, *args, **options):
        errors: list[str] = []
        public_url = settings.PUBLIC_SITE_URL
        public_host = settings.PUBLIC_SITE_HOST
        redirect_hosts = set(settings.CANONICAL_REDIRECT_HOSTS)
        render_host = getattr(settings, "RENDER_EXTERNAL_HOSTNAME", "") or ""
        render_host = render_host.lower().split(":", 1)[0]

        if not public_url:
            if options["require_public"]:
                errors.append("PUBLIC_SITE_URL is blank")
            if redirect_hosts:
                errors.append(
                    "CANONICAL_REDIRECT_HOSTS must remain blank while PUBLIC_SITE_URL is blank"
                )
            if errors:
                raise CommandError("; ".join(errors))
            self.stdout.write(
                self.style.SUCCESS(
                    "Staging configuration is safe: public indexing and canonical redirects are disabled."
                )
            )
            return

        parsed = urlparse(public_url)
        if parsed.scheme != "https":
            errors.append("PUBLIC_SITE_URL must use https")
        if not parsed.netloc or not public_host:
            errors.append("PUBLIC_SITE_URL must contain a hostname")
        if parsed.path not in ("", "/") or parsed.params or parsed.query or parsed.fragment:
            errors.append("PUBLIC_SITE_URL must be an origin without path, query or fragment")
        if public_host.endswith(".onrender.com"):
            errors.append("PUBLIC_SITE_URL must not use a Render hostname")
        if public_host != parsed.netloc.split(":", 1)[0].lower():
            errors.append("PUBLIC_SITE_HOST does not match PUBLIC_SITE_URL")

        if not self._host_is_allowed(public_host, settings.ALLOWED_HOSTS):
            errors.append("canonical host is missing from ALLOWED_HOSTS")
        if public_url not in settings.CSRF_TRUSTED_ORIGINS:
            errors.append("canonical origin is missing from CSRF_TRUSTED_ORIGINS")
        if settings.WAGTAILADMIN_BASE_URL.rstrip("/") != public_url:
            errors.append("WAGTAILADMIN_BASE_URL must equal PUBLIC_SITE_URL")

        default_site = Site.objects.filter(is_default_site=True).first()
        if default_site is None:
            errors.append("default Wagtail Site record is missing")
        elif default_site.hostname.lower() != public_host:
            errors.append(
                f"default Wagtail Site hostname is {default_site.hostname!r}, expected {public_host!r}"
            )

        if public_host in redirect_hosts:
            errors.append("canonical host must not be listed in CANONICAL_REDIRECT_HOSTS")
        render_redirects = sorted(
            host for host in redirect_hosts if host.endswith(".onrender.com")
        )
        if render_redirects:
            errors.append(
                "Render aliases must not be listed in CANONICAL_REDIRECT_HOSTS: "
                + ", ".join(render_redirects)
            )
        for host in sorted(redirect_hosts):
            if not self._host_is_allowed(host, settings.ALLOWED_HOSTS):
                errors.append(f"redirect host {host!r} is missing from ALLOWED_HOSTS")
            origin = f"https://{host}"
            if origin not in settings.CSRF_TRUSTED_ORIGINS:
                errors.append(
                    f"redirect origin {origin!r} is missing from CSRF_TRUSTED_ORIGINS"
                )

        if not settings.SECURE_SSL_REDIRECT:
            errors.append("SECURE_SSL_REDIRECT must be enabled")
        if not settings.SESSION_COOKIE_SECURE:
            errors.append("SESSION_COOKIE_SECURE must be enabled")
        if not settings.CSRF_COOKIE_SECURE:
            errors.append("CSRF_COOKIE_SECURE must be enabled")

        if errors:
            raise CommandError("\n- " + "\n- ".join(errors))

        self.stdout.write(self.style.SUCCESS("Public-domain launch configuration passed."))
        self.stdout.write(f"Canonical origin: {public_url}")
        self.stdout.write(
            "Redirect hosts: " + (", ".join(sorted(redirect_hosts)) or "none")
        )
        if render_host:
            self.stdout.write(f"Render rollback host: {render_host}")

    @staticmethod
    def _host_is_allowed(host: str, allowed_hosts: list[str]) -> bool:
        for allowed in allowed_hosts:
            value = allowed.lower().strip()
            if value == "*" or value == host:
                return True
            if value.startswith(".") and (
                host == value[1:] or host.endswith(value)
            ):
                return True
        return False
