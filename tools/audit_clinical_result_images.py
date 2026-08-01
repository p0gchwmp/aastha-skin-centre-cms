#!/usr/bin/env python3
"""Validate every locally materialised clinical-result WebP asset."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PIL import Image

from home.clinical_results import CLINICAL_RESULT_GALLERIES
from home.clinical_results_local import local_asset_path

OUTPUT = ROOT / "audit-artifacts" / "clinical-result-images.json"
STATIC_ROOT = ROOT / "home" / "static"


def check(route: str, index: int) -> dict:
    relative = local_asset_path(route, index)
    path = STATIC_ROOT / relative
    result = {
        "route": route,
        "index": index,
        "relative_path": relative,
        "path": path.relative_to(ROOT).as_posix(),
        "ok": False,
        "errors": [],
    }
    if not path.is_file():
        result["errors"].append("file is missing")
        return result

    payload = path.read_bytes()
    result["bytes"] = len(payload)
    result["sha256"] = hashlib.sha256(payload).hexdigest()
    if len(payload) < 4096:
        result["errors"].append("file is unexpectedly small")

    try:
        with Image.open(path) as image:
            image.verify()
        with Image.open(path) as image:
            result["format"] = image.format
            result["width"], result["height"] = image.size
            if image.format != "WEBP":
                result["errors"].append(f"format is {image.format}, expected WEBP")
            if image.width <= 0 or image.height <= 0:
                result["errors"].append("image has invalid dimensions")
            if max(image.size) > 1200:
                result["errors"].append("longest edge exceeds 1200px")
    except Exception as error:
        result["errors"].append(f"Pillow could not decode image: {error}")

    result["ok"] = not result["errors"]
    return result


def main() -> int:
    results = [
        check(route, index)
        for route, gallery in sorted(CLINICAL_RESULT_GALLERIES.items())
        for index in range(1, len(gallery["images"]) + 1)
    ]
    paths = [result["relative_path"] for result in results]
    duplicates = sorted({path for path in paths if paths.count(path) > 1})
    if duplicates:
        for result in results:
            if result["relative_path"] in duplicates:
                result["ok"] = False
                result["errors"].append("duplicate output path")

    payload = {
        "checked": len(results),
        "passed": sum(result["ok"] for result in results),
        "failed": [result for result in results if not result["ok"]],
        "results": results,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f'Clinical image audit: {payload["passed"]}/{payload["checked"]} '
        "local WebP assets pass."
    )
    if payload["failed"]:
        for failure in payload["failed"]:
            print(
                f'- {failure["relative_path"]}: '
                + "; ".join(failure["errors"]),
                file=sys.stderr,
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
