"""Small template helpers for reusable doctor and clinic records."""

from django import template


register = template.Library()


@register.filter
def live_profile_url(entity):
    """Return the first published public page linked to a snippet record."""

    pages = getattr(entity, "pages", None)
    if pages is None:
        return ""
    page = pages.live().public().first()
    return page.url if page else ""
