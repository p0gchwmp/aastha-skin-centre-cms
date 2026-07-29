#!/usr/bin/env python3
"""Convert the verified static v28 pages into structured CMS seed data."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

from lxml import etree, html


LAYOUT = {
    "width": "content",
    "theme": "default",
    "text_alignment": "left",
    "top_spacing": "md",
    "bottom_spacing": "md",
    "anchor_id": "",
    "hide_on_mobile": False,
    "hide_on_desktop": False,
}


def text_of(element: etree._Element) -> str:
    return " ".join(" ".join(element.itertext()).split())


def has_class(element: etree._Element, class_name: str) -> bool:
    return class_name in (element.get("class") or "").split()


def inner_html(element: etree._Element, skip_first_heading=False) -> str:
    parts = []
    for index, child in enumerate(element):
        if (
            skip_first_heading
            and index == 0
            and child.tag in {"h1", "h2", "h3", "h4"}
        ):
            continue
        parts.append(
            etree.tostring(child, encoding="unicode", method="html")
        )
    return "".join(parts).strip()


def meta_content(document: etree._Element, name: str) -> str:
    values = document.xpath(
        f'//meta[translate(@name,"ABCDEFGHIJKLMNOPQRSTUVWXYZ","abcdefghijklmnopqrstuvwxyz")="{name.casefold()}"]/@content'
    )
    return values[0].strip() if values else ""


def canonical_path(document: etree._Element, fallback: str) -> str:
    values = document.xpath('//link[@rel="canonical"]/@href')
    if not values:
        return fallback
    value = values[0]
    return re.sub(r"^https?://[^/]+", "", value) or "/"


def button_value(link: etree._Element) -> dict | None:
    href = link.get("href", "").strip()
    label = text_of(link)
    if not href or not label:
        return None
    if href.startswith("/"):
        # The importer resolves this to a Wagtail page after every page exists.
        return {
            "link": {
                "label": label,
                "page_path": href,
                "external_url": "",
                "new_tab": False,
            },
            "style": "secondary" if "secondary" in (link.get("class") or "") else "primary",
        }
    return {
        "link": {
            "label": label,
            "page_path": "",
            "external_url": href,
            "new_tab": link.get("target") == "_blank",
        },
        "style": "secondary" if "secondary" in (link.get("class") or "") else "primary",
    }


def parse_article(article: etree._Element) -> list[dict]:
    blocks: list[dict] = []
    accordion_items: list[dict] = []

    def flush_accordion():
        nonlocal accordion_items
        if not accordion_items:
            return
        blocks.append(
            {
                "type": "accordion",
                "value": {
                    "heading": "Detailed guidance",
                    "items": accordion_items,
                    "open_first": False,
                    "layout": {**LAYOUT, "top_spacing": "lg", "bottom_spacing": "lg"},
                },
            }
        )
        accordion_items = []

    for child in list(article):
        if not isinstance(child.tag, str):
            continue

        if child.tag == "details" and has_class(child, "deep-dive"):
            summary = next((node for node in child if node.tag == "summary"), None)
            body = next(
                (node for node in child if has_class(node, "deep-dive-body")),
                None,
            )
            if summary is not None and body is not None:
                accordion_items.append(
                    {
                        "heading": text_of(summary),
                        "body": inner_html(body),
                    }
                )
            continue

        flush_accordion()

        if child.tag == "p" and has_class(child, "medical-disclaimer"):
            continue
        if child.tag == "section" and has_class(child, "clinic-choice-section"):
            continue

        if child.tag == "section" and has_class(child, "faq-section"):
            items = []
            for details in child.iter("details"):
                summary = next(
                    (node for node in details if node.tag == "summary"),
                    None,
                )
                answer = next(
                    (
                        node
                        for node in details
                        if has_class(node, "faq-answer")
                    ),
                    None,
                )
                if summary is not None and answer is not None:
                    items.append(
                        {
                            "question": text_of(summary),
                            "answer": inner_html(answer),
                        }
                    )
            if items:
                heading = next(child.iter("h2"), None)
                blocks.append(
                    {
                        "type": "faq",
                        "value": {
                            "heading": text_of(heading)
                            if heading is not None
                            else "Frequently asked questions",
                            "items": items,
                            "open_first": False,
                            "layout": {
                                **LAYOUT,
                                "top_spacing": "lg",
                                "bottom_spacing": "lg",
                            },
                        },
                    }
                )
            continue

        if child.tag == "section" and has_class(child, "article-cta"):
            heading = next(child.iter("h2"), None)
            paragraph = next(child.iter("p"), None)
            buttons = [
                button
                for link in child.iter("a")
                if (button := button_value(link)) is not None
            ]
            if heading is not None and buttons:
                blocks.append(
                    {
                        "type": "cta",
                        "value": {
                            "eyebrow": "Next step",
                            "heading": text_of(heading),
                            "text": text_of(paragraph) if paragraph is not None else "",
                            "buttons": buttons[:3],
                            "layout": {
                                **LAYOUT,
                                "theme": "accent",
                                "top_spacing": "lg",
                                "bottom_spacing": "lg",
                            },
                        },
                    }
                )
            continue

        if child.tag == "aside" and has_class(child, "deep-dive-cta"):
            blocks.append(
                {
                    "type": "advanced_html",
                    "value": etree.tostring(
                        child,
                        encoding="unicode",
                        method="html",
                    ),
                }
            )
            continue

        if child.tag == "section":
            heading = next(
                (
                    node
                    for node in child
                    if node.tag in {"h1", "h2", "h3", "h4"}
                ),
                None,
            )
            heading_text = text_of(heading) if heading is not None else ""
            body = inner_html(child, skip_first_heading=heading is not None)
            if heading_text or body:
                blocks.append(
                    {
                        "type": "text",
                        "value": {
                            "eyebrow": "",
                            "heading": heading_text,
                            "body": body,
                            "buttons": [],
                            "layout": LAYOUT.copy(),
                        },
                    }
                )
            continue

        serialized = etree.tostring(
            child,
            encoding="unicode",
            method="html",
        )
        if text_of(child):
            blocks.append({"type": "advanced_html", "value": serialized})

    flush_accordion()
    return blocks


def parse_generic_main(main: etree._Element) -> list[dict]:
    blocks = []
    for child in list(main):
        if not isinstance(child.tag, str):
            continue
        if has_class(child, "page-hero"):
            continue
        blocks.append(
            {
                "type": "advanced_html",
                "value": etree.tostring(
                    child,
                    encoding="unicode",
                    method="html",
                ),
            }
        )
    return blocks


def classify(relative: str) -> tuple[str, str | None]:
    parts = Path(relative).parts
    if relative == "index.html":
        return "home", None
    if relative in {
        "conditions/index.html",
        "treatments/index.html",
        "blog/index.html",
    }:
        return "index", None
    if len(parts) == 3 and parts[0] == "treatments":
        return "treatment", "/treatments/"
    if len(parts) == 3 and parts[0] == "blog":
        return "blog", "/blog/"
    if len(parts) == 3 and parts[0] == "locations":
        return "clinic", "/locations/"
    if relative == "dr-cheena-langer/index.html":
        return "doctor", "/"
    return "standard", "/"


def record_for(path: Path, source: Path) -> dict:
    document = html.fromstring(path.read_bytes())
    relative = path.relative_to(source).as_posix()
    fallback = "/" if relative == "index.html" else "/" + relative.removesuffix("index.html")
    route = canonical_path(document, fallback)
    page_type, parent = classify(relative)
    h1 = next(document.iter("h1"), None)
    title = text_of(h1) if h1 is not None else (
        next(document.iter("title"), etree.Element("title")).text or route
    )
    title = re.sub(r"\s*\|\s*Aastha.*$", "", title).strip()
    eyebrow_node = next(
        (
            node
            for node in document.iter()
            if has_class(node, "eyebrow")
        ),
        None,
    )
    intro_node = next(
        (
            node
            for node in document.iter("p")
            if has_class(node, "lead")
        ),
        None,
    )
    article = next(
        (
            node
            for node in document.iter("article")
            if has_class(node, "article-stack")
        ),
        None,
    )
    main = next(
        (
            node
            for node in document.iter("main")
            if node.get("id") == "main-content"
        ),
        None,
    )
    blocks = (
        parse_article(article)
        if article is not None
        else parse_generic_main(main)
        if main is not None
        else []
    )
    return {
        "path": route,
        "parent_path": parent,
        "page_type": page_type,
        "title": title,
        "slug": route.rstrip("/").split("/")[-1] if route != "/" else "home",
        "seo_title": (
            next(document.iter("title"), etree.Element("title")).text or title
        ).strip(),
        "search_description": meta_content(document, "description"),
        "eyebrow": text_of(eyebrow_node) if eyebrow_node is not None else "",
        "introduction": text_of(intro_node) if intro_node is not None else "",
        "body": blocks,
        "show_consultation_sidebar": article is not None,
        "show_clinic_choices": page_type == "treatment",
        "show_medical_disclaimer": page_type in {"treatment", "blog"},
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--source", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()
    source = args.source.resolve()
    records = []
    for path in sorted(source.rglob("*.html")):
        relative_parts = path.relative_to(source).parts
        if any(part in {"dist", "post-template", "reports"} for part in relative_parts):
            continue
        if path.name == "404.html":
            continue
        records.append(record_for(path, source))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        json.dumps(records, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    print(f"Exported {len(records)} pages to {args.output}")
    print(f"Structured blocks: {sum(len(record['body']) for record in records)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
