#!/usr/bin/env python3
"""Repair verified malformed list items in the exact-page snapshot bundle."""

from __future__ import annotations

import base64
import gzip
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "seed_data" / "exact-pages.json.gz.b64"


def replace_once(source: str, old: str, new: str, *, path: str) -> str:
    count = source.count(old)
    if count != 1:
        raise RuntimeError(f"{path}: expected one repair target, found {count}")
    return source.replace(old, new, 1)


def main() -> int:
    compressed = base64.b64decode(BUNDLE.read_text("ascii"))
    bundle = json.loads(gzip.decompress(compressed).decode("utf-8"))
    pages = bundle["pages"]

    acne_path = "/treatments/acne-scar-treatment/"
    acne = pages[acne_path]["html"]
    acne = replace_once(
        acne,
        "<li>Dark marks and textural scars are present together</li></ul><p>The patient has a history of keloids</p>\n<p>Active acne is still recurring</p>",
        "<li>Dark marks and textural scars are present together</li><li>The patient has a history of keloids</li><li>Active acne is still recurring</li></ul>",
        path=acne_path,
    )
    pages[acne_path]["html"] = acne
    pages[acne_path]["sha256"] = hashlib.sha256(acne.encode("utf-8")).hexdigest()

    rf_path = "/treatments/rf-skin-tightening/"
    rf = pages[rf_path]["html"]
    rf = replace_once(
        rf,
        "</ul><p>Uses focused ultrasound energy</p>\n<ul class=\"clean-list\"><li>Delivers energy to planned focal depths</li>",
        "</ul><ul class=\"clean-list\"><li>Uses focused ultrasound energy</li><li>Delivers energy to planned focal depths</li>",
        path=rf_path,
    )
    pages[rf_path]["html"] = rf
    pages[rf_path]["sha256"] = hashlib.sha256(rf.encode("utf-8")).hexdigest()

    payload = json.dumps(bundle, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    BUNDLE.write_text(base64.b64encode(gzip.compress(payload, compresslevel=9, mtime=0)).decode("ascii"), encoding="ascii")
    print("Repaired 3 malformed list items across 2 exact pages.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
