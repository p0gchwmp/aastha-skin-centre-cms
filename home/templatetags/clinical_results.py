"""Template tags for route-specific clinical result galleries."""

from __future__ import annotations

import re

from bs4 import BeautifulSoup, Tag
from django import template
from django.utils.safestring import mark_safe

from home.clinical_results_local import gallery_markup

register = template.Library()

CLEAN_LIST_SELECTOR = "ul.clean-list, ol.clean-list"
DANGLING_LIST_LEAD = "A dermatologist may consider:"


def _request_path(context) -> str:
    request = context.get("request")
    page = context.get("page")
    return (
        getattr(page, "url", "")
        or getattr(request, "path_info", "/")
        or "/"
    )


def _clean_text(node: Tag) -> str:
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()


def _looks_like_orphaned_item(node: Tag) -> bool:
    if node.name != "p" or "list-lead" in node.get("class", []):
        return False
    text = _clean_text(node)
    return bool(text) and len(text) <= 160 and not re.search(r"[.!?:]", text)


def repair_legacy_list_markup(source: str) -> str:
    """Repair known malformed list output without rewriting editor content.

    Some legacy snapshots closed a ``clean-list`` before their final one or two
    item-like paragraphs.  The stored CMS record may pre-date the corrected seed
    bundle, so this narrow, idempotent transform also runs at render time.
    """
    soup = BeautifulSoup(source, "html.parser")

    for list_node in list(soup.select(CLEAN_LIST_SELECTOR)):
        sibling = list_node.find_next_sibling()
        while isinstance(sibling, Tag) and _looks_like_orphaned_item(sibling):
            following = sibling.find_next_sibling()
            item = soup.new_tag("li")
            for child in list(sibling.contents):
                item.append(child.extract())

            if (
                isinstance(following, Tag)
                and following.name in {"ul", "ol"}
                and "clean-list" in following.get("class", [])
            ):
                following.insert(0, item)
            else:
                list_node.append(item)

            sibling.decompose()
            sibling = following

    for lead in list(soup.select("p.list-lead")):
        if (
            _clean_text(lead) == DANGLING_LIST_LEAD
            and lead.find_next_sibling() is None
            and isinstance(lead.parent, Tag)
            and lead.parent.name == "section"
        ):
            lead.decompose()

    return str(soup)


@register.simple_tag(takes_context=True)
def clinical_result_gallery(context):
    return mark_safe(gallery_markup(_request_path(context)))


@register.simple_tag(takes_context=True)
def exact_page_with_clinical_results(context, exact_main):
    if not exact_main:
        return ""

    source = repair_legacy_list_markup(str(exact_main))
    gallery = gallery_markup(_request_path(context))
    if not gallery:
        return mark_safe(source)

    closing_index = source.lower().rfind("</main>")
    if closing_index == -1:
        return mark_safe(source + gallery)
    return mark_safe(source[:closing_index] + gallery + source[closing_index:])
