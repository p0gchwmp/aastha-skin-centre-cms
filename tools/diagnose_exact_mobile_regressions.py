#!/usr/bin/env python3
"""Diagnose the exact mobile regressions shown by the clinic owner.

This intentionally targets text from the supplied screenshots instead of broad
component classes. It records the live DOM, computed styles, contrast, item
geometry and WebKit screenshots for:

* Homepage FAQ: "How much does a consultation cost?"
* Acne-scar FAQ reference: "Can acne scars be removed completely?"
* Laser-hair list: Sideburns through Toes
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
ACNE_QUESTION = "Can acne scars be removed completely?"
LASER_TOKENS = (
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
)


def normalise(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def prepare_page(browser: Browser) -> Page:
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
    page.wait_for_timeout(1_000)
    page.evaluate(
        """
        async () => {
          if (document.fonts && document.fonts.ready) await document.fonts.ready;
        }
        """
    )
    page.wait_for_timeout(250)


def find_details(page: Page, question: str) -> Locator:
    details = page.locator("details")
    for index in range(details.count()):
        candidate = details.nth(index)
        summaries = candidate.locator(":scope > summary")
        if summaries.count() and normalise(summaries.first.inner_text()) == question:
            return candidate
    raise RuntimeError(f"Could not find FAQ details for {question!r} at {page.url}")


def inspect_faq(page: Page, question: str, screenshot_path: Path) -> dict[str, Any]:
    details = find_details(page, question)
    details.scroll_into_view_if_needed()
    if not details.get_attribute("open"):
        details.locator(":scope > summary").click()
    page.wait_for_timeout(350)

    result = details.evaluate(
        """
        (details) => {
          const parseRgb = value => {
            const match = value.match(/rgba?\\(([^)]+)\\)/i);
            if (!match) return null;
            const parts = match[1].split(',').map(part => Number.parseFloat(part.trim()));
            return { r: parts[0], g: parts[1], b: parts[2], a: parts.length > 3 ? parts[3] : 1 };
          };
          const luminance = color => {
            const convert = channel => {
              const value = channel / 255;
              return value <= 0.04045 ? value / 12.92 : Math.pow((value + 0.055) / 1.055, 2.4);
            };
            return 0.2126 * convert(color.r) + 0.7152 * convert(color.g) + 0.0722 * convert(color.b);
          };
          const contrast = (foreground, background) => {
            const light = Math.max(luminance(foreground), luminance(background));
            const dark = Math.min(luminance(foreground), luminance(background));
            return (light + 0.05) / (dark + 0.05);
          };
          const nearestBackground = node => {
            let current = node;
            while (current) {
              const parsed = parseRgb(getComputedStyle(current).backgroundColor);
              if (parsed && parsed.a >= 0.98) {
                return { color: parsed, css: getComputedStyle(current).backgroundColor,
                  tag: current.tagName.toLowerCase(), className: current.className || '' };
              }
              current = current.parentElement;
            }
            return { color: { r: 0, g: 0, b: 0, a: 1 }, css: 'rgb(0, 0, 0)', tag: 'fallback', className: '' };
          };
          const effectiveOpacity = node => {
            let opacity = 1;
            let current = node;
            while (current) {
              opacity *= Number.parseFloat(getComputedStyle(current).opacity || '1');
              current = current.parentElement;
            }
            return opacity;
          };
          const describe = node => {
            const style = getComputedStyle(node);
            const foreground = parseRgb(style.color);
            const background = nearestBackground(node);
            const rect = node.getBoundingClientRect();
            return {
              tag: node.tagName.toLowerCase(),
              className: node.className || '',
              text: (node.innerText || '').replace(/\\s+/g, ' ').trim(),
              color: style.color,
              opacity: style.opacity,
              effectiveOpacity: effectiveOpacity(node),
              backgroundColor: style.backgroundColor,
              nearestBackground: background,
              contrastRatio: foreground ? contrast(foreground, background.color) : null,
              fontSize: style.fontSize,
              fontWeight: style.fontWeight,
              lineHeight: style.lineHeight,
              visibility: style.visibility,
              display: style.display,
              rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height },
            };
          };
          const directAnswerChildren = Array.from(details.children).filter(node => node.tagName !== 'SUMMARY');
          const textNodes = directAnswerChildren.flatMap(root => {
            const nodes = [root, ...root.querySelectorAll('p, li, span, strong, div')];
            return nodes.filter(node => (node.innerText || '').trim().length > 0);
          });
          const uniqueTextNodes = Array.from(new Set(textNodes));
          const ancestry = [];
          let current = directAnswerChildren[0] || null;
          while (current && ancestry.length < 7) {
            const style = getComputedStyle(current);
            ancestry.push({
              tag: current.tagName.toLowerCase(),
              className: current.className || '',
              color: style.color,
              opacity: style.opacity,
              backgroundColor: style.backgroundColor,
            });
            current = current.parentElement;
          }
          return {
            outerHTML: details.outerHTML,
            details: describe(details),
            summary: describe(details.querySelector(':scope > summary')),
            directAnswerChildren: directAnswerChildren.map(describe),
            textNodes: uniqueTextNodes.map(describe),
            ancestry,
          };
        }
        """
    )
    details.screenshot(path=str(screenshot_path), animations="disabled")
    return result


def find_laser_list(page: Page) -> Locator:
    candidates = page.locator("ul, ol, [role='list']")
    best_index = -1
    best_score = -1
    diagnostics: list[dict[str, Any]] = []
    for index in range(candidates.count()):
        candidate = candidates.nth(index)
        direct_texts = candidate.locator(":scope > li, :scope > [role='listitem']").all_inner_texts()
        texts = [normalise(value) for value in direct_texts]
        score = sum(any(token.casefold() == text.casefold() for text in texts) for token in LASER_TOKENS)
        diagnostics.append({"index": index, "score": score, "texts": texts[:30]})
        if score > best_score:
            best_score = score
            best_index = index
    if best_index < 0 or best_score < 12:
        raise RuntimeError(f"Could not identify Sideburns-to-Toes list; candidates={diagnostics!r}")
    return candidates.nth(best_index)


def inspect_laser_list(page: Page, screenshot_path: Path) -> dict[str, Any]:
    target = find_laser_list(page)
    target.scroll_into_view_if_needed()
    page.wait_for_timeout(250)
    result = target.evaluate(
        """
        list => {
          const describeStyle = node => {
            const style = getComputedStyle(node);
            const rect = node.getBoundingClientRect();
            return {
              tag: node.tagName.toLowerCase(),
              className: node.className || '',
              text: (node.innerText || '').replace(/\\s+/g, ' ').trim(),
              display: style.display,
              position: style.position,
              gridTemplateColumns: style.gridTemplateColumns,
              gridAutoRows: style.gridAutoRows,
              rowGap: style.rowGap,
              columnGap: style.columnGap,
              columns: style.columns,
              columnCount: style.columnCount,
              alignItems: style.alignItems,
              alignContent: style.alignContent,
              minHeight: style.minHeight,
              height: style.height,
              marginTop: style.marginTop,
              marginBottom: style.marginBottom,
              paddingTop: style.paddingTop,
              paddingBottom: style.paddingBottom,
              breakInside: style.breakInside,
              rect: { x: rect.x, y: rect.y, width: rect.width, height: rect.height,
                top: rect.top, bottom: rect.bottom },
            };
          };
          const items = Array.from(list.children).filter(node =>
            node.matches('li, [role="listitem"]')
          );
          const itemData = items.map(describeStyle);
          const gaps = itemData.slice(1).map((item, index) => ({
            from: itemData[index].text,
            to: item.text,
            pixels: item.rect.top - itemData[index].rect.bottom,
          }));
          const ancestry = [];
          let current = list;
          while (current && ancestry.length < 8) {
            ancestry.push(describeStyle(current));
            current = current.parentElement;
          }
          return {
            outerHTML: list.outerHTML,
            list: describeStyle(list),
            items: itemData,
            gaps,
            gapSpread: gaps.length ? Math.max(...gaps.map(g => g.pixels)) - Math.min(...gaps.map(g => g.pixels)) : 0,
            maxGap: gaps.length ? Math.max(...gaps.map(g => g.pixels)) : 0,
            minGap: gaps.length ? Math.min(...gaps.map(g => g.pixels)) : 0,
            ancestry,
          };
        }
        """
    )
    target.screenshot(path=str(screenshot_path), animations="disabled")
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="https://www.aasthaskincentre.in")
    parser.add_argument("--output", type=Path, default=Path("audit-artifacts/exact-mobile-diagnostic"))
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    base = args.base.rstrip("/")

    report: dict[str, Any] = {"base": base, "viewport": VIEWPORT}
    with sync_playwright() as playwright:
        browser = playwright.webkit.launch()
        try:
            home = prepare_page(browser)
            settle(home, f"{base}/")
            report["homepageFaq"] = inspect_faq(
                home,
                HOME_QUESTION,
                args.output / "homepage-faq.png",
            )
            home.context.close()

            acne = prepare_page(browser)
            settle(acne, f"{base}/treatments/acne-scar-treatment/")
            report["acneScarFaq"] = inspect_faq(
                acne,
                ACNE_QUESTION,
                args.output / "acne-scar-faq.png",
            )
            acne.context.close()

            laser = prepare_page(browser)
            settle(laser, f"{base}/treatments/laser-hair-reduction/")
            report["laserList"] = inspect_laser_list(
                laser,
                args.output / "laser-sideburns-to-toes.png",
            )
            laser.context.close()
        finally:
            browser.close()

    report_path = args.output / "diagnostic.json"
    report_path.write_text(json.dumps(report, indent=2), encoding="utf-8")

    summary = {
        "homepageFaqText": report["homepageFaq"]["textNodes"],
        "acneScarFaqText": report["acneScarFaq"]["textNodes"],
        "laserList": {
            "list": report["laserList"]["list"],
            "gaps": report["laserList"]["gaps"],
            "gapSpread": report["laserList"]["gapSpread"],
            "ancestry": report["laserList"]["ancestry"],
        },
    }
    print(json.dumps(summary, indent=2))
    print(f"Wrote exact mobile diagnostic to {report_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
