#!/usr/bin/env python3
"""Install curated transparent artwork into the responsive visual-cue set.

The base generator restores the original approved core icons. This second pass
replaces only the newer patient-facing specialist categories with curated
miniature dermatology artwork, while retaining the same filenames, responsive
sizes and transparent dark-mode-safe output contract.
"""
from __future__ import annotations

from io import BytesIO
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
SOURCE_DIR = ROOT / "home" / "static" / "images" / "visual-cue-sources"
OUTPUT_DIR = ROOT / "home" / "static" / "images" / "visual-cues"
SIZES = (64, 128, 256, 512)

# Hair deliberately remains in the original approved core set. The curated
# hair source produced the black/glitched artwork reported on iPhone Safari.
CURATED_CUES = {
    "growths": "moles-growths-nails",
    "scars": "scars-texture-skin-quality",
    "children": "childrens-dermatology",
    "dermatosurgery": "minor-dermatosurgery",
}


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


def _load_source(cue: str) -> Image.Image:
    path = SOURCE_DIR / f"{cue}.webp"
    if not path.is_file():
        raise FileNotFoundError(f"Missing curated visual cue source: {path}")

    with Image.open(path) as image:
        source = image.convert("RGBA")

    alpha = source.getchannel("A")
    if alpha.getextrema()[0] != 0 or alpha.getpixel((0, 0)) != 0:
        raise ValueError(f"Curated visual cue must have transparent corners: {path}")

    return source


def install_assets() -> list[Path]:
    changed: list[Path] = []
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    for cue, slug in CURATED_CUES.items():
        source = _load_source(cue)
        for size in SIZES:
            rendered = source.resize((size, size), Image.Resampling.LANCZOS)
            output = OUTPUT_DIR / f"{slug}-{size}.webp"
            if _write_if_changed(output, _webp_bytes(rendered)):
                changed.append(output)

    return changed


def main() -> int:
    changed = install_assets()
    status = (
        f"installed {len(changed)} changed file(s)"
        if changed
        else "already current"
    )
    print(f"Curated visual cue assets: {status} in {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
