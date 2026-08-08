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
            "exact": ExactPageLayout.objects.filter(enabled=True).count(),
        }
        return mark_safe(f"""
        <section class="aastha-control-panel">
          <div>
            <span class="aastha-admin-kicker">Website control centre</span>
            <h2>Choose what you want to change</h2>
            <p>Use <strong>Editable page content</strong> for existing wording,
            photographs and button destinations. Use Pages for page settings,
            hero images, new premium sections and complete builder layouts.
            Settings hold facts that must update everywhere, such as the fee,
            phone numbers and branding.</p>
            <div class="aastha-admin-stats">
              <span><strong>{counts["pages"]}</strong> live pages</span>
              <span><strong>{counts["exact"]}</strong> simple content editors</span>
              <span><strong>{counts["clinical"]}</strong> clinical pages</span>
              <span><strong>{counts["doctors"]}</strong> active doctors</span>
              <span><strong>{counts["clinics"]}</strong> active clinics</span>
              <span><strong>{counts["reusable"]}</strong> shared sections</span>
            </div>
            <div class="aastha-editor-workflows">
              <h3>Simple editing without code</h3>
              <ol>
                <li><strong>Change existing text, images or buttons:</strong> open Editable page content and choose the page path.</li>
                <li><strong>Change a page hero photograph:</strong> edit the Page and use Hero image.</li>
                <li><strong>Add a luxury text + photo section:</strong> edit the Page → Exact-design additions → Split text and media. Choose media left/right; the site handles the criss-cross reveal automatically.</li>
                <li><strong>Add a real before/after slider:</strong> edit the Page → Exact-design additions → Two-image comparison. Upload separate approved Before and After photographs; the draggable slider is automatic.</li>
                <li><strong>Add galleries, FAQs or treatment cards:</strong> use the matching visual block in Exact-design additions. Styling and motion are automatic.</li>
                <li><strong>Build or replace a page:</strong> choose Full visual page builder and drag sections into order.</li>
              </ol>
            </div>
          </div>
          <div class="aastha-admin-actions">
            <a href="/admin/snippets/home/exactpagelayout/">Edit existing page text, images and buttons</a>
            <a href="/admin/pages/">Edit page settings, hero images or premium sections</a>
            <a href="/admin/settings/home/sitesettings/{site_id}/">Edit global fee, phones and branding</a>
            <a href="/admin/images/">Upload or manage images</a>
            <a href="/admin/snippets/home/doctor/">Edit doctor profile and photograph</a>
            <a href="/admin/snippets/home/cliniclocation/">Edit clinic locations and photographs</a>
            <a href="/admin/snippets/home/reusablesection/add/">Create a reusable section</a>
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
    public_path = _public_path(specific, request)
    exact_layout = ExactPageLayout.objects.filter(
        path=public_path,
        enabled=True,
    ).first()
    if exact_layout and specific.layout_mode == "hybrid":
        messages.info(
            request,
            format_html(
                "This page keeps its verified design. The Hero image field changes "
                "the live hero. To change existing wording, other images or buttons, "
                "open <a href=\"/admin/snippets/home/exactpagelayout/\">Editable "
                "page content</a> and choose <strong>{}</strong>. For new premium "
                "sections use Exact-design additions: Split text and media creates "
                "the criss-cross layout, and Two-image comparison creates a real "
                "draggable before/after slider when two distinct images are supplied.",
                public_path,
            ),
        )
    elif exact_layout and specific.layout_mode == "exact":
        messages.warning(
            request,
            format_html(
                "Exact-design-only mode is active. Existing wording, images and "
                "buttons remain editable in <a href=\"/admin/snippets/home/"
                "exactpagelayout/\">Editable page content</a>; added sections are "
                "hidden until the rendering mode changes."
            ),
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
