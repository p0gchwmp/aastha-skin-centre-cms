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
    "melasma-treatment": "home/editorial_v37/treatments/melasma-treatment.html",
    "fungal-infection-treatment": "home/editorial_v37/treatments/fungal-infection-treatment.html",
    "hair-fall-treatment": "home/editorial_v37/treatments/hair-fall-treatment.html",
    "hair-transplant": "home/editorial_v37/treatments/hair-transplant.html",
    "laser-hair-reduction": "home/editorial_v37/treatments/laser-hair-reduction.html",
    "botulinum-toxin-dermal-fillers": "home/editorial_v37/treatments/botulinum-toxin-dermal-fillers.html",
    "book-appointment": "home/editorial_v37/booking.html",
    "contact": "home/editorial_v37/contact.html",
    "dr-cheena-langer": "home/editorial_v37/doctor.html",
    "karan-nagar": "home/editorial_v37/clinic.html",
    "paloura": "home/editorial_v37/clinic.html",
}


@register.simple_tag
def editorial_v37_template_for(page):
    """Return a dedicated v37 include path for an explicitly migrated page."""
    slug = getattr(page, "slug", "") or ""
    return EDITORIAL_V37_TEMPLATES.get(slug, "")
