#!/usr/bin/env python3
"""Check representative dark-mode text and decorative visual cues."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import Browser, Page, sync_playwright


DEFAULT_CMS = "https://aastha-skin-centre-cms.onrender.com"
TEXT_CHECKS = [
    ("/", ".trust-ribbon .trust-item strong", 4.5),
    ("/", ".trust-ribbon .trust-item span:not(.trust-icon)", 4.5),
    (
        "/book-appointment/",
        ".faq-pro-list summary, .faq-clean-list summary",
        4.5,
    ),
    ("/book-appointment/", ".faq-answer p", 4.5),
]
DECORATIVE_ICON_CHECKS = [
    ("/", ".trust-ribbon .trust-icon.message-visual", 5),
]


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cms", default=DEFAULT_CMS)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("audit-artifacts/dark-readability"),
    )
    return parser.parse_args()


def open_dark_page(browser: Browser, origin: str, route: str) -> Page:
    context = browser.new_context(
        viewport={"width": 1440, "height": 1000},
        color_scheme="dark",
    )
    context.add_init_script("localStorage.setItem('aastha-theme', 'dark');")
    page = context.new_page()
    page.goto(
        urljoin(origin.rstrip("/") + "/", route.lstrip("/")),
        wait_until="networkidle",
        timeout=90_000,
    )
    page.wait_for_selector("main#main-content", timeout=30_000)
    page.wait_for_timeout(500)
    return page


def contrast_records(page: Page, selector: str) -> list[dict[str, object]]:
    return page.locator(selector).evaluate_all(
        r"""
        elements => {
          const parse = value => {
            const match = value.match(/rgba?\(([^)]+)\)/);
            if (!match) return null;
            const parts = match[1].split(',').map(part => Number(part.trim()));
            return {r: parts[0], g: parts[1], b: parts[2], a: parts[3] ?? 1};
          };
          const luminance = colour => {
            const channel = value => {
              const normal = value / 255;
              return normal <= 0.04045
                ? normal / 12.92
                : Math.pow((normal + 0.055) / 1.055, 2.4);
            };
            return 0.2126 * channel(colour.r)
              + 0.7152 * channel(colour.g)
              + 0.0722 * channel(colour.b);
          };
          const contrast = (left, right) => {
            const one = luminance(left);
            const two = luminance(right);
            return (Math.max(one, two) + 0.05) / (Math.min(one, two) + 0.05);
          };
          const backgroundFor = element => {
            let current = element;
            while (current) {
              const parsed = parse(getComputedStyle(current).backgroundColor);
              if (parsed && parsed.a > 0.02) return parsed;
              current = current.parentElement;
            }
            return {r: 15, g: 11, b: 13, a: 1};
          };
          return elements
            .filter(element => {
              const box = element.getBoundingClientRect();
              const style = getComputedStyle(element);
              return box.width > 0
                && box.height > 0
                && style.visibility !== 'hidden';
            })
            .map(element => {
              const foreground = parse(getComputedStyle(element).color);
              const background = backgroundFor(element);
              return {
                text: element.textContent.trim().replace(/\s+/g, ' ').slice(0, 120),
                foreground: getComputedStyle(element).color,
                background: `rgb(${background.r}, ${background.g}, ${background.b})`,
                ratio: foreground ? contrast(foreground, background) : 0,
              };
            });
        }
        """
    )


def decorative_icon_records(
    page: Page,
    selector: str,
) -> list[dict[str, object]]:
    return page.locator(selector).evaluate_all(
        r"""
        elements => elements
          .filter(element => {
            const box = element.getBoundingClientRect();
            const style = getComputedStyle(element);
            return box.width > 0
              && box.height > 0
              && style.visibility !== 'hidden';
          })
          .map(element => {
            const image = element.querySelector('img.message-visual__img');
            const background = getComputedStyle(element).backgroundColor;
            const transparentBackground = background === 'rgba(0, 0, 0, 0)'
              || background === 'transparent';
            const imageBox = image?.getBoundingClientRect();
            return {
              cue: element.dataset.clayCue || '',
              ariaHidden: element.getAttribute('aria-hidden'),
              role: element.getAttribute('role'),
              background,
              transparentBackground,
              imagePresent: Boolean(image),
              imageLoaded: Boolean(image?.complete && image?.naturalWidth > 0),
              imageVisible: Boolean(imageBox?.width > 0 && imageBox?.height > 0),
              imageSource: image?.currentSrc || image?.src || '',
            };
          });
        """
    )


def page_for(
    pages: dict[str, Page],
    browser: Browser,
    origin: str,
    route: str,
    output: Path,
) -> Page:
    page = pages.get(route)
    if page is not None:
        return page

    page = open_dark_page(browser, origin, route)
    pages[route] = page
    slug = "home" if route == "/" else route.strip("/").replace("/", "__")
    page.screenshot(
        path=str(output / f"{slug}--dark.png"),
        full_page=True,
        animations="disabled",
    )
    return page


def main() -> int:
    args = arguments()
    args.output.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    text_results: list[dict[str, object]] = []
    icon_results: list[dict[str, object]] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        pages: dict[str, Page] = {}
        try:
            for route, selector, minimum in TEXT_CHECKS:
                page = page_for(
                    pages,
                    browser,
                    args.cms,
                    route,
                    args.output,
                )
                records = contrast_records(page, selector)
                if not records:
                    failures.append(
                        f"{route}: no visible elements matched {selector}"
                    )
                    continue
                for record in records:
                    item = {
                        "route": route,
                        "selector": selector,
                        "minimum": minimum,
                        **record,
                    }
                    text_results.append(item)
                    if float(record["ratio"]) < minimum:
                        failures.append(
                            f"{route} {selector}: contrast "
                            f"{float(record['ratio']):.2f} below "
                            f"{minimum:.2f} for {record['text']!r}"
                        )

            for route, selector, expected_count in DECORATIVE_ICON_CHECKS:
                page = page_for(
                    pages,
                    browser,
                    args.cms,
                    route,
                    args.output,
                )
                records = decorative_icon_records(page, selector)
                if len(records) != expected_count:
                    failures.append(
                        f"{route} {selector}: expected {expected_count} visible "
                        f"decorative icons, found {len(records)}"
                    )
                for index, record in enumerate(records, start=1):
                    item = {
                        "route": route,
                        "selector": selector,
                        "index": index,
                        **record,
                    }
                    icon_results.append(item)
                    checks = {
                        "aria-hidden": record["ariaHidden"] == "true",
                        "presentation role": record["role"] == "presentation",
                        "transparent background": bool(
                            record["transparentBackground"]
                        ),
                        "image present": bool(record["imagePresent"]),
                        "image loaded": bool(record["imageLoaded"]),
                        "image visible": bool(record["imageVisible"]),
                        "visual-cue source": "visual-cues/"
                        in str(record["imageSource"]),
                    }
                    failed = [name for name, passed in checks.items() if not passed]
                    if failed:
                        failures.append(
                            f"{route} {selector} icon {index} "
                            f"({record['cue']!r}) failed: {', '.join(failed)}"
                        )
        finally:
            for page in pages.values():
                page.context.close()
            browser.close()

    payload = {
        "cms": args.cms,
        "text_results": text_results,
        "decorative_icon_results": icon_results,
        "failures": failures,
    }
    (args.output / "dark-readability.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    checks_run = len(text_results) + len(icon_results)
    print(
        f"Dark readability audit: {checks_run - len(failures)}/{checks_run} "
        f"text and decorative checks pass."
    )
    for failure in failures:
        print(f"- {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
