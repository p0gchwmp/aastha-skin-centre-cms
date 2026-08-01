#!/usr/bin/env python3
"""Audit every public page for narrow-grid and iOS mobile defects."""

from __future__ import annotations

import argparse
import base64
import gzip
import json
import re
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import Page, sync_playwright


BASE_DIR = Path(__file__).resolve().parents[1]
SNAPSHOT_BUNDLE = BASE_DIR / "seed_data" / "exact-pages.json.gz.b64"
VIEWPORT = {"width": 390, "height": 844}
IOS_USER_AGENT = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 18_6 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/18.6 "
    "Mobile/15E148 Safari/604.1"
)
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
    ".hub-category-grid",
    ".hub-link-grid",
    ".directory-grid",
    ".card-grid",
    ".category-grid",
]
TEXT_CHECKS = [
    {"selector": ".trust-item strong", "max_px": 24},
    {"selector": ".trust-item span:not(.trust-icon)", "max_px": 22},
    {"selector": ".concern-card h3", "max_px": 34},
    {"selector": ".concern-card p", "max_px": 23},
    {"selector": ".concern-card .card-link", "max_px": 24},
    {"selector": ".hub-intro", "max_px": 23},
    {"selector": ".hub-category-heading h2", "max_px": 36},
    {"selector": ".hub-category-heading p", "max_px": 23},
    {"selector": ".hub-link strong", "max_px": 25},
    {"selector": ".hub-link span", "max_px": 22},
]


def public_paths() -> list[str]:
    compressed = base64.b64decode(SNAPSHOT_BUNDLE.read_text("ascii"))
    bundle = json.loads(gzip.decompress(compressed).decode("utf-8"))
    paths = sorted(bundle.get("pages", {}))
    if "/locations/" not in paths:
        paths.append("/locations/")
    return paths


def safe_name(path: str) -> str:
    name = path.strip("/") or "home"
    return re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")


def prime_visual_images(page: Page) -> None:
    """Let the site upgrade placeholders, then load its lazy icon images.

    Lazy images below the first viewport are valid production behaviour. The
    audit explicitly primes them before checking naturalWidth so it can still
    detect a real 404 without reporting untouched below-the-fold images.
    """
    page.wait_for_timeout(350)
    page.evaluate(
        r"""async () => {
          const images = [...document.querySelectorAll('img.message-visual__img')];
          for (const image of images) image.loading = 'eager';
          await Promise.all(images.map(image => {
            if (image.complete) return Promise.resolve();
            return new Promise(resolve => {
              const finish = () => resolve();
              image.addEventListener('load', finish, {once: true});
              image.addEventListener('error', finish, {once: true});
              setTimeout(finish, 1800);
            });
          }));
        }"""
    )
    page.wait_for_timeout(100)


def collect_findings(page: Page) -> dict:
    return page.evaluate(
        r"""config => {
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

          for (const selector of config.gridSelectors) {
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
                const columns = style.gridTemplateColumns.trim().split(/\s+/).filter(Boolean).length;
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

          for (const check of config.textChecks) {
            document.querySelectorAll(check.selector).forEach((element, index) => {
              if (!visible(element)) return;
              const rect = element.getBoundingClientRect();
              const style = getComputedStyle(element);
              const fontSize = Number.parseFloat(style.fontSize);
              const range = document.createRange();
              range.selectNodeContents(element);
              const textRect = range.getBoundingClientRect();
              if (fontSize > check.max_px + .5) {
                errors.push(`${check.selector}[${index}] inflated to ${fontSize.toFixed(1)}px`);
              }
              if (rect.left < -2 || rect.right > viewport + 2) {
                errors.push(`${check.selector}[${index}] box crosses viewport`);
              }
              if (textRect.left < -2 || textRect.right > viewport + 2) {
                errors.push(`${check.selector}[${index}] text crosses viewport`);
              }
              if (element.scrollWidth > element.clientWidth + 2) {
                errors.push(`${check.selector}[${index}] clips ${element.scrollWidth - element.clientWidth}px of text`);
              }
            });
          }

          document.querySelectorAll('.message-visual').forEach((element, index) => {
            if (!visible(element)) return;
            const style = getComputedStyle(element);
            if (style.filter !== 'none') {
              errors.push(`.message-visual[${index}] has container filter ${style.filter}`);
            }
            const image = element.querySelector('img.message-visual__img');
            if (image && (!image.complete || image.naturalWidth < 1)) {
              errors.push(`.message-visual[${index}] image did not load`);
            }
          });

          return {
            viewport,
            documentWidth: document.documentElement.scrollWidth,
            errors: [...new Set(errors)]
          };
        }""",
        {"gridSelectors": GRID_SELECTORS, "textChecks": TEXT_CHECKS},
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument(
        "--engine", choices=("chromium", "webkit"), default="chromium"
    )
    parser.add_argument(
        "--color-scheme", choices=("light", "dark"), default="light"
    )
    args = parser.parse_args()

    args.output.mkdir(parents=True, exist_ok=True)
    results: list[dict] = []
    total_errors = 0

    with sync_playwright() as playwright:
        browser_type = getattr(playwright, args.engine)
        browser = browser_type.launch()
        page_options = {
            "viewport": VIEWPORT,
            "screen": VIEWPORT,
            "device_scale_factor": 3 if args.engine == "webkit" else 1,
            "has_touch": args.engine == "webkit",
            "is_mobile": args.engine == "webkit",
            "color_scheme": args.color_scheme,
        }
        if args.engine == "webkit":
            page_options["user_agent"] = IOS_USER_AGENT
        page = browser.new_page(**page_options)
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
                    prime_visual_images(page)
                    findings = collect_findings(page)
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
                    path=(
                        args.output
                        / f"{safe_name(path)}--{args.engine}-{args.color_scheme}-failure.png"
                    ),
                    full_page=True,
                )
            results.append(page_result)

        browser.close()

    report = {
        "site": args.site,
        "engine": args.engine,
        "color_scheme": args.color_scheme,
        "viewport": VIEWPORT,
        "pages_checked": len(results),
        "pages_failed": sum(bool(result["errors"]) for result in results),
        "error_count": total_errors,
        "results": results,
    }
    (args.output / "mobile-layout-report.json").write_text(
        json.dumps(report, indent=2), encoding="utf-8"
    )

    if total_errors:
        print(
            f"Mobile layout audit failed ({args.engine}/{args.color_scheme}): "
            f"{report['pages_failed']}/{report['pages_checked']} pages; "
            f"{total_errors} defects."
        )
        for result in results:
            for error in result["errors"]:
                print(f"- {result['path']}: {error}")
        return 1

    print(
        f"Mobile layout audit passed: {report['pages_checked']} pages at "
        f"{VIEWPORT['width']}px in {args.engine}/{args.color_scheme}; "
        "no narrow grids, clipped text, icon filtering or viewport overflow."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
