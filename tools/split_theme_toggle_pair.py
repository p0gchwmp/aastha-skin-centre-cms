#!/usr/bin/env python3
"""Split the approved generated theme pair into matching square PNG assets."""

from __future__ import annotations

import argparse
from pathlib import Path

from PIL import Image


def _square_asset(image: Image.Image, size: int = 1024) -> Image.Image:
    alpha = image.getchannel("A")
    bounds = alpha.getbbox()
    if bounds is None:
        raise ValueError("Theme asset contains no visible pixels")
    subject = image.crop(bounds)
    available = round(size * 0.86)
    scale = min(available / subject.width, available / subject.height)
    resized = subject.resize(
        (max(1, round(subject.width * scale)), max(1, round(subject.height * scale))),
        Image.Resampling.LANCZOS,
    )
    canvas = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    canvas.alpha_composite(
        resized,
        ((size - resized.width) // 2, (size - resized.height) // 2),
    )
    return canvas


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output_dir", type=Path)
    args = parser.parse_args()

    with Image.open(args.input) as source_file:
        source = source_file.convert("RGBA")
    midpoint = source.width // 2
    left = source.crop((0, 0, midpoint, source.height))
    right = source.crop((midpoint, 0, source.width, source.height))

    args.output_dir.mkdir(parents=True, exist_ok=True)
    _square_asset(left).save(args.output_dir / "theme-dark-v2.png", optimize=True)
    _square_asset(right).save(args.output_dir / "theme-light-v2.png", optimize=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
