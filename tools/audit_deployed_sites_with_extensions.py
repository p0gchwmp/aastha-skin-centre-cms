#!/usr/bin/env python3
"""Run the legacy parity audit while excluding approved additive extensions.

The retained static site does not contain the route-specific clinical result
section. This wrapper removes only that explicitly named extension from the CMS
DOM before delegating to the existing strict 75-route audit. All inherited page
content, headings, disclosures, forms, metadata and destinations remain covered
by the original audit implementation.
"""

from __future__ import annotations

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


def without_approved_extensions(main: Tag) -> Tag:
    clone = BeautifulSoup(str(main), "lxml").find("main")
    if clone is None:
        return main

    for extension in clone.select(".clinical-results"):
        extension.decompose()

    # The gallery currently emits its route-scoped CSS and controller beside
    # the section. Remove only blocks that identify that component by name.
    for node in clone.find_all(["style", "script"]):
        source = node.string or node.get_text()
        if "clinical-results" in source:
            node.decompose()
    return clone


def normalise_main(main: Tag, hosts: set[str]) -> str:
    return _original_normalise_main(without_approved_extensions(main), hosts)


def headings(main: Tag) -> list[tuple[str, str]]:
    return _original_headings(without_approved_extensions(main))


parity.normalise_main = normalise_main
parity.headings = headings


if __name__ == "__main__":
    raise SystemExit(parity.main())
