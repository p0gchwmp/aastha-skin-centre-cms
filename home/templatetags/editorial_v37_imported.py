"""Native Editorial v37 adapter for verified legacy page content.

The old public pages remain the medical/source-of-truth during migration.  This
module reads the trusted ExactPageLayout snapshot and converts its semantic
article structure into data consumed by the native v37 templates.  It preserves
copy, lists, links and FAQs while dropping old presentation markup.
"""

from __future__ import annotations

from urllib.parse import urlsplit

from bs4 import BeautifulSoup
from django import template
from django.utils.safestring import mark_safe

from home.models import ExactPageLayout, SiteSettings
from home.templatetags.exact_pages import apply_global_facts, normalise_path
from home.templatetags.editorial_v37 import EDITORIAL_V37_GUIDES, EDITORIAL_V37_TEMPLATES

register = template.Library()

IMPORTABLE_MODELS = {
    "treatmentpage",
    "conditionpage",
    "blogpage",
    "standardpage",
}

SPECIAL_SECTION_CLASSES = {
    "faq-section",
    "related-knowledge",
    "source-note",
}

CUE_GROUPS = {
    "acne": {
        "acne",
        "blackhead",
        "whitehead",
        "papule",
        "pustule",
        "cystic",
        "oily-skin",
    },
    "scars": {"scar", "keloid", "chickenpox"},
    "hair": {"hair", "alopecia", "dandruff", "seborrheic"},
    "pigmentation": {
        "pigment",
        "melasma",
        "freckle",
        "dark-lip",
        "dark-circle",
        "black-neck",
        "sun-damage",
        "xanthelasma",
        "vitiligo",
        "q-switched",
    },
    "infection": {
        "fungal",
        "scabies",
        "molluscum",
        "abscess",
        "sti",
        "std",
    },
    "allergy": {
        "allergy",
        "eczema",
        "dermatitis",
        "urticaria",
        "hives",
        "psoriasis",
        "rosacea",
        "lichen-planus",
    },
    "growths": {"wart", "mole", "skin-tag", "dpn", "keratosis"},
    "dermatosurgery": {
        "biopsy",
        "cyst",
        "lipoma",
        "corn",
        "toenail",
        "nail-surgery",
        "screening",
    },
    "children": {"paediatric", "pediatric", "child"},
    "ageing": {
        "hifu",
        "rf-skin",
        "ipl",
        "hydrafacial",
        "medifacial",
        "cryolipolysis",
        "body-contouring",
        "botulinum",
        "filler",
    },
}


def _model_name(page) -> str:
    return (
        getattr(getattr(page, "content_type", None), "model", "")
        or page.__class__.__name__
    ).lower()


def _path_for(page, request=None) -> str:
    raw = getattr(page, "url", "") or getattr(request, "path_info", "/") or "/"
    return normalise_path(urlsplit(raw).path or "/")


def is_editorial_v37_importable(page, path: str | None = None) -> bool:
    """Return whether a page can be rendered by the semantic import adapter."""

    if page is None or _model_name(page) not in IMPORTABLE_MODELS:
        return False
    if getattr(page, "layout_mode", "hybrid") == "builder":
        return False
    public_path = normalise_path(path or getattr(page, "url", "") or "/")
    return ExactPageLayout.objects.filter(path=public_path, enabled=True).exists()


CUE_ASSETS = {
    "acne": "images/visual-cues/acne-care-512.webp",
    "scars": "images/visual-cues/scars-texture-skin-quality-512.webp",
    "hair": "images/visual-cues/hair-scalp-care-512.webp",
    "pigmentation": "images/visual-cues/pigmentation-care-512.webp",
    "infection": "images/visual-cues/fungal-infection-care-512.webp",
    "allergy": "images/visual-cues/allergy-inflammatory-rashes-512.webp",
    "growths": "images/visual-cues/moles-growths-nails-512.webp",
    "dermatosurgery": "images/visual-cues/minor-dermatosurgery-512.webp",
    "children": "images/visual-cues/childrens-dermatology-512.webp",
    "ageing": "images/visual-cues/skin-quality-ageing-512.webp",
}


def _cue_for_slug(slug: str) -> str:
    value = (slug or "").lower()
    for cue, tokens in CUE_GROUPS.items():
        if any(token in value for token in tokens):
            return CUE_ASSETS[cue]
    return "images/visual-cues/clinical-skin-care-512.webp"


def _text(node, default="") -> str:
    if node is None:
        return default
    return " ".join(node.stripped_strings).strip() or default


def _fragment_without_heading(section) -> str:
    """Return trusted section body without legacy layout wrappers."""

    clone_soup = BeautifulSoup(str(section), "html.parser")
    clone = clone_soup.find(section.name)
    if clone is None:
        return ""

    heading = clone.find(["h2", "h3"])
    if heading:
        heading.decompose()

    for unwanted in clone.select(
        "script, style, .related-care-links, .hero-actions, .article-cta"
    ):
        unwanted.decompose()

    for image in clone.find_all("img"):
        image["loading"] = "lazy"
        image["decoding"] = "async"
        image.attrs.pop("fetchpriority", None)
        image.attrs.pop("style", None)

    for anchor in clone.find_all("a", href=True):
        href = anchor.get("href", "")
        if href.startswith(("http://", "https://")):
            anchor["target"] = "_blank"
            anchor["rel"] = "noopener noreferrer"

    return mark_safe("".join(str(child) for child in clone.contents).strip())


def _faq_items(article) -> list[dict[str, object]]:
    output = []
    if article is None:
        return output
    for details in article.select(".faq-section details, .faq-clean-list details"):
        summary = details.find("summary")
        if summary is None:
            continue
        question = _text(summary)
        body = details.find(class_="faq-answer")
        if body is None:
            pieces = [
                str(child)
                for child in details.contents
                if getattr(child, "name", None) != "summary"
            ]
            answer = mark_safe("".join(pieces).strip())
        else:
            answer = mark_safe("".join(str(child) for child in body.contents).strip())
        if question and answer:
            output.append({"q": question, "a": answer})
    return output


def _link_items(root, selector: str) -> list[dict[str, str]]:
    output = []
    if root is None:
        return output
    seen = set()
    for anchor in root.select(selector):
        href = (anchor.get("href") or "").strip()
        label = _text(anchor)
        if not href or not label or href in seen:
            continue
        seen.add(href)
        output.append({"href": href, "label": label})
    return output


def _summary_items(root) -> list[dict[str, str]]:
    output = []
    if root is None:
        return output
    for item in root.select(".premium-summary-item, .premium-summary-grid > div"):
        strong = item.find(["strong", "b"])
        label = _text(strong)
        if strong:
            strong.extract()
        value = _text(item)
        if label or value:
            output.append({"label": label, "value": value})
        if len(output) >= 4:
            break
    return output


def _extract_sections(article):
    primary = []
    secondary = []
    if article is None:
        return primary, secondary

    for index, section in enumerate(article.select("section.article-section"), 1):
        classes = set(section.get("class") or [])
        if classes.intersection(SPECIAL_SECTION_CLASSES):
            continue

        # FAQs are rendered as a dedicated accordion below.
        if section.select_one(".faq-clean-list, details > summary"):
            if "faq-section" in classes:
                continue

        heading = section.find(["h2", "h3"])
        title = _text(heading)
        if not title:
            continue
        anchor = (heading.get("id") if heading else "") or f"section-{index}"
        content = _fragment_without_heading(section)
        if not content:
            continue

        item = {
            "title": title,
            "anchor": anchor,
            "html": content,
        }
        if section.find_parent("details", class_="deep-dive") is not None:
            secondary.append(item)
        else:
            primary.append(item)

    return primary, secondary


def _build_imported_article(page, request):
    path = _path_for(page, request)
    layout = ExactPageLayout.objects.filter(path=path, enabled=True).first()
    if layout is None:
        return {}

    site_settings = SiteSettings.for_request(request)
    source = apply_global_facts(layout.html, site_settings)
    soup = BeautifulSoup(source, "html.parser")

    hero = soup.select_one(".page-hero, .page-hero--professional")
    article = soup.select_one("article.prose, article.article-stack, .article-stack")
    if article is None:
        article = soup.find("article")

    h1 = hero.find("h1") if hero else soup.find("h1")
    eyebrow = (
        hero.select_one(".eyebrow, .quiet-label, .section-kicker")
        if hero
        else None
    )
    lede = hero.select_one(".lead, .page-intro") if hero else None

    source_image = None
    if hero:
        hero_img = hero.find("img")
        if hero_img:
            src = (hero_img.get("src") or "").strip()
            if src and not src.endswith((".svg", "hero-care.svg")):
                source_image = src

    primary, secondary = _extract_sections(article)
    faqs = _faq_items(article)
    related = _link_items(article, ".related-care-links a, .related-knowledge a")
    sources = _link_items(article, ".source-note a")

    slug = getattr(page, "slug", "") or ""
    model = _model_name(page)
    return {
        "path": path,
        "title": _text(h1, getattr(page, "title", "")),
        "eyebrow": _text(
            eyebrow,
            "Journal" if model == "blogpage" else "Dermatologist-led care · Jammu",
        ),
        "lede": _text(lede, getattr(page, "introduction", "")),
        "source_image": source_image,
        "fallback_image": _cue_for_slug(slug),
        "summary": _summary_items(soup),
        "sections": primary,
        "secondary_sections": secondary,
        "faqs": faqs,
        "related": related[:6],
        "sources": sources[:8],
        "is_blog": model == "blogpage",
        "is_treatment": model in {"treatmentpage", "conditionpage"},
        "section_count": len(primary) + len(secondary),
    }


@register.simple_tag(takes_context=True)
def editorial_v37_imported_article(context, page):
    if not context.get("editorial_v37_enabled"):
        return {}
    request = context.get("request")
    slug = getattr(page, "slug", "") or ""
    if slug in EDITORIAL_V37_TEMPLATES or slug in EDITORIAL_V37_GUIDES:
        return {}
    if request is None or not is_editorial_v37_importable(page, request.path_info):
        return {}
    return _build_imported_article(page, request)


__all__ = [
    "IMPORTABLE_MODELS",
    "editorial_v37_imported_article",
    "is_editorial_v37_importable",
]
