#!/usr/bin/env python3
"""Audit all exact-page snapshots for malformed or visually incomplete lists."""

from __future__ import annotations

import base64
import gzip
import json
import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Tag

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "seed_data" / "exact-pages.json.gz.b64"
OUTPUT = ROOT / "audit-artifacts" / "content-list-quality"
BOUNDARY_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "details", "hr", "section", "article"}


def load_pages() -> dict[str, dict]:
    compressed = base64.b64decode(BUNDLE.read_text("ascii"))
    return json.loads(gzip.decompress(compressed).decode("utf-8"))["pages"]


def clean_text(node: Tag) -> str:
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()


def following_paragraphs(list_node: Tag) -> list[Tag]:
    paragraphs: list[Tag] = []
    sibling = list_node.next_sibling
    while sibling is not None:
        if isinstance(sibling, Tag):
            if sibling.name in BOUNDARY_TAGS or sibling.name in {"ul", "ol"}:
                break
            if sibling.name == "p" and clean_text(sibling):
                paragraphs.append(sibling)
            elif sibling.name not in {"div", "span", "br"} and clean_text(sibling):
                break
        sibling = sibling.next_sibling
    return paragraphs


def looks_like_orphaned_list_item(text: str) -> bool:
    """Short item-like copy without sentence punctuation should be an LI."""
    text = text.strip()
    return bool(text) and len(text) <= 160 and not re.search(r"[.!?]", text)


def main() -> int:
    pages = load_pages()
    report = {
        "pages_checked": len(pages),
        "orphan_text_inside_lists": [],
        "visually_orphaned_list_items": [],
        "empty_list_items": [],
        "duplicate_adjacent_items": [],
    }

    for path, record in sorted(pages.items()):
        soup = BeautifulSoup(record["html"], "html.parser")
        for list_node in soup.find_all(["ul", "ol"]):
            items = list_node.find_all("li", recursive=False)
            for item in items:
                if not clean_text(item):
                    report["empty_list_items"].append({"path": path, "list_html": str(list_node)})

            normalized = [clean_text(item).casefold() for item in items if clean_text(item)]
            for left, right in zip(normalized, normalized[1:]):
                if left == right:
                    report["duplicate_adjacent_items"].append({"path": path, "item": left})

            orphan_chunks = []
            for child in list_node.children:
                if isinstance(child, str):
                    text = re.sub(r"\s+", " ", child).strip()
                    if text:
                        orphan_chunks.append(text)
                elif isinstance(child, Tag) and child.name != "li" and clean_text(child):
                    orphan_chunks.append(str(child))
            if orphan_chunks:
                report["orphan_text_inside_lists"].append(
                    {"path": path, "chunks": orphan_chunks, "list_html": str(list_node)}
                )

            for paragraph in following_paragraphs(list_node):
                text = clean_text(paragraph)
                if looks_like_orphaned_list_item(text):
                    report["visually_orphaned_list_items"].append(
                        {
                            "path": path,
                            "text": text,
                            "list_items": [clean_text(item) for item in items],
                            "context_html": str(list_node.parent)[:12000],
                        }
                    )

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "report.json").write_text(
        json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    lines = [
        "# Exact-page list quality audit",
        "",
        f"- Pages checked: {report['pages_checked']}",
        f"- Visually orphaned list items: {len(report['visually_orphaned_list_items'])}",
        f"- Orphan text inside lists: {len(report['orphan_text_inside_lists'])}",
        f"- Empty list items: {len(report['empty_list_items'])}",
        f"- Adjacent duplicate items: {len(report['duplicate_adjacent_items'])}",
    ]
    for issue in report["visually_orphaned_list_items"]:
        lines.extend(["", f"- `{issue['path']}`: {issue['text']}"])
    (OUTPUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    failures = sum(
        len(report[key])
        for key in (
            "visually_orphaned_list_items",
            "orphan_text_inside_lists",
            "empty_list_items",
            "duplicate_adjacent_items",
        )
    )
    print(f"Content list audit: {len(pages)} pages checked; {failures} defects.")
    if failures:
        for issue in report["visually_orphaned_list_items"]:
            print(f"- {issue['path']}: orphaned list item: {issue['text']}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
