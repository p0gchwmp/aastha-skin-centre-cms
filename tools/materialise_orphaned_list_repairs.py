#!/usr/bin/env python3
"""Convert high-confidence orphaned list paragraphs into proper list items."""

from __future__ import annotations

import base64
import gzip
import hashlib
import html
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "seed_data" / "exact-pages.json.gz.b64"
LIST_THEN_PARAGRAPH = re.compile(
    r'(?P<list><ul class="clean-list">.*?</ul>)(?P<gap>\s*)'
    r'<p(?P<attrs>[^>]*)>(?P<text>[^<]+)</p>',
    re.DOTALL,
)
NEXT_LIST = re.compile(r'(?P<gap>\s*)(?P<open><ul class="clean-list">)')


def item_like(text: str) -> bool:
    value = re.sub(r"\s+", " ", html.unescape(text)).strip()
    return bool(value) and len(value) <= 160 and not re.search(r"[.!?:]", value)


def repair_page(source: str) -> tuple[str, list[str]]:
    repaired: list[str] = []
    while True:
        match = LIST_THEN_PARAGRAPH.search(source)
        changed = False
        while match:
            text_html = match.group("text")
            text = re.sub(r"\s+", " ", html.unescape(text_html)).strip()
            attrs = match.group("attrs") or ""
            if "list-lead" not in attrs and item_like(text):
                remainder = source[match.end():]
                next_list = NEXT_LIST.match(remainder)
                if next_list:
                    replacement = (
                        match.group("list")
                        + match.group("gap")
                        + next_list.group("gap")
                        + next_list.group("open")
                        + f"<li>{text_html}</li>"
                    )
                    source = source[:match.start()] + replacement + source[match.end() + next_list.end():]
                else:
                    list_html = match.group("list")
                    replacement = (
                        list_html[:-5]
                        + f"<li>{text_html}</li></ul>"
                    )
                    source = source[:match.start()] + replacement + source[match.end():]
                repaired.append(text)
                changed = True
                break
            match = LIST_THEN_PARAGRAPH.search(source, match.end())
        if not changed:
            break

    dangling = '<p class="list-lead">A dermatologist may consider:</p>'
    if dangling in source:
        source = source.replace(dangling, "", 1)
        repaired.append("Removed dangling list lead: A dermatologist may consider:")
    return source, repaired


def main() -> int:
    compressed = base64.b64decode(BUNDLE.read_text("ascii"))
    bundle = json.loads(gzip.decompress(compressed).decode("utf-8"))
    total: list[tuple[str, str]] = []
    for path, record in bundle["pages"].items():
        source, repaired = repair_page(record["html"])
        if repaired:
            record["html"] = source
            record["sha256"] = hashlib.sha256(source.encode("utf-8")).hexdigest()
            total.extend((path, item) for item in repaired)

    payload = json.dumps(bundle, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    BUNDLE.write_text(
        base64.b64encode(gzip.compress(payload, compresslevel=9, mtime=0)).decode("ascii"),
        encoding="ascii",
    )
    print(f"Repaired {len(total)} exact-page list defects.")
    for path, item in total:
        print(f"- {path}: {item}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
