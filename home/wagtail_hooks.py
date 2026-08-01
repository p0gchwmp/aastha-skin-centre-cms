from urllib.parse import urlsplit

from django.contrib import messages
from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from wagtail import hooks
from wagtail.admin.ui.components import Component
from wagtail.models import Page, Site

from .models import (
    BlogPage,
    ClinicLocation,
    ConditionPage,
    Doctor,
    ExactPageLayout,
    ReusableSection,
    TreatmentPage,
)


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}"><link rel="stylesheet" href="{}">',
        static("css/aastha_admin.css"),
        static("css/future-editor-admin.css"),
    )


class WebsiteControlPanel(Component):
    name = "aastha-control-panel"
    order = 50

    def render_html(self, parent_context):
        request = parent_context["request"]
        site = Site.find_for_request(request) or Site.objects.filter(
            is_default_site=True
        ).first()
        site_id = site.pk if site else 1
        counts = {
            "pages": Page.objects.live().public().count(),
            "blogs": BlogPage.objects.live().public().count(),
            "clinical": (
                ConditionPage.objects.live().public().count()
                + TreatmentPage.objects.live().public().count()
            ),
            "doctors": Doctor.objects.filter(is_active=True, live=True).count(),
            "clinics": ClinicLocation.objects.filter(is_active=True, live=True).count(),
            "reusable": ReusableSection.objects.filter(is_active=True, live=True).count(),
        }
        return mark_safe(f"""
        <section class="aastha-control-panel">
          <div>
            <span class="aastha-admin-kicker">Website control centre</span>
            <h2>Choose what you want to change</h2>
            <p>Pages control URLs and section order. Snippets hold reusable doctors,
            clinics and shared sections. Settings hold facts that must update
            everywhere, such as the consultation fee and phone numbers.</p>
            <div class="aastha-admin-stats">
              <span><strong>{counts["pages"]}</strong> live pages</span>
              <span><strong>{counts["clinical"]}</strong> clinical pages</span>
              <span><strong>{counts["doctors"]}</strong> active doctors</span>
              <span><strong>{counts["clinics"]}</strong> active clinics</span>
              <span><strong>{counts["reusable"]}</strong> shared sections</span>
            </div>
            <div class="aastha-editor-workflows">
              <h3>Complex changes without code</h3>
              <ol>
                <li><strong>Add to an existing design:</strong> edit the page and use Exact-design additions.</li>
                <li><strong>Build or replace a page:</strong> choose Full visual page builder and drag sections into order.</li>
                <li><strong>Add a clinic or doctor:</strong> publish a snippet; automatic lists update and an optional draft profile page is created.</li>
                <li><strong>Update many pages together:</strong> create or edit a Reusable section.</li>
              </ol>
            </div>
          </div>
          <div class="aastha-admin-actions">
            <a href="/admin/settings/home/sitesettings/{site_id}/">Edit global fee, phones and branding</a>
            <a href="/admin/pages/">Edit or add pages and sections</a>
            <a href="/admin/snippets/home/doctor/add/">Add a doctor</a>
            <a href="/admin/snippets/home/cliniclocation/add/">Add a clinic</a>
            <a href="/admin/snippets/home/reusablesection/add/">Create a reusable section</a>
            <a href="/admin/images/">Manage images</a>
            <a href="/admin/reports/">Review drafts, workflows and reports</a>
          </div>
        </section>
        """)


@hooks.register("construct_homepage_panels")
def add_control_panel(request, panels):
    panels.append(WebsiteControlPanel())


def _public_path(page, request):
    url = page.get_url(request=request) or ""
    path = urlsplit(url).path
    if path and not path.endswith("/"):
        path += "/"
    return path or "/"


@hooks.register("before_edit_page")
def explain_rendering_mode(request, page):
    specific = page.specific
    if not hasattr(specific, "layout_mode"):
        return
    exact_active = ExactPageLayout.objects.filter(
        path=_public_path(specific, request),
        enabled=True,
    ).exists()
    if exact_active and specific.layout_mode == "hybrid":
        messages.info(
            request,
            "This page keeps its verified design. Add, reorder and position new "
            "sections in ‘Exact-design additions’; the existing layout remains intact.",
        )
    elif exact_active and specific.layout_mode == "exact":
        messages.warning(
            request,
            "Exact-design-only mode is active. Sections in the editor are saved "
            "but intentionally hidden until the rendering mode is changed.",
        )
    elif specific.layout_mode == "builder":
        messages.info(
            request,
            "Full visual page builder mode is active. The public page follows the "
            "drag-and-drop order in the Full page builder field.",
        )


@hooks.register("construct_main_menu")
def simplify_main_menu(request, menu_items):
    preferred = {
        "explorer": 10,
        "images": 20,
        "documents": 30,
        "snippets": 40,
        "settings": 50,
        "reports": 60,
        "users": 70,
    }
    for item in menu_items:
        if item.name in preferred:
            item.order = preferred[item.name]
