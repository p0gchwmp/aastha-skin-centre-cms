#!/usr/bin/env python3
"""Run hydrated browser parity with CMS-managed branding neutralized.

The retained static rollback service contains the historical circular ``A``
mark. The CMS intentionally replaces that mark with the logo selected in global
Wagtail settings. Brand-asset rendering, dimensions, accessibility and fallback
behaviour have dedicated tests, while mobile and Lighthouse audits inspect the
real public logo.

For legacy pixel comparison only, this wrapper restores the same ``A`` mark in
both DOMs before the existing hydrated screenshot normalisation runs. All
surrounding header/footer geometry, typography, spacing and interactions remain
strictly compared.
"""

from __future__ import annotations

from pathlib import Path

import audit_browser_parity_hydrated as hydrated
from playwright.sync_api import Page


_hydrated_screenshot = hydrated.audit.screenshot


def brand_normalized_screenshot(page: Page, path: Path) -> tuple[int, int]:
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
    return _hydrated_screenshot(page, path)


hydrated.audit.screenshot = brand_normalized_screenshot


if __name__ == "__main__":
    raise SystemExit(hydrated.audit.main())
