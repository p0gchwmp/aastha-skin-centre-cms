#!/usr/bin/env python3
"""Block the exact mobile regressions reported from the live iPhone UI.

The audit deliberately binds to patient-visible content instead of generic
component counts:

* Homepage FAQ question: ``How much does a consultation cost?``
* Laser section heading: ``#which-areas-can-be-treated``
* All 19 area labels, including boundaries between three sibling clean lists

It runs at a 414 x 896 iPhone-sized WebKit viewport in dark mode and records
screenshots plus computed geometry/contrast evidence.
"""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from playwright.sync_api import Browser, Locator, Page, sync_playwright


VIEWPORT = {"width": 414, "height": 896}
HOME_QUESTION = "How much does a consultation cost?"
EXPECTED_AREAS = (
    "Upper lip",
    "Chin",
    "Sideburns",
    "Jawline",
    "Neck",
    "Full face",
    "Underarms",
    "Arms",
    "Forearms",
    "Shoulders",
    "Chest",
    "Abdomen",
    "Back",
    "Bikini line",
    "Legs",
    "Thighs",
    "Lower legs",
    "Toes",
    "Full body",
)
MIN_FAQ_CONTRAST = 7.0
MAX_LIST_GAP = 20.0
MAX_GAP_SPREAD = 8.0


def normalise(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip()


def new_page(browser: Browser) -> Page:
    context = browser.new_context(
        viewport=VIEWPORT,
        device_scale_factor=2,
        is_mobile=True,
        has_touch=True,
        color_scheme="dark",
        locale="en-IN",
    )
    context.add_init_script(
        """
        (() => {
          try { localStorage.setItem('aastha-theme', 'dark'); } catch (_) {}
          document.documentElement.dataset.theme = 'dark';
        })();
        """
    )
    return context.new_page()


def settle(page: Page, url: str) -> None:
    page.goto(url, wait_until="networkidle", timeout=120_000)
    page.evaluate("document.documentElement.dataset.theme = 'dark'")
    page.wait_for_timeout(750)
    page.evaluate(
        """
        async () => {
          if (document.fonts && document.fonts.ready) await document.fonts.ready;
        }
        """
    )
    page.wait_for_timeout(250)


def find_faq(page: Page, question: str) -> Locator:
    for index in range(page.locator("details").count()):
        details = page.locator("details").nth(index)
        summary = details.locator(":scope > summary")
        if summary.count() and normalise(summary.first.inner_text()) == question:
            return details
    raise RuntimeError(f"FAQ question not found: {question!r}")


def inspect_homepage_faq(page: Page, output: Path) -> dict[str, Any]:
    details = find_faq(page, HOME_QUESTION)
    details.evaluate("node => { node.open = true; }")
    details.scroll_into_view_if_needed()
    page.wait_for_timeout(250)

    answer = details.locator(":scope > p").first
    if not answer.count():
        raise RuntimeError("Homepage consultation FAQ has no direct answer paragraph.")

    evidence = answer.evaluate(
        """
        node => {
          const parseRgb = value => {
            const match = value.match(/rgba?\\(([^)]+)\\)/i);
            if (!match) return null;
            const parts = match[1].split(',').map(part => Number.parseFloat(part.trim()));
            return {
              r: parts[0], g: parts[1], b: parts[2],
              a: parts.length > 3 ? parts[3] : 1,
            };
          };
          const channel = value => {
            const normalised = value / 255;
            return normalised <= 0.04045
              ? normalised / 12.92
              : Math.pow((normalised + 0.055) / 1.055, 2.4);
          };
          const luminance = color =>
            0.2126 * channel(color.r) +
            0.7152 * channel(color.g) +
            0.0722 * channel(color.b);
          const contrast = (foreground, background) => {
            const high = Math.max(luminance(foreground), luminance(background));
            const low = Math.min(luminance(foreground), luminance(background));
            return (high + 0.05) / (low + 0.05);
          };
          const nearestOpaqueBackground = start => {
            let current = start;
            while (current) {
              const css = getComputedStyle(current).backgroundColor;
              const parsed = parseRgb(css);
              if (parsed && parsed.a >= 0.98) {
                return {
                  css,
                  color: parsed,
                  tag: current.tagName.toLowerCase(),
                  className: current.className || '',
                };
              }
              current = current.parentElement;
            }
            return {
              css: 'rgb(0, 0, 0)',
              color: { r: 0, g: 0, b: 0, a: 1 },
              tag: 'fallback',
              className: '',
            };
          };
          const style = getComputedStyle(node);
          const foreground = parseRgb(style.color);
          const background = nearestOpaqueBackground(node);
          const rect = node.getBoundingClientRect();
          return {
            text: (node.innerText || '').replace(/\\s+/g, ' ').trim(),
            color: style.color,
            background,
            contrastRatio: contrast(foreground, background.color),
            opacity: style.opacity,
            fontSize: style.fontSize,
            lineHeight: style.lineHeight,
            rect: {
              x: rect.x, y: rect.y, width: rect.width, height: rect.height,
            },
            parentClass: node.parentElement ? node.parentElement.className || '' : '',
          };
        }
        """
    )
    details.screenshot(path=str(output / "homepage-consultation-faq.png"), animations="disabled")
    return evidence


def inspect_laser_area_lists(page: Page, output: Path) -> dict[str, Any]:
    heading = page.locator("#which-areas-can-be-treated")
    if heading.count() != 1:
        raise RuntimeError(
            "Expected exactly one #which-areas-can-be-treated heading; "
            f"found {heading.count()}."
        )

    heading.evaluate(
        """
        node => {
          const disclosure = node.closest('details');
          if (disclosure) disclosure.open = true;
        }
        """
    )
    page.wait_for_timeout(250)
    section = heading.locator("xpath=ancestor::section[contains(@class, 'article-section')][1]")
    if section.count() != 1:
        raise RuntimeError("Could not resolve the article section for treated areas.")
    section.scroll_into_view_if_needed()
    page.wait_for_timeout(250)

    evidence = section.evaluate(
        """
        section => {
          const normalise = value => (value || '').replace(/\\s+/g, ' ').trim();
          const lists = Array.from(section.children).filter(node =>
            node.matches('ul.clean-list:not(.clean-list--three)')
          );
          const items = lists.flatMap((list, listIndex) =>
            Array.from(list.children)
              .filter(node => node.tagName === 'LI')
              .map((node, itemIndex) => {
                const style = getComputedStyle(node);
                const rect = node.getBoundingClientRect();
                return {
                  text: normalise(node.innerText),
                  listIndex,
                  itemIndex,
                  rect: {
                    x: rect.x,
                    y: rect.y,
                    width: rect.width,
                    height: rect.height,
                    top: rect.top,
                    bottom: rect.bottom,
                  },
                  marginTop: style.marginTop,
                  marginBottom: style.marginBottom,
                  paddingTop: style.paddingTop,
                  paddingBottom: style.paddingBottom,
                  lineHeight: style.lineHeight,
                };
              })
          );
          const listStyles = lists.map(list => {
            const style = getComputedStyle(list);
            const rect = list.getBoundingClientRect();
            return {
              className: list.className,
              display: style.display,
              marginTop: style.marginTop,
              marginBottom: style.marginBottom,
              rowGap: style.rowGap,
              gridTemplateColumns: style.gridTemplateColumns,
              rect: {
                top: rect.top,
                bottom: rect.bottom,
                height: rect.height,
                width: rect.width,
              },
            };
          });
          const gaps = items.slice(1).map((item, index) => ({
            from: items[index].text,
            to: item.text,
            fromList: items[index].listIndex,
            toList: item.listIndex,
            crossesListBoundary: items[index].listIndex !== item.listIndex,
            pixels: item.rect.top - items[index].rect.bottom,
          }));
          const values = gaps.map(gap => gap.pixels);
          return {
            sectionHTML: section.outerHTML,
            listCount: lists.length,
            listStyles,
            items,
            labels: items.map(item => item.text),
            gaps,
            minGap: values.length ? Math.min(...values) : null,
            maxGap: values.length ? Math.max(...values) : null,
            gapSpread: values.length
              ? Math.max(...values) - Math.min(...values)
              : null,
            boundaryGaps: gaps.filter(gap => gap.crossesListBoundary),
            horizontalOverflow:
              section.scrollWidth > document.documentElement.clientWidth + 1,
          };
        }
        """
    )
    section.screenshot(path=str(output / "laser-treated-areas.png"), animations="disabled")
    return evidence


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--site", default="http://127.0.0.1:8000")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("audit-artifacts/reported-mobile-regressions"),
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    site = args.site.rstrip("/")

    failures: list[str] = []
    report: dict[str, Any] = {
        "site": site,
        "viewport": VIEWPORT,
        "thresholds": {
            "minimumFaqContrast": MIN_FAQ_CONTRAST,
            "maximumListGap": MAX_LIST_GAP,
            "maximumGapSpread": MAX_GAP_SPREAD,
        },
    }

    with sync_playwright() as playwright:
        browser = playwright.webkit.launch()
        try:
            homepage = new_page(browser)
            try:
                settle(homepage, f"{site}/")
                report["homepageFaq"] = inspect_homepage_faq(homepage, args.output)
            finally:
                homepage.context.close()

            laser = new_page(browser)
            try:
                settle(laser, f"{site}/treatments/laser-hair-reduction/")
                report["laserAreas"] = inspect_laser_area_lists(laser, args.output)
            finally:
                laser.context.close()
        finally:
            browser.close()

    faq = report["homepageFaq"]
    if faq["contrastRatio"] < MIN_FAQ_CONTRAST:
        failures.append(
            "Homepage consultation answer contrast is "
            f"{faq['contrastRatio']:.2f}:1; minimum is {MIN_FAQ_CONTRAST:.2f}:1."
        )
    if faq["opacity"] != "1":
        failures.append(
            f"Homepage consultation answer opacity is {faq['opacity']}; expected 1."
        )

    laser = report["laserAreas"]
    if laser["listCount"] != 3:
        failures.append(
            f"Treated-areas section has {laser['listCount']} direct clean lists; expected 3."
        )
    if tuple(laser["labels"]) != EXPECTED_AREAS:
        failures.append(
            "Treated-area labels/order changed. "
            f"Observed: {laser['labels']!r}."
        )
    if laser["maxGap"] is None or laser["maxGap"] > MAX_LIST_GAP:
        failures.append(
            f"Maximum treated-area gap is {laser['maxGap']}px; "
            f"budget is {MAX_LIST_GAP}px."
        )
    if laser["gapSpread"] is None or laser["gapSpread"] > MAX_GAP_SPREAD:
        failures.append(
            f"Treated-area gap spread is {laser['gapSpread']}px; "
            f"budget is {MAX_GAP_SPREAD}px."
        )
    if laser["horizontalOverflow"]:
        failures.append("Treated-areas section has horizontal overflow.")

    report["failures"] = failures
    (args.output / "reported-mobile-regressions.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    print(
        "Homepage consultation FAQ contrast: "
        f"{faq['contrastRatio']:.2f}:1."
    )
    print(
        "Laser treated-area gaps: "
        f"min={laser['minGap']:.2f}px, max={laser['maxGap']:.2f}px, "
        f"spread={laser['gapSpread']:.2f}px; "
        f"boundaries={laser['boundaryGaps']!r}."
    )
    if failures:
        for failure in failures:
            print(f"- {failure}")
        return 1
    print("Exact reported mobile regressions: 2/2 pass.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
