#!/usr/bin/env python3
"""Materialise approved Drive clinical photographs as local optimized WebP assets.

This is an explicit maintenance tool, not a runtime dependency. It downloads
only the file IDs already approved in ``home.clinical_results``, normalises
orientation, bounds the longest edge, and writes deterministic route-specific
filenames under the private repository's static image tree.
"""

from __future__ import annotations

import hashlib
import io
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

import requests
from PIL import Image, ImageOps

from home.clinical_results import (
    CLINICAL_RESULT_GALLERIES,
    drive_fallback_url,
    drive_thumbnail_url,
)

OUTPUT_ROOT = ROOT / "home" / "static" / "images" / "clinical-results"
REPORT = ROOT / "audit-artifacts" / "materialised-clinical-results.json"
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "Chrome/151 Safari/537.36"
    )
}


def download(file_id: str) -> bytes:
    attempts: list[str] = []
    urls = (
        drive_thumbnail_url(file_id).replace("sz=w1200", "sz=w1600"),
        drive_fallback_url(file_id),
    )
    for url in urls:
        for retry in range(3):
            try:
                response = requests.get(
                    url,
                    headers=HEADERS,
                    timeout=45,
                    allow_redirects=True,
                )
                content_type = response.headers.get("content-type", "").lower()
                if response.ok and content_type.startswith("image/") and len(response.content) > 1024:
                    return response.content
                attempts.append(
                    f"{url}: HTTP {response.status_code}, {content_type}, "
                    f"{len(response.content)} bytes"
                )
            except requests.RequestException as error:
                attempts.append(f"{url}: {error}")
            time.sleep(1 + retry)
    raise RuntimeError(
        f"Could not download approved Drive image {file_id}: " + " | ".join(attempts)
    )


def optimise(source: bytes, destination: Path) -> dict:
    with Image.open(io.BytesIO(source)) as opened:
        image = ImageOps.exif_transpose(opened)
        if image.mode not in {"RGB", "RGBA"}:
            image = image.convert("RGB")
        if image.mode == "RGBA":
            background = Image.new("RGB", image.size, "white")
            background.paste(image, mask=image.getchannel("A"))
            image = background
        else:
            image = image.convert("RGB")
        image.thumbnail((1200, 1200), Image.Resampling.LANCZOS)
        destination.parent.mkdir(parents=True, exist_ok=True)
        image.save(destination, "WEBP", quality=84, method=6, optimize=True)
        width, height = image.size

    payload = destination.read_bytes()
    return {
        "path": destination.relative_to(ROOT).as_posix(),
        "width": width,
        "height": height,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def main() -> int:
    records: list[dict] = []
    for route, gallery in sorted(CLINICAL_RESULT_GALLERIES.items()):
        slug = route.strip("/").split("/")[-1]
        for index, image in enumerate(gallery["images"], start=1):
            destination = OUTPUT_ROOT / slug / f"{slug}-{index:02d}.webp"
            source = download(image["id"])
            record = optimise(source, destination)
            record.update(
                {
                    "route": route,
                    "source_file_id": image["id"],
                    "index": index,
                }
            )
            records.append(record)
            print(
                f"Materialised {route} image {index}/{len(gallery['images'])}: "
                f"{record['width']}x{record['height']}, {record['bytes']} bytes"
            )

    REPORT.parent.mkdir(parents=True, exist_ok=True)
    REPORT.write_text(
        json.dumps(
            {
                "routes": len(CLINICAL_RESULT_GALLERIES),
                "images": len(records),
                "records": records,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Materialised {len(records)} clinical images across {len(CLINICAL_RESULT_GALLERIES)} routes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
