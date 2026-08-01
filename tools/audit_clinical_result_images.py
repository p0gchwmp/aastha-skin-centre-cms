#!/usr/bin/env python3
"""Verify that every Drive-backed clinical photograph is publicly renderable."""

from __future__ import annotations

import json
import sys
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

import requests

from home.clinical_results import (
    CLINICAL_RESULT_GALLERIES,
    drive_fallback_url,
    drive_thumbnail_url,
)

OUTPUT = Path("audit-artifacts/clinical-result-images.json")
HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
        "Chrome/151 Safari/537.36"
    )
}


def check(file_id: str) -> dict:
    attempts = []
    for url in (drive_thumbnail_url(file_id), drive_fallback_url(file_id)):
        for retry in range(3):
            try:
                response = requests.get(
                    url,
                    headers=HEADERS,
                    timeout=30,
                    allow_redirects=True,
                    stream=True,
                )
                content_type = response.headers.get("content-type", "")
                first_chunk = next(response.iter_content(16384), b"")
                result = {
                    "url": url,
                    "final_url": response.url,
                    "status": response.status_code,
                    "content_type": content_type,
                    "first_chunk_bytes": len(first_chunk),
                }
                attempts.append(result)
                if (
                    response.ok
                    and content_type.lower().startswith("image/")
                    and len(first_chunk) >= 1024
                ):
                    return {
                        "file_id": file_id,
                        "ok": True,
                        "selected": result,
                        "attempts": attempts,
                    }
            except requests.RequestException as error:
                attempts.append({"url": url, "error": str(error)})
            time.sleep(1 + retry)
    return {"file_id": file_id, "ok": False, "attempts": attempts}


def main() -> int:
    ids = sorted({
        image["id"]
        for gallery in CLINICAL_RESULT_GALLERIES.values()
        for image in gallery["images"]
    })
    results = []
    with ThreadPoolExecutor(max_workers=8) as executor:
        futures = {executor.submit(check, file_id): file_id for file_id in ids}
        for future in as_completed(futures):
            results.append(future.result())
    results.sort(key=lambda item: item["file_id"])

    payload = {
        "checked": len(results),
        "passed": sum(item["ok"] for item in results),
        "failed": [item for item in results if not item["ok"]],
        "results": results,
    }
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    print(
        f'Clinical image audit: {payload["passed"]}/{payload["checked"]} '
        "Drive images are publicly renderable."
    )
    if payload["failed"]:
        for failure in payload["failed"]:
            print(f'- {failure["file_id"]}: not renderable', file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
