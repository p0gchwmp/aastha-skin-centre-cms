#!/usr/bin/env python3
"""Audit exact-page snapshots for malformed or visually incomplete lists."""

from __future__ import annotations

import base64
import gzip
import json
import re
from pathlib import Path

from bs4 import BeautifulSoup, Tag

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "seed_data" / "exact-pages.json.gz.b64"
OUTPUT = ROOT / "audit-artifacts" / "content-list-quality"
TARGET_PHRASES = (
    "The patient has a history of keloids",
    "Active acne is still recurring",
)
BOUNDARY_TAGS = {"h1", "h2", "h3", "h4", "h5", "h6", "details", "hr", "section", "article"}


def load_pages() -> dict[str, dict]:
    compressed = base64.b64decode(BUNDLE.read_text("ascii"))
    return json.loads(gzip.decompress(compressed).decode("utf-8"))["pages"]


def clean_text(node: Tag) -> str:
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()


def sibling_paragraphs_after_list(ul: Tag) -> list[Tag]:
    paragraphs: list[Tag] = []
    sibling = ul.next_sibling
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


def main() -> int:
    pages = load_pages()
    report = {
        "pages_checked": len(pages),
        "target_phrase_hits": [],
        "orphan_text_inside_lists": [],
        "paragraphs_after_lists": [],
        "empty_list_items": [],
        "duplicate_adjacent_items": [],
    }

    for path, record in sorted(pages.items()):
        source = record["html"]
        soup = BeautifulSoup(source, "html.parser")

        for phrase in TARGET_PHRASES:
            if phrase.lower() in source.lower():
                node = soup.find(string=lambda value: value and phrase.lower() in value.lower())
                report["target_phrase_hits"].append(
                    {
                        "path": path,
                        "phrase": phrase,
                        "parent": node.parent.name if node and node.parent else None,
                        "parent_html": str(node.parent) if node and node.parent else None,
                        "previous_html": str(node.parent.find_previous_sibling()) if node and node.parent and node.parent.find_previous_sibling() else None,
                        "next_html": str(node.parent.find_next_sibling()) if node and node.parent and node.parent.find_next_sibling() else None,
                    }
                )

        for list_node in soup.find_all(["ul", "ol"]):
            items = list_node.find_all("li", recursive=False)
            for item in items:
                if not clean_text(item):
                    report["empty_list_items"].append({"path": path, "list_html": str(list_node)})

            normalized_items = [clean_text(item).casefold() for item in items if clean_text(item)]
            for left, right in zip(normalized_items, normalized_items[1:]):
                if left == right:
                    report["duplicate_adjacent_items"].append(
                        {"path": path, "item": left, "list_html": str(list_node)}
                    )

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

            paragraphs = sibling_paragraphs_after_list(list_node)
            if paragraphs:
                report["paragraphs_after_lists"].append(
                    {
                        "path": path,
                        "list_items": [clean_text(item) for item in items],
                        "following_paragraphs": [clean_text(item) for item in paragraphs],
                        "parent_tag": list_node.parent.name if list_node.parent else None,
                        "parent_class": list_node.parent.get("class", []) if list_node.parent else [],
                        "context_html": str(list_node.parent)[:12000] if list_node.parent else str(list_node),
                    }
                )

    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")

    lines = [
        "# Exact-page list quality audit",
        "",
        f"- Pages checked: {report['pages_checked']}",
        f"- Target phrase hits: {len(report['target_phrase_hits'])}",
        f"- Lists with orphan text: {len(report['orphan_text_inside_lists'])}",
        f"- Lists followed by paragraphs: {len(report['paragraphs_after_lists'])}",
        f"- Empty list items: {len(report['empty_list_items'])}",
        f"- Adjacent duplicate items: {len(report['duplicate_adjacent_items'])}",
        "",
        "## Target phrase hits",
    ]
    for hit in report["target_phrase_hits"]:
        lines.extend(["", f"### `{hit['path']}`", f"- Phrase: {hit['phrase']}", f"- Parent: `{hit['parent']}`", "```html", hit["parent_html"] or "", "```"])
    lines.append("")
    lines.append("## Paragraphs immediately following lists")
    for candidate in report["paragraphs_after_lists"]:
        lines.extend([
            "",
            f"### `{candidate['path']}`",
            f"- List: {' | '.join(candidate['list_items'])}",
            f"- Following: {' | '.join(candidate['following_paragraphs'])}",
        ])
    (OUTPUT / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(
        "Content list audit: "
        f"{len(report['target_phrase_hits'])} target hits, "
        f"{len(report['paragraphs_after_lists'])} list-following paragraph groups, "
        f"{len(report['orphan_text_inside_lists'])} orphan-list groups."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
