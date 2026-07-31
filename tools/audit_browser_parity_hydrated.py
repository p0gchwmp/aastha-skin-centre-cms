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

Decorative message-led artwork is normalised before pixel comparison. This
keeps parity focused on layout, typography, spacing and controls while allowing
the CMS to replace legacy placeholders and enrich compact navigation cards.
The live visual treatment remains covered by mobile-layout, dark-mode and
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

          /* Navigation helpers injected only for the enhanced CMS are removed
             completely before pixel comparison. */
          document.querySelectorAll('[data-visual-injected="true"]').forEach(visual => {
            const card = visual.closest('.visual-cue-card');
            visual.remove();
            card?.classList.remove('visual-cue-card');
          });

          /* Existing placeholders keep their original markup in data attributes.
             Restore it so parity compares the underlying legacy layout rather
             than the deliberately upgraded decorative scene. */
          document.querySelectorAll('.message-visual').forEach(icon => {
            const originalHtml = icon.getAttribute('data-visual-original-html');
            if (originalHtml !== null) {
              icon.innerHTML = originalHtml;
            } else {
              icon.querySelectorAll('.message-visual__svg').forEach(svg => svg.remove());
            }

            [...icon.classList]
              .filter(name => name.startsWith('message-visual'))
              .forEach(name => icon.classList.remove(name));

            const restoreAttribute = (attribute, stored) => {
              const value = icon.getAttribute(stored);
              if (value === null || value === '__clay_missing__') {
                icon.removeAttribute(attribute);
              } else {
                icon.setAttribute(attribute, value);
              }
              icon.removeAttribute(stored);
            };
            restoreAttribute('aria-hidden', 'data-visual-original-aria-hidden');
            restoreAttribute('role', 'data-visual-original-role');
            icon.removeAttribute('data-visual-original-html');
            icon.removeAttribute('data-clay-cue');
          });

          /* Homepage artwork is intentionally larger than the old glyphs. Both
             the CMS and static reference are reduced to the same neutral boxes
             so the audit continues to police all surrounding geometry. */
          document.querySelectorAll(
            '.concern-card .icon-bubble, .trust-item .trust-icon'
          ).forEach(icon => {
            const concern = icon.matches('.concern-card .icon-bubble');
            const size = concern ? '54px' : '42px';
            const radius = concern ? '18px' : '13px';
            const declarations = {
              width: size,
              height: size,
              'min-width': size,
              'max-width': size,
              display: 'grid',
              'place-items': 'center',
              flex: '0 0 auto',
              padding: '0',
              color: 'transparent',
              'font-size': '0',
              'line-height': '0',
              'text-indent': '0',
              background: '#fff7f5',
              'background-image': 'none',
              border: '1px solid rgba(111, 23, 54, .08)',
              'border-radius': radius,
              'box-shadow': 'none',
              filter: 'none',
              transform: 'none',
              transition: 'none',
              overflow: 'hidden'
            };
            Object.entries(declarations).forEach(([name, value]) => {
              icon.style.setProperty(name, value, 'important');
            });
          });
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
            text-indent: 0 !important;
            padding: 0 !important;
            background: #fff7f5 !important;
            background-image: none !important;
            border-color: rgba(111, 23, 54, .08) !important;
            box-shadow: none !important;
            filter: none !important;
            transform: none !important;
            transition: none !important;
          }
          .concern-card .icon-bubble {
            width: 54px !important;
            min-width: 54px !important;
            max-width: 54px !important;
            height: 54px !important;
            border-radius: 18px !important;
          }
          .trust-item .trust-icon {
            width: 42px !important;
            min-width: 42px !important;
            max-width: 42px !important;
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
