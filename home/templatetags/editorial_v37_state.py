"""Renderer-state helpers for the Editorial v37 rollout.

Kept separate from the clinical guide registry so infrastructure changes never
need to rewrite clinical copy.
"""

from django import template

from .editorial_v37 import EDITORIAL_V37_GUIDES, EDITORIAL_V37_TEMPLATES

register = template.Library()


@register.simple_tag
def editorial_v37_is_native(page):
    """Return True when a page has a self-contained Editorial v37 renderer."""
    if page is None:
        return False
    slug = getattr(page, "slug", "") or ""
    model = getattr(getattr(page, "content_type", None), "model", "") or ""
    if model in {"homepage", "contentindexpage"}:
        return True
    return slug in EDITORIAL_V37_TEMPLATES or slug in EDITORIAL_V37_GUIDES
