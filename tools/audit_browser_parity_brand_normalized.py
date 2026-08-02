#!/usr/bin/env python3
"""Run hydrated browser parity with intentional presentation layers neutralized.

The retained static rollback service contains the historical circular ``A``
mark. The CMS intentionally replaces that mark with the logo selected in global
Wagtail settings. Brand-asset rendering, dimensions, accessibility and fallback
behaviour have dedicated tests, while mobile and Lighthouse audits inspect the
real public logo.

The CMS also carries a final editorial-rhythm layer that fixes row gaps in long
clinical lists and improves dark FAQ presentation. The rollback service is kept
immutable, so pixel parity applies that exact committed stylesheet to both DOMs
before capture. Dedicated content-rhythm and dark-mode audits verify that the
real CMS loads the stylesheet and meets its layout and contrast contracts.

All underlying content, landmarks, surrounding geometry, typography,
interactions and destinations remain strictly compared.
"""

from __future__ import annotations

from pathlib import Path

import audit_browser_parity_hydrated as hydrated
from playwright.sync_api import Page


_hydrated_screenshot = hydrated.audit.screenshot
_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_CONTENT_RHYTHM_TEMPLATE = (
    _PROJECT_ROOT
    / "home"
    / "templates"
    / "home"
    / "partials"
    / "content_rhythm_styles.html"
).read_text(encoding="utf-8")
_CONTENT_RHYTHM = (
    _CONTENT_RHYTHM_TEMPLATE.replace("<style>", "", 1)
    .rsplit("</style>", 1)[0]
    .strip()
)


def presentation_normalized_screenshot(page: Page, path: Path) -> tuple[int, int]:
    page.evaluate(
        """
        () => {
          document.querySelectorAll('.brand-mark.brand-mark--image').forEach(mark => {
            mark.classList.remove('brand-mark--image');
            mark.replaceChildren(document.createTextNode('A'));
          });
        }
        """
    )
    page.add_style_tag(content=_CONTENT_RHYTHM)
    page.wait_for_timeout(100)
    return _hydrated_screenshot(page, path)


hydrated.audit.screenshot = presentation_normalized_screenshot


if __name__ == "__main__":
    raise SystemExit(hydrated.audit.main())
