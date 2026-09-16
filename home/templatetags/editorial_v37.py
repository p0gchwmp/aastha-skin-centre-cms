"""Editorial v37 route helpers.

Only explicitly migrated public pages are routed to dedicated editorial
partials. Everything else keeps the existing ExactPageLayout / Wagtail
renderer under the shared v37 skin, which makes the migration incremental and
reversible.
"""

from django import template

register = template.Library()

EDITORIAL_V37_TEMPLATES = {
    "acne-treatment": "home/editorial_v37/treatments/acne-treatment.html",
    "acne-scar-treatment": "home/editorial_v37/treatments/acne-scar-treatment.html",
    "pigmentation-treatment": "home/editorial_v37/treatments/pigmentation-treatment.html",
    "hair-fall-treatment": "home/editorial_v37/treatments/hair-fall-treatment.html",
    "laser-hair-reduction": "home/editorial_v37/treatments/laser-hair-reduction.html",
    "dr-cheena-langer": "home/editorial_v37/doctor.html",
    "karan-nagar": "home/editorial_v37/clinic.html",
    "paloura": "home/editorial_v37/clinic.html",
}


@register.simple_tag
def editorial_v37_template_for(page):
    """Return a dedicated v37 include path for an explicitly migrated page."""
    slug = getattr(page, "slug", "") or ""
    return EDITORIAL_V37_TEMPLATES.get(slug, "")
