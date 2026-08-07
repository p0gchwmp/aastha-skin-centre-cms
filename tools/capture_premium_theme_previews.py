#!/usr/bin/env python3
"""Capture exact rendered premium-theme previews from the local CMS.

Preview-only QA helper used by PR #66. It does not mutate content or settings.
"""

from __future__ import annotations

import argparse
from pathlib import Path

from playwright.sync_api import sync_playwright


ROUTES = {
    "home": "/",
    "acne-treatment": "/treatments/acne-treatment/",
    "book-appointment": "/book-appointment/",
}

VIEWPORTS = {
    "desktop": {"width": 1440, "height": 1000},
    "mobile": {"width": 430, "height": 932},
}


def capture(base_url: str, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    base_url = base_url.rstrip("/")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        for device_name, viewport in VIEWPORTS.items():
            for theme in ("light", "dark"):
                context = browser.new_context(
                    viewport=viewport,
                    color_scheme=theme,
                    device_scale_factor=1,
                    reduced_motion="reduce",
                )
                context.add_init_script(
                    script=(
                        "localStorage.setItem('aastha-theme', " + repr(theme) + ");"
                        "document.documentElement.dataset.theme = " + repr(theme) + ";"
                    )
                )
                page = context.new_page()
                for label, route in ROUTES.items():
                    page.goto(f"{base_url}{route}", wait_until="networkidle", timeout=60000)
                    page.evaluate(
                        "theme => {"
                        " localStorage.setItem('aastha-theme', theme);"
                        " document.documentElement.dataset.theme = theme;"
                        "}",
                        theme,
                    )
                    page.wait_for_timeout(700)
                    page.screenshot(
                        path=str(output / f"{label}--{device_name}--{theme}.png"),
                        full_page=True,
                        animations="disabled",
                    )
                context.close()
        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", default="audit-artifacts/premium-v4-preview")
    args = parser.parse_args()
    capture(args.base_url, Path(args.output))
