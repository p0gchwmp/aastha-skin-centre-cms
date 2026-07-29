from django.templatetags.static import static
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from wagtail import hooks
from wagtail.admin.ui.components import Component
from wagtail.models import Page, Site

from .models import BlogPage, ConditionPage, TreatmentPage


@hooks.register("insert_global_admin_css")
def global_admin_css():
    return format_html(
        '<link rel="stylesheet" href="{}">',
        static("css/aastha_admin.css"),
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
        }
        return mark_safe(f"""
        <section class="aastha-control-panel">
          <div>
            <span class="aastha-admin-kicker">Website control centre</span>
            <h2>Choose what you want to change</h2>
            <p>Pages control the site structure. Images and snippets hold reusable
            media, doctors, clinics and sections. Settings hold facts that must
            update everywhere, such as the consultation fee and phone numbers.</p>
            <div class="aastha-admin-stats">
              <span><strong>{counts["pages"]}</strong> live pages</span>
              <span><strong>{counts["blogs"]}</strong> blog posts</span>
              <span><strong>{counts["clinical"]}</strong> clinical pages</span>
            </div>
          </div>
          <div class="aastha-admin-actions">
            <a href="/admin/settings/home/sitesettings/{site_id}/">Edit global fee, phones and branding</a>
            <a href="/admin/pages/">Edit pages</a>
            <a href="/admin/images/">Manage images</a>
            <a href="/admin/snippets/">Doctors, clinics and reusable sections</a>
            <a href="/admin/reports/">Review reports</a>
          </div>
        </section>
        """)


@hooks.register("construct_homepage_panels")
def add_control_panel(request, panels):
    panels.append(WebsiteControlPanel())


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
