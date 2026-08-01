import os

from django.conf import settings
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect

from .models import SiteSettings


def _is_public_request(request):
    host = request.get_host().split(":", 1)[0].lower()
    return bool(settings.PUBLIC_SITE_HOST and host == settings.PUBLIC_SITE_HOST)


def favicon(request):
    """Serve the CMS-managed favicon at the browser's conventional URL.

    Modern pages also emit an explicit icon link, but browsers and audit tools
    still request ``/favicon.ico``. Redirect to the selected Wagtail image when
    present; otherwise return a successful empty response instead of a noisy
    404. The no-cache policy lets a future settings change take effect quickly.
    """

    site_settings = SiteSettings.for_request(request)
    if site_settings.favicon:
        try:
            destination = site_settings.favicon.file.url
        except (AttributeError, ValueError):
            destination = ""
        if destination:
            response = redirect(destination)
            response["Cache-Control"] = "no-cache"
            return response

    response = HttpResponse(status=204)
    response["Cache-Control"] = "no-cache"
    return response


def robots_txt(request):
    if not _is_public_request(request):
        body = "User-agent: *\nDisallow: /\n"
    else:
        body = (
            "User-agent: *\nAllow: /\n"
            f"Sitemap: {settings.PUBLIC_SITE_URL}/sitemap.xml\n"
        )
    return HttpResponse(body, content_type="text/plain")


def healthz(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()

    release = (
        os.environ.get("RENDER_GIT_COMMIT")
        or os.environ.get("GIT_COMMIT")
        or "unknown"
    )
    payload = {
        "status": "ok",
        "release": release,
    }
    service_name = os.environ.get("RENDER_SERVICE_NAME")
    if service_name:
        payload["service"] = service_name

    response = JsonResponse(payload)
    response["Cache-Control"] = "no-store"
    return response
