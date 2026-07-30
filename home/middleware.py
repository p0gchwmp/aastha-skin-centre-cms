"""Small response helpers shared by every public page."""

from __future__ import annotations

from django.conf import settings as django_settings

from .models import SiteSettings


class StagingRobotsMiddleware:
    """Keep development and Render staging hosts out of search indexes.

    A Render service can accidentally be configured as ``PUBLIC_SITE_URL``
    during staging. Temporary ``*.onrender.com`` hosts must nevertheless remain
    non-indexable; only the clinic's final custom domain may be public.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        host = request.get_host().split(":", 1)[0].lower()
        is_render_host = host.endswith(".onrender.com")
        if django_settings.DEBUG or is_render_host or not (
            django_settings.PUBLIC_SITE_HOST
            and host == django_settings.PUBLIC_SITE_HOST
        ):
            response["X-Robots-Tag"] = "noindex, nofollow"
        return response


class SmartTokenMiddleware:
    """Resolve global content tokens in final public HTML.

    Resolving at response level means tokens work consistently in rich text,
    headings, buttons, imported HTML and reusable sections. Admin screens are
    intentionally skipped so editors continue to see the token itself.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if (
            request.path.startswith("/admin/")
            or getattr(response, "streaming", False)
            or response.status_code >= 400
            or "text/html" not in response.get("Content-Type", "")
        ):
            return response

        settings = SiteSettings.for_request(request)
        content = response.content.decode(response.charset)
        for token, replacement in settings.smart_tokens().items():
            content = content.replace(
                "{{ " + token + " }}",
                str(replacement),
            )
            content = content.replace(
                "{{" + token + "}}",
                str(replacement),
            )
        response.content = content.encode(response.charset)
        if response.has_header("Content-Length"):
            response["Content-Length"] = len(response.content)
        return response