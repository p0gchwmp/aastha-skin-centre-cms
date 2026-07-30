#!/usr/bin/env python3
"""Extract the verified static site's complete <main> elements.

The snapshots are trusted, first-party HTML. They are imported into editable
Wagtail snippets by migration 0005 and used as the public parity layer. The
ordinary StreamField content remains available as a structured fallback.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
import shutil
import xml.etree.ElementTree as ET
from pathlib import Path
from urllib.parse import urlsplit


MAIN_PATTERN = re.compile(r"(<main\b.*?</main>)", re.IGNORECASE | re.DOTALL)


def normalise_path(value: str) -> str:
    path = urlsplit(value).path or "/"
    if path != "/" and not path.endswith("/"):
        path += "/"
    return path


def source_file(source_root: Path, path: str) -> Path:
    if path == "/":
        return source_root / "index.html"
    return source_root / path.strip("/") / "index.html"


def snapshot_file(output_root: Path, path: str) -> Path:
    if path == "/":
        return output_root / "__home__.html"
    return output_root / path.strip("/") / "index.html"


def build(source_root: Path, output_root: Path, bundle_path: Path) -> dict:
    sitemap = ET.fromstring((source_root / "sitemap.xml").read_text("utf-8"))
    paths = sorted(
        {
            normalise_path(node.text or "")
            for node in sitemap.findall(".//{*}loc")
        }
    )

    if output_root.exists():
        shutil.rmtree(output_root)
    output_root.mkdir(parents=True)

    manifest = {"version": 1, "source": "verified static v28", "pages": {}}
    bundle = {"version": 1, "source": "verified static v28", "pages": {}}
    for path in paths:
        source_path = source_file(source_root, path)
        if not source_path.exists():
            raise FileNotFoundError(f"Missing static source for {path}: {source_path}")
        source = source_path.read_text("utf-8")
        match = MAIN_PATTERN.search(source)
        if match is None:
            raise ValueError(f"No <main> element found in {source_path}")
        main_html = match.group(1).strip() + "\n"
        target = snapshot_file(output_root, path)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(main_html, "utf-8")
        manifest["pages"][path] = {
            "file": target.relative_to(output_root).as_posix(),
            "sha256": hashlib.sha256(main_html.encode("utf-8")).hexdigest(),
            "bytes": len(main_html.encode("utf-8")),
        }
        bundle["pages"][path] = {
            "html": main_html,
            "sha256": manifest["pages"][path]["sha256"],
        }

    (output_root / "manifest.json").write_text(
        json.dumps(manifest, indent=2) + "\n",
        "utf-8",
    )
    compressed = gzip.compress(
        json.dumps(bundle, separators=(",", ":")).encode("utf-8"),
        compresslevel=9,
        mtime=0,
    )
    bundle_path.parent.mkdir(parents=True, exist_ok=True)
    bundle_path.write_text(
        base64.b64encode(compressed).decode("ascii") + "\n",
        "ascii",
    )
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source_root", type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("seed_data/exact_pages"),
    )
    parser.add_argument(
        "--bundle",
        type=Path,
        default=Path("seed_data/exact-pages.json.gz.b64"),
    )
    arguments = parser.parse_args()
    manifest = build(
        arguments.source_root.resolve(),
        arguments.output.resolve(),
        arguments.bundle.resolve(),
    )
    total_bytes = sum(page["bytes"] for page in manifest["pages"].values())
    print(
        f"Created {len(manifest['pages'])} exact page snapshots "
        f"({total_bytes:,} bytes)."
    )


if __name__ == "__main__":
    main()
