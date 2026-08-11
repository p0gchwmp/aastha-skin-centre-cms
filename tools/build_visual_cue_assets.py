#!/usr/bin/env python3
"""Build the approved 2026 clay artwork into responsive WebP assets.

The source set is kept at its supplied 1024px resolution. Render and local
builds generate the smaller files used by the site so cards never upscale a
thumbnail and browsers never need to download the full source JPEG.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image, ImageOps


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "home" / "static_src" / "visual-cues" / "approved-2026"
OUTPUT_DIR = ROOT / "home" / "static" / "images" / "visual-cues"
SIZES = (64, 128, 256, 512)

# Multiple semantic placements may deliberately share one approved artwork.
APPROVED_SOURCES = {
    "acne-care": "acne-care.jpg",
    "pigmentation-care": "pigmentation-care.jpg",
    "hair-scalp-care": "hair-scalp-care.jpg",
    "fungal-infection-care": "fungal-infection-care.jpg",
    "allergy-inflammatory-rashes": "allergy-inflammatory-rashes.jpg",
    "skin-quality-ageing": "skin-quality-ageing.jpg",
    "dermatologist-diagnosis": "dermatologist-diagnosis.jpg",
    "medical-experience": "medical-experience.jpg",
    "two-clinic-locations": "two-clinic-locations.jpg",
    "complete-care": "complete-care.jpg",
    "advanced-laser-care": "complete-care.jpg",
    "personalised-plan": "personalised-plan.jpg",
    "clinical-skin-care": "clinical-skin-care.jpg",
    "clinic-directions": "clinic-directions.jpg",
    "appointment-booking": "appointment-booking.jpg",
    "theme-dark": "theme-dark.jpg",
    "theme-light": "theme-light.jpg",
}


def _source_image(filename: str) -> Image.Image:
    path = SOURCE_DIR / filename
    if not path.is_file():
        raise FileNotFoundError(f"Missing approved visual-cue source: {path}")
    with Image.open(path) as image:
        source = ImageOps.exif_transpose(image).convert("RGB")
    if source.size != (1024, 1024):
        raise ValueError(
            f"{filename} must be 1024x1024, received "
            f"{source.width}x{source.height}"
        )
    return source


def _webp_bytes(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(
        buffer,
        format="WEBP",
        quality=92,
        method=6,
    )
    return buffer.getvalue()


def _write_if_changed(path: Path, data: bytes) -> bool:
    if path.is_file() and path.read_bytes() == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return True


def build_assets() -> list[Path]:
    """Generate the responsive approved set and return changed paths."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    expected_names: set[str] = set()
    changed: list[Path] = []
    source_cache: dict[str, Image.Image] = {}

    for slug, filename in sorted(APPROVED_SOURCES.items()):
        if filename not in source_cache:
            source_cache[filename] = _source_image(filename)
        source = source_cache[filename]
        for size in SIZES:
            expected_names.add(f"{slug}-{size}.webp")
            rendered = source.resize((size, size), Image.Resampling.LANCZOS)
            output = OUTPUT_DIR / f"{slug}-{size}.webp"
            if _write_if_changed(output, _webp_bytes(rendered)):
                changed.append(output)

    # Specialist transparent cues are restored immediately afterwards by
    # install_curated_visual_cue_assets.py.
    for stale in OUTPUT_DIR.glob("*.webp"):
        if stale.name not in expected_names:
            stale.unlink()
            changed.append(stale)

    return changed


def main() -> int:
    changed = build_assets()
    status = (
        f"generated {len(changed)} changed file(s)"
        if changed
        else "already current"
    )
    print(f"Approved visual cue assets: {status} in {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
