from django.conf import settings
from django.db import connection
from django.http import HttpResponse, JsonResponse


def _is_public_request(request):
    host = request.get_host().split(":", 1)[0].lower()
    return bool(settings.PUBLIC_SITE_HOST and host == settings.PUBLIC_SITE_HOST)


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
    return JsonResponse({"status": "ok"})
