#!/usr/bin/env python3
"""Run desktop visual parity plus hydrated mobile interaction checks.

The original static site remains the desktop visual reference. Mobile layouts
are now assessed by ``audit_mobile_layout.py`` against objective usability
requirements instead of pixel-matching known responsive defects in the legacy
site. Mobile navigation, theme and appointment-form interactions remain part
of this audit.

Real visitors retain native lazy loading. Full-page QA screenshots deliberately
scroll through each page first so the evidence captures the final rendered
layout rather than unloaded placeholders far below the initial viewport.

Decorative homepage icon artwork is normalised before pixel comparison. This
keeps parity focused on layout, typography, spacing and controls while allowing
the CMS to replace legacy emoji placeholders with approved production artwork.
The live icon treatment is still covered by mobile-layout, dark-mode and
performance audits.
"""

from __future__ import annotations

from pathlib import Path

import audit_browser_parity as audit
from playwright.sync_api import Page


_original_screenshot = audit.screenshot
_original_test_interactions = audit.test_interactions
_original_viewports = dict(audit.VIEWPORTS)


def hydrated_screenshot(page: Page, path: Path) -> tuple[int, int]:
    page.evaluate(
        """
        async () => {
          document.documentElement.style.scrollBehavior = 'auto';
          const viewport = Math.max(window.innerHeight, 600);
          const bottom = Math.max(
            document.body.scrollHeight,
            document.documentElement.scrollHeight
          );
          for (let position = 0; position <= bottom; position += viewport * 0.8) {
            window.scrollTo(0, position);
            await new Promise(resolve => setTimeout(resolve, 35));
          }
          document.querySelectorAll('img[loading="lazy"]').forEach(image => {
            image.loading = 'eager';
          });
          await Promise.all([...document.images].map(image => {
            if (image.complete) {
              return image.decode ? image.decode().catch(() => undefined) : undefined;
            }
            return new Promise(resolve => {
              image.addEventListener('load', resolve, {once: true});
              image.addEventListener('error', resolve, {once: true});
              setTimeout(resolve, 5000);
            });
          }));
          window.scrollTo(0, 0);
        }
        """
    )
    page.add_style_tag(
        content="""
          .concern-card .icon-bubble,
          .trust-item .trust-icon {
            color: transparent !important;
            font-size: 0 !important;
            line-height: 0 !important;
            background: #fff7f5 !important;
            background-image: none !important;
            border-color: rgba(111, 23, 54, .08) !important;
            box-shadow: none !important;
            filter: none !important;
            transform: none !important;
          }
          .concern-card .icon-bubble {
            width: 54px !important;
            height: 54px !important;
            border-radius: 18px !important;
          }
          .trust-item .trust-icon {
            width: 42px !important;
            height: 42px !important;
            border-radius: 13px !important;
          }
          .concern-card .icon-bubble::before,
          .concern-card .icon-bubble::after,
          .trust-item .trust-icon::before,
          .trust-item .trust-icon::after {
            content: none !important;
            display: none !important;
          }
        """
    )
    page.wait_for_timeout(250)
    return _original_screenshot(page, path)


def mobile_interactions(browser, cms: str) -> list[str]:
    """Temporarily restore the mobile viewport for interaction testing."""
    current = audit.VIEWPORTS
    audit.VIEWPORTS = _original_viewports
    try:
        return _original_test_interactions(browser, cms)
    finally:
        audit.VIEWPORTS = current


audit.screenshot = hydrated_screenshot
audit.test_interactions = mobile_interactions
audit.VIEWPORTS = {"desktop": _original_viewports["desktop"]}


if __name__ == "__main__":
    raise SystemExit(audit.main())
