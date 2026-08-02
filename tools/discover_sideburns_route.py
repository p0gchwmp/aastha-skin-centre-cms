#!/usr/bin/env python3
"""Find the live route containing the Sideburns-to-Toes component.

Routes come from the repository's canonical 75-page snapshot bundle. The scan
uses live HTML first, then reports ranked token matches so no route is guessed.
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
            ranked.append(
                {
                    "route": route,
                    "url": url,
                    "status": status,
                    "score": len(matches),
                    "matches": matches,
                    "source_contains_sideburns": "sideburns" in source_folded,
                    "visible_contains_sideburns": "sideburns" in visible_folded,
                }
            )
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
    report = {
        "tokens": TOKENS,
        "best": ranked[:15],
        "exact": [item for item in ranked if int(item["score"]) == len(TOKENS)],
    }
    args.output.write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))

    if not ranked or int(ranked[0]["score"]) == 0:
        raise SystemExit("No live route contained any reported label.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
