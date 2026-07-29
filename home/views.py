from django.conf import settings
from django.db import connection
from django.http import HttpResponse, JsonResponse


def robots_txt(request):
    if settings.DEBUG or request.get_host().endswith(".onrender.com"):
        body = "User-agent: *\nDisallow: /\n"
    else:
        body = "User-agent: *\nAllow: /\nSitemap: https://www.aasthaskincentre.in/sitemap.xml\n"
    return HttpResponse(body, content_type="text/plain")


def healthz(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1")
        cursor.fetchone()
    return JsonResponse({"status": "ok"})
