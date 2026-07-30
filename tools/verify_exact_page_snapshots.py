#!/usr/bin/env python3
"""Fail the build when an exact-page snapshot is incomplete or corrupted."""

from __future__ import annotations

import base64
import gzip
import hashlib
import json
import re
import sys
from pathlib import Path
from urllib.parse import urlsplit


BASE_DIR = Path(__file__).resolve().parents[1]
SNAPSHOT_BUNDLE = BASE_DIR / "seed_data" / "exact-pages.json.gz.b64"
STATIC_ROOT = BASE_DIR / "home" / "static"
TAG = lambda name: re.compile(
    rf"<{name}\b",
    re.IGNORECASE,
)
ATTRIBUTE_URL = re.compile(
    r"""(?:href|src)=["']([^"'#]+)["']""",
    re.IGNORECASE,
)
ALLOWED_INTERNAL_PATHS = {
    "/appointment-request-received/",
    "/locations/",
    "/search/",
}


def normalise_path(value: str) -> str:
    path = urlsplit(value).path or "/"
    if path != "/" and not path.endswith("/") and "." not in path.rsplit("/", 1)[-1]:
        path += "/"
    return path


def main() -> int:
    errors: list[str] = []
    if not SNAPSHOT_BUNDLE.exists():
        print(f"Missing {SNAPSHOT_BUNDLE}", file=sys.stderr)
        return 1

    compressed = base64.b64decode(SNAPSHOT_BUNDLE.read_text("ascii"))
    bundle = json.loads(gzip.decompress(compressed).decode("utf-8"))
    pages = bundle.get("pages", {})
    if len(pages) != 75:
        errors.append(f"Expected 75 exact pages; found {len(pages)}")

    known_paths = set(pages) | ALLOWED_INTERNAL_PATHS
    for path, record in pages.items():
        source = record["html"]
        source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
        if source_hash != record["sha256"]:
            errors.append(f"{path}: checksum mismatch")
        if len(TAG("main").findall(source)) != 1 or source.lower().count(
            "</main>"
        ) != 1:
            errors.append(f"{path}: expected one complete <main> element")
        if 'id="main-content"' not in source:
            errors.append(f"{path}: main-content landmark is missing")
        if len(TAG("h1").findall(source)) != 1:
            errors.append(f"{path}: expected exactly one H1")
        if len(TAG("details").findall(source)) != len(
            re.findall(r"</details>", source, flags=re.IGNORECASE)
        ):
            errors.append(f"{path}: unbalanced details elements")
        if "data-block-key=" in source:
            errors.append(f"{path}: flattened Wagtail markup leaked into snapshot")
        if "No pages yet" in source:
            errors.append(f"{path}: CMS placeholder leaked into snapshot")

        for raw_url in ATTRIBUTE_URL.findall(source):
            parsed = urlsplit(raw_url)
            if parsed.scheme or raw_url.startswith("//"):
                continue
            target = normalise_path(raw_url)
            if target.startswith("/assets/"):
                asset = STATIC_ROOT / target.removeprefix("/assets/")
                if not asset.exists():
                    errors.append(f"{path}: missing asset {target}")
                continue
            if target.startswith("/") and target not in known_paths:
                errors.append(f"{path}: missing internal route {target}")

    if errors:
        print("Exact-page verification failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    total_bytes = sum(
        len(record["html"].encode("utf-8"))
        for record in pages.values()
    )
    print(
        f"Verified {len(pages)} exact pages, all landmarks, routes and assets "
        f"({total_bytes:,} bytes)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
