#!/usr/bin/env python3
"""Find and inspect the live route containing the Sideburns-to-Toes component.

Routes come from the repository's canonical 75-page snapshot bundle. The scan
uses live HTML first, then saves the exact server-rendered markup and ancestor
chain around Sideburns so spacing fixes target real wrappers rather than guessed
selectors.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import json
import re
import time
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urljoin
from urllib.request import Request, urlopen

from bs4 import BeautifulSoup, NavigableString, Tag


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "seed_data" / "exact-pages.json.gz.b64"
TOKENS = (
    "Sideburns",
    "Jawline",
    "Neck",
    "Full face",
    "Underarms",
    "Arms",
    "Forearms",
    "Shoulders",
    "Chest",
    "Abdomen",
    "Back",
    "Bikini line",
    "Legs",
    "Thighs",
    "Lower legs",
    "Toes",
)
SPACE = re.compile(r"\s+")
TAG = re.compile(r"<[^>]+>")


def load_routes() -> list[str]:
    raw = base64.b64decode(BUNDLE.read_text("ascii"))
    data = json.loads(gzip.decompress(raw).decode("utf-8"))
    pages = data.get("pages", {})
    if len(pages) != 75:
        raise RuntimeError(f"Expected 75 routes; found {len(pages)}")
    return sorted(pages)


def fetch(url: str, retries: int = 3) -> tuple[int, str]:
    error: Exception | None = None
    for attempt in range(retries):
        request = Request(
            url,
            headers={
                "User-Agent": "AasthaExactMobileQA/1.0",
                "Accept": "text/html,application/xhtml+xml",
            },
        )
        try:
            with urlopen(request, timeout=30) as response:
                return response.status, response.read().decode("utf-8", "replace")
        except (HTTPError, URLError, TimeoutError) as exc:
            error = exc
            if attempt + 1 < retries:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"Could not fetch {url}: {error}")


def normalise_source(source: str) -> str:
    text = TAG.sub(" ", source)
    return SPACE.sub(" ", text).strip()


def describe_tag(tag: Tag) -> dict[str, object]:
    return {
        "tag": tag.name,
        "id": tag.get("id", ""),
        "class": tag.get("class", []),
        "role": tag.get("role", ""),
        "style": tag.get("style", ""),
        "data": {
            key: value
            for key, value in tag.attrs.items()
            if isinstance(key, str) and key.startswith("data-")
        },
        "direct_text": SPACE.sub(
            " ",
            " ".join(
                str(child)
                for child in tag.children
                if isinstance(child, NavigableString)
            ),
        ).strip(),
        "text": SPACE.sub(" ", tag.get_text(" ", strip=True)).strip()[:600],
        "child_tags": [
            {
                "tag": child.name,
                "id": child.get("id", ""),
                "class": child.get("class", []),
                "text": SPACE.sub(" ", child.get_text(" ", strip=True)).strip()[:180],
            }
            for child in tag.find_all(recursive=False)
        ],
    }


def inspect_markup(source: str, output_dir: Path) -> dict[str, object]:
    source_folded = source.casefold()
    index = source_folded.find("sideburns")
    if index < 0:
        return {"error": "Sideburns was not present in source."}

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "laser-hair-reduction-live.html").write_text(
        source,
        encoding="utf-8",
    )
    snippet = source[max(0, index - 5000) : min(len(source), index + 12_000)]
    (output_dir / "sideburns-source-snippet.html").write_text(
        snippet,
        encoding="utf-8",
    )

    soup = BeautifulSoup(source, "html.parser")
    text_nodes = soup.find_all(
        string=lambda value: isinstance(value, str)
        and "sideburns" in value.casefold()
    )
    matches: list[dict[str, object]] = []
    for text_node in text_nodes:
        parent = text_node.parent
        if not isinstance(parent, Tag):
            continue
        ancestors: list[dict[str, object]] = []
        current: Tag | None = parent
        for _ in range(12):
            if current is None:
                break
            ancestors.append(describe_tag(current))
            current = current.parent if isinstance(current.parent, Tag) else None
        matches.append(
            {
                "raw_text": str(text_node),
                "parent_html": str(parent),
                "ancestors": ancestors,
            }
        )

    return {
        "source_index": index,
        "snippet_file": "sideburns-source-snippet.html",
        "full_source_file": "laser-hair-reduction-live.html",
        "text_node_matches": matches,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="https://www.aasthaskincentre.in")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("audit-artifacts/exact-mobile-diagnostic/sideburns-route.json"),
    )
    args = parser.parse_args()
    args.output.parent.mkdir(parents=True, exist_ok=True)

    ranked: list[dict[str, object]] = []
    exact_source: str | None = None
    exact_route: str | None = None
    for index, route in enumerate(load_routes(), start=1):
        url = urljoin(args.base.rstrip("/") + "/", route.lstrip("/"))
        try:
            status, source = fetch(url)
            source_folded = source.casefold()
            visible = normalise_source(source)
            visible_folded = visible.casefold()
            matches = [
                token
                for token in TOKENS
                if token.casefold() in source_folded or token.casefold() in visible_folded
            ]
            score = len(matches)
            ranked.append(
                {
                    "route": route,
                    "url": url,
                    "status": status,
                    "score": score,
                    "matches": matches,
                    "source_contains_sideburns": "sideburns" in source_folded,
                    "visible_contains_sideburns": "sideburns" in visible_folded,
                }
            )
            if score == len(TOKENS) and exact_source is None:
                exact_source = source
                exact_route = route
        except Exception as exc:
            ranked.append(
                {
                    "route": route,
                    "url": url,
                    "status": None,
                    "score": 0,
                    "matches": [],
                    "error": str(exc),
                }
            )
        print(f"[{index:02d}/75] {route}", flush=True)

    ranked.sort(key=lambda item: (-int(item["score"]), str(item["route"])))
    markup = (
        inspect_markup(exact_source, args.output.parent)
        if exact_source is not None
        else {"error": "No exact 16-token route was found."}
    )
    report = {
        "tokens": TOKENS,
        "best": ranked[:15],
        "exact": [item for item in ranked if int(item["score"]) == len(TOKENS)],
        "inspected_route": exact_route,
        "markup": markup,
    }
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

    if not ranked or int(ranked[0]["score"]) == 0:
        raise SystemExit("No live route contained any reported label.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
