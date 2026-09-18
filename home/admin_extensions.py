"""Aastha-specific Wagtail admin assistance and editorial control centre."""

from __future__ import annotations

from html import unescape
import json
import re
from urllib.parse import urlsplit

from django.contrib.auth.decorators import login_required, permission_required
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.templatetags.static import static
from django.urls import path, reverse
from django.utils.html import format_html, strip_tags
from django.utils.safestring import mark_safe
from django.views.decorators.http import require_GET
from wagtail import hooks
from wagtail.admin.menu import MenuItem
from wagtail.images import get_image_model
from wagtail.models import Page

from .models import BlogPage, ClinicLocation, Doctor, ExactPageLayout, TreatmentPage
from .seo_verification import build_seo_verification_state


ARTICLE_SECTION_RE = re.compile(
    r'<section\b(?=[^>]*\bclass=(?P<quote>["\'])'
    r'[^"\']*\barticle-section\b[^"\']*(?P=quote))[^>]*>'
    r'(?P<body>.*?)</section>',
    re.IGNORECASE | re.DOTALL,
)
ID_RE = re.compile(r'\bid=(["\'])(?P<id>[a-z][a-z0-9-]*)\1', re.IGNORECASE)
HEADING_RE = re.compile(
    r'<h[2-4]\b[^>]*>(?P<label>.*?)</h[2-4]>',
    re.IGNORECASE | re.DOTALL,
)

CONTROL_CENTRE_ROUTES = (
    ("Homepage", "home", "/"),
    ("Conditions", "conditions", "/conditions/"),
    ("Treatments", "treatments", "/treatments/"),
    ("Doctor", "dr-cheena-langer", "/dr-cheena-langer/"),
    ("Karan Nagar", "karan-nagar", "/locations/karan-nagar/"),
    ("Paloura", "paloura", "/locations/paloura/"),
    ("Journal", "blog", "/blog/"),
    ("Booking", "book-appointment", "/book-appointment/"),
    ("Contact", "contact", "/contact/"),
)


def extract_anchor_options(source: str) -> list[dict[str, str]]:
    """Return stable article-section anchors and human-readable labels."""

    options: list[dict[str, str]] = []
    seen: set[str] = set()
    for section in ARTICLE_SECTION_RE.finditer(source or ""):
        body = section.group("body")
        anchor_match = ID_RE.search(section.group(0))
        if not anchor_match:
            continue
        anchor = anchor_match.group("id")
        if anchor in seen:
            continue
        heading_match = HEADING_RE.search(body)
        label = anchor.replace("-", " ").title()
        if heading_match:
            cleaned = " ".join(
                unescape(strip_tags(heading_match.group("label"))).split()
            )
            if cleaned:
                label = cleaned
        seen.add(anchor)
        options.append({"id": anchor, "label": label})
    return options


def _public_path(page, request) -> str:
    url = page.get_url(request=request) or request.path_info or "/"
    public_path = urlsplit(url).path or "/"
    if public_path != "/" and not public_path.endswith("/"):
        public_path += "/"
    return public_path


def _route_page(slug: str, path: str):
    if path == "/":
        return Page.objects.filter(depth=2).specific().first()
    return Page.objects.filter(slug=slug, live=True).specific().first()


@require_GET
@login_required(login_url="/admin/login/")
@permission_required("wagtailadmin.access_admin", raise_exception=True)
def aastha_control_centre(request):
    route_cards = []
    for label, slug, path in CONTROL_CENTRE_ROUTES:
        page = _route_page(slug, path)
        route_cards.append(
            {
                "label": label,
                "path": path,
                "page": page,
                "edit_url": f"/admin/pages/{page.pk}/edit/" if page else "",
            }
        )

    seo_verification = build_seo_verification_state()
    context = {
        "route_cards": route_cards,
        "seo_verification": seo_verification,
        "counts": {
            "pages": Page.objects.live().public().count(),
            "treatments": TreatmentPage.objects.live().count(),
            "journal": BlogPage.objects.live().count(),
            "images": get_image_model().objects.count(),
            "clinics": ClinicLocation.objects.filter(is_active=True).count(),
            "doctors": Doctor.objects.filter(is_active=True).count(),
        },
    }
    return render(request, "home/admin/aastha_control_centre.html", context)


@require_GET
@login_required(login_url="/admin/login/")
@permission_required("wagtailadmin.access_admin", raise_exception=True)
def editor_placement_map(request, page_id: int):
    page = get_object_or_404(Page, pk=page_id).specific
    public_path = _public_path(page, request)
    exact_layout = ExactPageLayout.objects.filter(
        path=public_path,
        enabled=True,
    ).first()
    return JsonResponse(
        {
            "page_id": page.pk,
            "path": public_path,
            "has_exact_layout": exact_layout is not None,
            "anchors": extract_anchor_options(exact_layout.html if exact_layout else ""),
            "fixed_placements": [
                {"id": "after_hero", "label": "Immediately after the hero"},
                {
                    "id": "before_sidebar",
                    "label": "Before consultation sidebar / article end",
                },
                {"id": "page_end", "label": "End of the page"},
            ],
        }
    )


@hooks.register("register_admin_urls")
def register_editor_placement_urls():
    return [
        path(
            "aastha-control-centre/",
            aastha_control_centre,
            name="aastha_control_centre",
        ),
        path(
            "editor-placement-map/<int:page_id>/",
            editor_placement_map,
            name="aastha_editor_placement_map",
        ),
    ]


@hooks.register("register_admin_menu_item")
def register_aastha_control_centre_menu_item():
    return MenuItem(
        "Aastha Control Centre",
        reverse("aastha_control_centre"),
        icon_name="site",
        order=1,
    )


@hooks.register("insert_editor_js")
def editor_placement_javascript():
    endpoint = reverse("aastha_editor_placement_map", args=[0]).replace(
        "/0/",
        "/__PAGE_ID__/",
    )
    return format_html(
        '<script>window.AASTHA_EDITOR_PLACEMENT_URL={};</script>'
        '<script src="{}" defer></script>',
        mark_safe(json.dumps(endpoint)),
        static("js/editor-placement-map.js"),
    )


@hooks.register("insert_global_admin_css")
def editor_placement_css():
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static("css/editor-placement-map.css"),
    )
