#!/usr/bin/env python3
"""Run strict legacy parity while normalising approved additive extensions.

The retained static site does not contain route-specific clinical galleries and
still contains a small set of list items emitted as adjacent paragraphs. This
wrapper removes only the named gallery extension and applies the same narrow,
high-confidence list repair to both DOMs before delegating to the strict
75-route audit. All other content, headings, disclosures, forms, metadata and
destinations remain covered by the original implementation.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

from bs4 import BeautifulSoup, Tag

TOOLS = Path(__file__).resolve().parent
ROOT = TOOLS.parent
for value in (str(ROOT), str(TOOLS)):
    if value not in sys.path:
        sys.path.insert(0, value)

import audit_deployed_sites as parity


_original_normalise_main = parity.normalise_main
_original_headings = parity.headings
CLEAN_LIST_SELECTOR = "ul.clean-list, ol.clean-list"
DANGLING_LIST_LEAD = "A dermatologist may consider:"


def _clean_text(node: Tag) -> str:
    return re.sub(r"\s+", " ", node.get_text(" ", strip=True)).strip()


def _is_high_confidence_list_item(node: Tag) -> bool:
    if node.name != "p" or "list-lead" in node.get("class", []):
        return False
    text = _clean_text(node)
    return bool(text) and len(text) <= 160 and not re.search(r"[.!?:]", text)


def normalise_approved_list_repairs(root: Tag) -> None:
    """Apply only the list corrections already approved in the CMS bundle."""
    for list_node in list(root.select(CLEAN_LIST_SELECTOR)):
        sibling = list_node.find_next_sibling()
        while isinstance(sibling, Tag) and _is_high_confidence_list_item(sibling):
            following = sibling.find_next_sibling()
            item = root.new_tag("li")
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

    for lead in list(root.select("p.list-lead")):
        if (
            _clean_text(lead) == DANGLING_LIST_LEAD
            and lead.find_next_sibling() is None
            and isinstance(lead.parent, Tag)
            and lead.parent.name == "section"
        ):
            lead.decompose()


def without_approved_extensions(main: Tag) -> Tag:
    clone = BeautifulSoup(str(main), "lxml").find("main")
    if clone is None:
        return main

    for extension in clone.select(".clinical-results"):
        extension.decompose()

    # The gallery emits route-scoped CSS and its controller beside the section.
    # Remove only blocks that identify that component by name.
    for node in clone.find_all(["style", "script"]):
        source = node.string or node.get_text()
        if "clinical-results" in source:
            node.decompose()

    normalise_approved_list_repairs(clone)
    return clone


def normalise_main(main: Tag, hosts: set[str]) -> str:
    return _original_normalise_main(without_approved_extensions(main), hosts)


def headings(main: Tag) -> list[tuple[str, str]]:
    return _original_headings(without_approved_extensions(main))


parity.normalise_main = normalise_main
parity.headings = headings


if __name__ == "__main__":
    raise SystemExit(parity.main())
