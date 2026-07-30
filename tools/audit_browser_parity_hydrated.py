#!/usr/bin/env python3
"""Run the browser parity audit after hydrating viewport-triggered images.

Real visitors retain native lazy loading. Full-page QA screenshots deliberately
scroll through each page first so the evidence captures the final rendered
layout rather than unloaded placeholders far below the initial viewport.
"""

from __future__ import annotations

from pathlib import Path

import audit_browser_parity as audit
from playwright.sync_api import Page


_original_screenshot = audit.screenshot


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
    page.wait_for_timeout(250)
    return _original_screenshot(page, path)


audit.screenshot = hydrated_screenshot


if __name__ == "__main__":
    raise SystemExit(audit.main())
