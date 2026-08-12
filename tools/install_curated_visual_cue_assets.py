#!/usr/bin/env python3
"""Compatibility no-op for the retired two-pass visual-cue installer.

The single approved generator now owns every responsive, transparent output.
This entry point remains temporarily because older build workflows may still
invoke it after the generator. It deliberately leaves those outputs untouched.
"""
from __future__ import annotations

from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "home" / "static" / "images" / "visual-cues"


def install_assets() -> list[Path]:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    return []


def main() -> int:
    changed = install_assets()
    status = (
        f"installed {len(changed)} changed file(s)"
        if changed
        else "already current"
    )
    print(f"Legacy visual cue compatibility step: {status} in {OUTPUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
