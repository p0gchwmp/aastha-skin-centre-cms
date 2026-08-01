"""Template tags for route-specific clinical result galleries."""

import re

from django import template
from django.utils.safestring import mark_safe

from home.clinical_results_local import gallery_markup, hero_gallery_markup


register = template.Library()
HERO_ART = re.compile(
    r'(?P<open><div\b(?=[^>]*\bclass=(?P<quote>["\'])'
    r'[^"\']*\bpage-hero-art\b[^"\']*(?P=quote))[^>]*>)'
    r'(?P<body>.*?)(?P<close></div>)',
    re.IGNORECASE | re.DOTALL,
)


def _request_path(context) -> str:
    request = context.get("request")
    page = context.get("page")
    return (
        getattr(page, "url", "")
        or getattr(request, "path_info", "/")
        or "/"
    )


@register.simple_tag(takes_context=True)
def clinical_result_gallery(context):
    return mark_safe(gallery_markup(_request_path(context)))


@register.simple_tag(takes_context=True)
def exact_page_with_clinical_results(context, exact_main):
    if not exact_main:
        return ""

    path = _request_path(context)
    hero_gallery = hero_gallery_markup(path)
    if not hero_gallery:
        return exact_main

    source = str(exact_main)

    def inject_into_hero(match: re.Match[str]) -> str:
        return (
            match.group("open")
            + match.group("body")
            + hero_gallery
            + match.group("close")
        )

    source, replacements = HERO_ART.subn(inject_into_hero, source, count=1)
    if replacements:
        return mark_safe(source)

    fallback_gallery = gallery_markup(path)
    closing_index = source.lower().rfind("</main>")
    if closing_index == -1:
        return mark_safe(source + fallback_gallery)
    return mark_safe(
        source[:closing_index] + fallback_gallery + source[closing_index:]
    )
