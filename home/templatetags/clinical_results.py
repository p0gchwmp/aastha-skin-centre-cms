"""Template tags for route-specific clinical result galleries."""

from django import template
from django.utils.safestring import mark_safe

from home.clinical_results_local import gallery_markup

register = template.Library()


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
    gallery = gallery_markup(_request_path(context))
    if not gallery:
        return exact_main

    source = str(exact_main)
    closing_index = source.lower().rfind("</main>")
    if closing_index == -1:
        return mark_safe(source + gallery)
    return mark_safe(source[:closing_index] + gallery + source[closing_index:])
