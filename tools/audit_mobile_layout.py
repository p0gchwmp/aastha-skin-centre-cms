#!/usr/bin/env python3
"""Audit every public page for narrow-grid and viewport-overflow defects."""

from __future__ import annotations

import argparse
import base64
import gzip
import json
import re
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import sync_playwright


BASE_DIR = Path(__file__).resolve().parents[1]
SNAPSHOT_BUNDLE = BASE_DIR / "seed_data" / "exact-pages.json.gz.b64"
VIEWPORT = {"width": 390, "height": 844}
GRID_SELECTORS = [
    ".concern-grid",
    ".treatment-grid",
    ".treatment-directory",
    ".article-grid",
    ".care-path-grid",
    ".condition-grid",
    ".location-grid",
    ".feature-grid",
    ".featured-map__grid",
    ".journal-grid",
    ".clinic-choice-grid",
    ".contact-action-grid",
    ".value-grid",
    ".process-grid",
    ".hours-grid",
    ".why-grid",
    ".location-pro-grid",
    ".premium-summary-grid",
    ".about-story-grid",
    ".clinic-location-grid",
    ".guide-grid",
    ".cms-card-grid",
    ".hub-link-grid",
    ".directory-grid",
    ".card-grid",
    ".category-grid",
]


def public_paths() -> list[str]:
    compressed = base64.b64decode(SNAPSHOT_BUNDLE.read_text("ascii"))
    bundle = json.loads(gzip.decompress(compressed).decode("utf-8"))
    paths = sorted(bundle.get("pages", {}))
    for extra in ("/locations/",):
        if extra not in paths:
            paths.append(extra)
    return paths


def safe_name(path: str) -> str:
    name = path.strip("/") or "home"
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    total_errors = 0

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        page = browser.new_page(viewport=VIEWPORT, device_scale_factor=1)
        page.set_default_timeout(12_000)

        for path in public_paths():
            url = urljoin(args.site.rstrip("/") + "/", path.lstrip("/"))
            page_result = {"path": path, "url": url, "errors": []}
            try:
                response = page.goto(url, wait_until="domcontentloaded", timeout=30_000)
                if response is None or response.status >= 400:
                    status = response.status if response else "no response"
                    page_result["errors"].append(f"HTTP {status}")
                else:
                    page.add_style_tag(
                        content=(
                            "*,*::before,*::after{animation:none!important;"
                            "transition:none!important;scroll-behavior:auto!important}"
                        )
                    )
                    page.wait_for_timeout(250)
                    findings = page.evaluate(
                        """selectors => {
                          const visible = element => {
                            const style = getComputedStyle(element);
                            const rect = element.getBoundingClientRect();
                            return style.display !== 'none' &&
                              style.visibility !== 'hidden' &&
                              rect.width > 1 && rect.height > 1;
                          };
                          const viewport = document.documentElement.clientWidth;
                          const errors = [];
                          const overflow = document.documentElement.scrollWidth - viewport;
                          if (overflow > 2) {
                            errors.push(`document overflows viewport by ${Math.round(overflow)}px`);
                          }

                          for (const selector of selectors) {
                            document.querySelectorAll(selector).forEach((grid, index) => {
                              if (!visible(grid)) return;
                              const rect = grid.getBoundingClientRect();
                              const style = getComputedStyle(grid);
                              if (rect.left < -2 || rect.right > viewport + 2) {
                                errors.push(`${selector}[${index}] crosses viewport (${Math.round(rect.left)}..${Math.round(rect.right)})`);
                              }

                              let ancestor = grid.parentElement;
                              let comparisonWidth = ancestor?.getBoundingClientRect().width || rect.width;
                              while (ancestor && ancestor !== document.body) {
                                const width = ancestor.getBoundingClientRect().width;
                                if (width > rect.width + 18 && width <= viewport + 4) {
                                  comparisonWidth = width;
                                  break;
                                }
                                ancestor = ancestor.parentElement;
                              }
                              if (comparisonWidth > 0 && rect.width < comparisonWidth * 0.78) {
                                errors.push(`${selector}[${index}] uses only ${Math.round(rect.width)}px of ${Math.round(comparisonWidth)}px available`);
                              }

                              if (style.display === 'grid') {
                                const columns = style.gridTemplateColumns
                                  .trim().split(/\s+/).filter(Boolean).length;
                                if (viewport <= 540 && columns > 1) {
                                  errors.push(`${selector}[${index}] retains ${columns} columns on a phone`);
                                }
                              }

                              [...grid.children].filter(visible).forEach((child, childIndex) => {
                                const childRect = child.getBoundingClientRect();
                                if (childRect.left < -2 || childRect.right > viewport + 2) {
                                  errors.push(`${selector}[${index}] child ${childIndex} crosses viewport`);
                                }
                                if (rect.width > 0 && childRect.width < rect.width * 0.78) {
                                  errors.push(`${selector}[${index}] child ${childIndex} is only ${Math.round(childRect.width)}px within a ${Math.round(rect.width)}px grid`);
                                }
                              });
                            });
                          }
                          return {
                            viewport,
                            documentWidth: document.documentElement.scrollWidth,
                            errors: [...new Set(errors)]
                          };
                        }""",
                        GRID_SELECTORS,
                    )
                    page_result.update(
                        {
                            "viewport_width": findings["viewport"],
                            "document_width": findings["documentWidth"],
                        }
                    )
                    page_result["errors"].extend(findings["errors"])
            except Exception as error:  # Playwright gives useful error text.
                page_result["errors"].append(str(error).splitlines()[0])

            if page_result["errors"]:
                total_errors += len(page_result["errors"])
                page.screenshot(
                    path=args.output / f"{safe_name(path)}--mobile-failure.png",
                    full_page=True,
                )
            results.append(page_result)

        browser.close()

    report = {
        "site": args.site,
        "viewport": VIEWPORT,
        "pages_checked": len(results),
        "pages_failed": sum(bool(result["errors"]) for result in results),
        "error_count": total_errors,
        "results": results,
    }
    (args.output / "mobile-layout-report.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    if total_errors:
        print(
            f"Mobile layout audit failed: {report['pages_failed']}/"
            f"{report['pages_checked']} pages; {total_errors} defects."
        )
        for result in results:
            for error in result["errors"]:
                print(f"- {result['path']}: {error}")
        return 1

    print(
        f"Mobile layout audit passed: {report['pages_checked']} pages at "
        f"{VIEWPORT['width']}px; no narrow grids or viewport overflow."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
