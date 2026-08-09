"""Render verified layouts while retaining CMS-managed facts and sections."""

from __future__ import annotations

from collections import defaultdict
from html import escape, unescape
import re
from urllib.parse import urlsplit

from django import template
from django.utils.safestring import mark_safe

from home.models import ExactPageLayout, SiteSettings


register = template.Library()
IMG_TAG = re.compile(r"<img\b[^>]*>", re.IGNORECASE)
LOADING_ATTR = re.compile(r"\sloading\s*=\s*([\"']).*?\1", re.IGNORECASE)
DECODING_ATTR = re.compile(r"\sdecoding\s*=\s*([\"']).*?\1", re.IGNORECASE)
FETCHPRIORITY_ATTR = re.compile(
    r"\sfetchpriority\s*=\s*([\"']).*?\1", re.IGNORECASE
)
VISIBLE_TEXT_NODE = re.compile(r"(?<=>)(?P<text>[^<]+)(?=<)")
PROTECTED_TEXT_BLOCK = re.compile(
    r"<(?:script|style|code|pre)\b[^>]*>.*?</(?:script|style|code|pre)>",
    re.IGNORECASE | re.DOTALL,
)
LIST_THEN_PARAGRAPH = re.compile(
    r'(?P<list><(?P<tag>ul|ol)\b[^>]*\bclass=(?P<quote>["\'])'
    r'[^"\']*\bclean-list\b[^"\']*(?P=quote)[^>]*>.*?</(?P=tag)>)'
    r'(?P<gap>\s*)<p(?P<attrs>[^>]*)>(?P<text>[^<]+)</p>',
    re.IGNORECASE | re.DOTALL,
)
NEXT_CLEAN_LIST = re.compile(
    r'(?P<gap>\s*)(?P<open><(?:ul|ol)\b[^>]*\bclass=(?:["\'])'
    r'[^"\']*\bclean-list\b[^"\']*(?:["\'])[^>]*>)',
    re.IGNORECASE,
)
HERO_SECTION = re.compile(
    r'(?P<hero><section\b(?=[^>]*\bclass=(?P<quote>["\'])'
    r'[^"\']*\bpage-hero\b[^"\']*(?P=quote))[^>]*>.*?</section>)',
    re.IGNORECASE | re.DOTALL,
)
ARTICLE_WITH_SIDEBAR_CLOSE = re.compile(
    r'(?P<close></article>)(?P<gap>\s*)(?=<aside\b(?=[^>]*\bclass='
    r'(?P<quote>["\'])[^"\']*\bcare-sidebar\b[^"\']*(?P=quote)))',
    re.IGNORECASE,
)
DANGLING_LIST_LEAD = '<p class="list-lead">A dermatologist may consider:</p>'


def normalise_path(value: str) -> str:
    path = urlsplit(value or "/").path or "/"
    if not path.startswith("/"):
        path = "/" + path
    if path != "/" and not path.endswith("/"):
        path += "/"
    return path


def _safe(value) -> str:
    return escape(str(value), quote=True)


def _append_img_attributes(tag: str, attributes: str) -> str:
    """Add attributes without reserialising the verified snapshot HTML."""
    if tag.endswith("/>"):
        return f"{tag[:-2]}{attributes} />"
    return f"{tag[:-1]}{attributes}>"


def _looks_like_list_item(value: str) -> bool:
    text = re.sub(r"\s+", " ", unescape(value)).strip()
    return bool(text) and len(text) <= 160 and not re.search(r"[.!?:]", text)


def repair_orphaned_list_items(source: str) -> str:
    """Repair high-confidence list items left as adjacent paragraphs."""

    output = source
    while True:
        match = LIST_THEN_PARAGRAPH.search(output)
        changed = False
        while match:
            attrs = match.group("attrs") or ""
            text_html = match.group("text")
            if "list-lead" not in attrs and _looks_like_list_item(text_html):
                remainder = output[match.end():]
                next_list = NEXT_CLEAN_LIST.match(remainder)
                item = f"<li>{text_html}</li>"
                if next_list:
                    replacement = (
                        match.group("list")
                        + match.group("gap")
                        + next_list.group("gap")
                        + next_list.group("open")
                        + item
                    )
                    output = (
                        output[:match.start()]
                        + replacement
                        + output[match.end() + next_list.end():]
                    )
                else:
                    list_html = match.group("list")
                    closing = f"</{match.group('tag')}>"
                    replacement = list_html[:-len(closing)] + item + closing
                    output = (
                        output[:match.start()]
                        + replacement
                        + output[match.end():]
                    )
                changed = True
                break
            match = LIST_THEN_PARAGRAPH.search(output, match.end())
        if not changed:
            break

    return output.replace(DANGLING_LIST_LEAD, "", 1)


def optimise_image_delivery(source: str) -> str:
    """Keep the first content image eager and defer remaining page images."""

    image_index = 0

    def replace(match: re.Match[str]) -> str:
        nonlocal image_index
        tag = match.group(0)
        is_first = image_index == 0
        image_index += 1

        tag = LOADING_ATTR.sub("", tag)
        tag = DECODING_ATTR.sub("", tag)
        tag = FETCHPRIORITY_ATTR.sub("", tag)
        if is_first:
            return _append_img_attributes(
                tag,
                ' loading="eager" decoding="async" fetchpriority="high"',
            )
        return _append_img_attributes(tag, ' loading="lazy" decoding="async"')

    return IMG_TAG.sub(replace, source)


def normalise_visible_punctuation(source: str) -> str:
    """Remove em dashes from visible copy without touching markup values."""

    def replace(match: re.Match[str]) -> str:
        text = match.group("text")
        # The verified snapshots contain both the real character and the
        # historical UTF-8 mojibake form. Keep URLs, attributes and structured
        # values byte-for-byte intact by operating only between HTML tags.
        text = text.replace("â€”", "—")
        text = re.sub(r"\s*—\s*", ", ", text)
        return text

    parts: list[str] = []
    cursor = 0
    for protected in PROTECTED_TEXT_BLOCK.finditer(source):
        parts.append(VISIBLE_TEXT_NODE.sub(replace, source[cursor:protected.start()]))
        parts.append(protected.group(0))
        cursor = protected.end()
    parts.append(VISIBLE_TEXT_NODE.sub(replace, source[cursor:]))
    return "".join(parts)


def apply_global_facts(source: str, site_settings: SiteSettings) -> str:
    """Replace centrally managed facts without changing the verified layout."""

    primary_digits = site_settings.primary_phone_digits[-10:]
    secondary_digits = site_settings.secondary_phone_digits[-10:]
    whatsapp_digits = "".join(
        character
        for character in site_settings.whatsapp_mobile
        if character.isdigit()
    )[-10:]
    fee = (
        f"{site_settings.currency_symbol}"
        f"{site_settings.consultation_fee:,.0f}"
    )
    follow_up_days = str(site_settings.follow_up_days)

    replacements = [
        (
            "https://wa.me/917006613362",
            f"https://wa.me/91{whatsapp_digits}",
        ),
        ("tel:+917006613362", f"tel:+91{primary_digits}"),
        ("tel:7006613362", f"tel:{primary_digits}"),
        ("tel:+919796676541", f"tel:+91{secondary_digits}"),
        ("tel:9796676541", f"tel:{secondary_digits}"),
        (
            "mailto:aasthaskinsurgs@gmail.com",
            f"mailto:{site_settings.email}",
        ),
        ("aasthaskinsurgs@gmail.com", site_settings.email),
        ("7006613362", site_settings.primary_mobile),
        ("9796676541", site_settings.secondary_mobile),
        ("₹500", fee),
        ("within 10 days", f"within {follow_up_days} days"),
        ("10-day period", f"{follow_up_days}-day period"),
    ]
    output = normalise_visible_punctuation(repair_orphaned_list_items(source))
    for current, replacement in replacements:
        output = output.replace(current, _safe(replacement))
    return optimise_image_delivery(output)


def _layout_value(bound_block):
    value = getattr(bound_block, "value", None)
    if not hasattr(value, "get"):
        return {}
    layout = value.get("layout")
    return layout if hasattr(layout, "get") else {}


def render_editor_additions(context) -> dict[tuple[str, str], list[str]]:
    """Render hybrid additions and group them by selected placement."""

    page = context.get("page")
    additions = getattr(page, "layout_additions", None)
    if (
        page is None
        or getattr(page, "layout_mode", "hybrid") != "hybrid"
        or not additions
    ):
        return {}

    render_context = context.flatten() if hasattr(context, "flatten") else dict(context)
    grouped: dict[tuple[str, str], list[str]] = defaultdict(list)
    for bound_block in additions:
        layout = _layout_value(bound_block)
        placement = layout.get("placement") or "flow"
        target = layout.get("target_anchor") or ""
        rendered = bound_block.render(context=render_context)
        grouped[(placement, target)].append(str(rendered))
    return grouped


def _insert_after_hero(source: str, addition: str) -> tuple[str, bool]:
    match = HERO_SECTION.search(source)
    if not match:
        return source, False
    return source[:match.end()] + addition + source[match.end():], True


def _section_pattern_for_anchor(anchor: str) -> re.Pattern[str]:
    target = re.escape(anchor)
    return re.compile(
        r'(?P<section><section\b(?=[^>]*\bclass=(?P<class_quote>["\'])'
        r'[^"\']*\barticle-section\b[^"\']*(?P=class_quote))[^>]*>'
        r'.*?\bid=(?P<id_quote>["\'])'
        + target
        + r'(?P=id_quote).*?</section>)',
        re.IGNORECASE | re.DOTALL,
    )


def _insert_at_anchor(
    source: str,
    anchor: str,
    addition: str,
    *,
    after: bool,
) -> tuple[str, bool]:
    match = _section_pattern_for_anchor(anchor).search(source)
    if not match:
        return source, False
    position = match.end() if after else match.start()
    return source[:position] + addition + source[position:], True


def _insert_before_article_end(source: str, addition: str) -> tuple[str, bool]:
    match = ARTICLE_WITH_SIDEBAR_CLOSE.search(source)
    if match:
        return source[:match.start()] + addition + source[match.start():], True

    main_close = source.lower().rfind("</main>")
    search_end = main_close if main_close >= 0 else len(source)
    article_close = source.lower().rfind("</article>", 0, search_end)
    if article_close >= 0:
        return source[:article_close] + addition + source[article_close:], True
    return source, False


def _insert_page_end(source: str, addition: str) -> tuple[str, bool]:
    position = source.lower().rfind("</main>")
    if position < 0:
        return source + addition, True
    return source[:position] + addition + source[position:], True


def inject_editor_additions(source: str, grouped) -> str:
    """Insert rendered sections into stable exact-layout landmarks.

    Missing anchors never hide editor content. The section falls back to the
    article end with a non-visible diagnostic comment, making preview failures
    obvious in source while keeping the page usable.
    """

    output = source
    fallbacks: list[str] = []

    for (placement, target), fragments in grouped.items():
        addition = "".join(fragments)
        inserted = False
        if placement == "after_hero":
            output, inserted = _insert_after_hero(output, addition)
        elif placement == "before_anchor":
            output, inserted = _insert_at_anchor(
                output,
                target,
                addition,
                after=False,
            )
        elif placement == "after_anchor":
            output, inserted = _insert_at_anchor(
                output,
                target,
                addition,
                after=True,
            )
        elif placement in {"flow", "before_sidebar"}:
            output, inserted = _insert_before_article_end(output, addition)
        elif placement == "page_end":
            output, inserted = _insert_page_end(output, addition)

        if not inserted:
            label = f"{placement}:{target}" if target else placement
            fallbacks.append(
                f"<!-- CMS placement fallback: {escape(label)} -->" + addition
            )

    if fallbacks:
        fallback_html = "".join(fallbacks)
        output, inserted = _insert_before_article_end(output, fallback_html)
        if not inserted:
            output, _ = _insert_page_end(output, fallback_html)
    return output


@register.simple_tag(takes_context=True)
def exact_page_main(context):
    request = context.get("request")
    page = context.get("page")
    if getattr(page, "layout_mode", "hybrid") == "builder":
        return ""

    public_path = getattr(page, "url", "") or getattr(
        request,
        "path_info",
        "/",
    )
    layout = ExactPageLayout.objects.filter(
        path=normalise_path(public_path),
        enabled=True,
    ).first()
    if layout is None:
        return ""

    site_settings = SiteSettings.for_request(request)
    return mark_safe(apply_global_facts(layout.html, site_settings))


@register.simple_tag(takes_context=True)
def exact_page_with_editor_sections(context, exact_main):
    if not exact_main:
        return ""
    grouped = render_editor_additions(context)
    if not grouped:
        return exact_main
    return mark_safe(inject_editor_additions(str(exact_main), grouped))
