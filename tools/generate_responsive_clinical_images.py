#!/usr/bin/env python3
"""Generate build-time responsive variants for clinical-result photographs.

The approved 1200px WebP originals remain the durable source assets committed to
the repository. This build step creates smaller deterministic WebP candidates
before ``collectstatic`` so browsers can choose an appropriately sized file via
``srcset`` without changing clinical content or contacting Google Drive.
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from PIL import Image, ImageOps

from home.clinical_results import CLINICAL_RESULT_GALLERIES


STATIC_ROOT = ROOT / "home" / "static"
OUTPUT = ROOT / "audit-artifacts" / "responsive-clinical-images.json"
TARGET_WIDTHS = (480, 768)
QUALITY_BY_WIDTH = {480: 76, 768: 80}


def original_asset_path(route: str, index: int) -> Path:
    slug = route.strip("/").split("/")[-1]
    return (
        STATIC_ROOT
        / "images"
        / "clinical-results"
        / slug
        / f"{slug}-{index:02d}.webp"
    )


def variant_asset_path(source: Path, width: int) -> Path:
    return source.with_name(f"{source.stem}-{width}w.webp")


def _normalise(image: Image.Image) -> Image.Image:
    normalised = ImageOps.exif_transpose(image)
    if normalised.mode == "RGBA":
        background = Image.new("RGB", normalised.size, "white")
        background.paste(normalised, mask=normalised.getchannel("A"))
        return background
    return normalised.convert("RGB")


def generate_variant(source: Path, destination: Path, width: int) -> dict:
    if width <= 0:
        raise ValueError("Responsive image width must be positive")

    with Image.open(source) as opened:
        image = _normalise(opened)
        if image.width < width:
            raise ValueError(
                f"{source} is only {image.width}px wide; cannot generate {width}w"
            )
        height = max(1, round(image.height * width / image.width))
        resized = image.resize((width, height), Image.Resampling.LANCZOS)
        destination.parent.mkdir(parents=True, exist_ok=True)
        resized.save(
            destination,
            "WEBP",
            quality=QUALITY_BY_WIDTH.get(width, 80),
            method=4,
            optimize=True,
        )

    payload = destination.read_bytes()
    return {
        "source": source.relative_to(ROOT).as_posix(),
        "path": destination.relative_to(ROOT).as_posix(),
        "width": width,
        "height": height,
        "bytes": len(payload),
        "sha256": hashlib.sha256(payload).hexdigest(),
    }


def main() -> int:
    records: list[dict] = []
    failures: list[str] = []

    for route, gallery in sorted(CLINICAL_RESULT_GALLERIES.items()):
        for index in range(1, len(gallery["images"]) + 1):
            source = original_asset_path(route, index)
            if not source.is_file():
                failures.append(f"Missing clinical source image: {source}")
                continue

            source_bytes = source.stat().st_size
            for width in TARGET_WIDTHS:
                destination = variant_asset_path(source, width)
                try:
                    record = generate_variant(source, destination, width)
                except Exception as error:
                    failures.append(f"{destination}: {error}")
                    continue
                record.update(
                    {
                        "route": route,
                        "index": index,
                        "source_bytes": source_bytes,
                        "saving_bytes": max(0, source_bytes - record["bytes"]),
                    }
                )
                records.append(record)

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            {
                "source_images": sum(
                    len(gallery["images"])
                    for gallery in CLINICAL_RESULT_GALLERIES.values()
                ),
                "target_widths": list(TARGET_WIDTHS),
                "generated": len(records),
                "failures": failures,
                "records": records,
            },
            indent=2,
        ),
        encoding="utf-8",
    )

    expected = sum(
        len(gallery["images"]) for gallery in CLINICAL_RESULT_GALLERIES.values()
    ) * len(TARGET_WIDTHS)
    print(
        f"Responsive clinical images: generated {len(records)}/{expected} variants."
    )
    for failure in failures:
        print(f"- {failure}", file=sys.stderr)
    return 1 if failures or len(records) != expected else 0


if __name__ == "__main__":
    raise SystemExit(main())
