#!/usr/bin/env python3
"""Build transparent responsive WebP variants for the site visual-cue system.

The repository stores two detailed 256 px source icons and two compact 128 px
source strips. Render builds expand those sources into the 30 independently
cacheable 128/256/512 px files referenced by the Django asset manifest.
"""

from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "home" / "static_src" / "visual-cues"
OUTPUT_DIR = ROOT / "home" / "static" / "images" / "visual-cues"
SIZES = (128, 256, 512)

STANDALONE_SOURCES = {
    "acne-care": "acne-care-256.webp",
    "advanced-laser-care": "advanced-laser-care-256.webp",
}

SPRITE_SOURCES = {
    "group-a-128.webp": (
        "clinical-skin-care",
        "complete-care",
        "dermatologist-diagnosis",
        "hair-scalp-care",
    ),
    "group-b-128.webp": (
        "medical-experience",
        "personalised-plan",
        "pigmentation-care",
        "two-clinic-locations",
    ),
}


def _rgba_image(path: Path) -> Image.Image:
    if not path.is_file():
        raise FileNotFoundError(f"Missing visual-cue source asset: {path}")
    with Image.open(path) as image:
        return image.convert("RGBA")


def _source_icons() -> dict[str, Image.Image]:
    icons: dict[str, Image.Image] = {}

    for slug, filename in STANDALONE_SOURCES.items():
        image = _rgba_image(SOURCE_DIR / filename)
        if image.size != (256, 256):
            raise ValueError(
                f"{filename} must be 256x256, received {image.width}x{image.height}"
            )
        icons[slug] = image

    for filename, slugs in SPRITE_SOURCES.items():
        strip = _rgba_image(SOURCE_DIR / filename)
        expected = (128 * len(slugs), 128)
        if strip.size != expected:
            raise ValueError(
                f"{filename} must be {expected[0]}x{expected[1]}, "
                f"received {strip.width}x{strip.height}"
            )
        for index, slug in enumerate(slugs):
            left = index * 128
            icons[slug] = strip.crop((left, 0, left + 128, 128))

    if len(icons) != 10:
        raise RuntimeError(f"Expected 10 visual cues, built {len(icons)}")
    return icons


def _webp_bytes(image: Image.Image) -> bytes:
    buffer = BytesIO()
    image.save(
        buffer,
        format="WEBP",
        lossless=True,
        method=6,
        exact=True,
    )
    return buffer.getvalue()


def _write_if_changed(path: Path, data: bytes) -> bool:
    if path.is_file() and path.read_bytes() == data:
        return False
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    return True


def build_assets() -> list[Path]:
    """Generate every responsive icon variant and return changed paths."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    expected_names: set[str] = set()
    changed: list[Path] = []

    for slug, source in sorted(_source_icons().items()):
        for size in SIZES:
            expected_names.add(f"{slug}-{size}.webp")
            rendered = (
                source.copy()
                if source.size == (size, size)
                else source.resize((size, size), Image.Resampling.LANCZOS)
            )
            output = OUTPUT_DIR / f"{slug}-{size}.webp"
            if _write_if_changed(output, _webp_bytes(rendered)):
                changed.append(output)

    for stale in OUTPUT_DIR.glob("*.webp"):
        if stale.name not in expected_names:
            stale.unlink()
            changed.append(stale)

    return changed


def main() -> int:
    changed = build_assets()
    status = f"generated {len(changed)} changed file(s)" if changed else "already current"
    print(f"Visual cue assets: {status} in {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
