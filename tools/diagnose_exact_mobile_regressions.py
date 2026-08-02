#!/usr/bin/env python3
"""Diagnose the exact mobile regressions shown by the clinic owner.

The checks target visible text from the supplied screenshots rather than broad
component classes. They record live DOM, computed styles, contrast and geometry
for:

* Homepage FAQ: "How much does a consultation cost?"
* Acne-scar FAQ reference: "Can acne scars be removed completely?"
* Laser-hair component: Sideburns through Toes
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


def write_report(path: Path, report: dict[str, Any]) -> None:
    path.write_text(json.dumps(report, indent=2), encoding="utf-8")


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
        details => {
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
                return {
                  color: parsed,
                  css: getComputedStyle(current).backgroundColor,
                  tag: current.tagName.toLowerCase(),
                  className: current.className || '',
                };
              }
              current = current.parentElement;
            }
            return {
              color: { r: 0, g: 0, b: 0, a: 1 },
              css: 'rgb(0, 0, 0)',
              tag: 'fallback',
              className: '',
            };
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
              id: node.id || '',
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
          const directAnswerChildren = Array.from(details.children).filter(
            node => node.tagName !== 'SUMMARY'
          );
          const textNodes = directAnswerChildren.flatMap(root => {
            const nodes = [root, ...root.querySelectorAll('p, li, span, strong, div')];
            return nodes.filter(node => (node.innerText || '').trim().length > 0);
          });
          const uniqueTextNodes = Array.from(new Set(textNodes));
          const ancestry = [];
          let current = directAnswerChildren[0] || null;
          while (current && ancestry.length < 9) {
            ancestry.push(describe(current));
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


def inspect_laser_component(page: Page, screenshot_path: Path) -> dict[str, Any]:
    result = page.evaluate(
        """
        tokens => {
          const normalise = value => (value || '').replace(/\\s+/g, ' ').trim();
          const visible = element => {
            const rect = element.getBoundingClientRect();
            const style = getComputedStyle(element);
            return rect.width > 0 && rect.height > 0 && style.display !== 'none' &&
              style.visibility !== 'hidden';
          };
          const describe = node => {
            const style = getComputedStyle(node);
            const rect = node.getBoundingClientRect();
            return {
              tag: node.tagName.toLowerCase(),
              className: node.className || '',
              id: node.id || '',
              text: normalise(node.innerText),
              display: style.display,
              position: style.position,
              gridTemplateColumns: style.gridTemplateColumns,
              gridTemplateRows: style.gridTemplateRows,
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
              rect: {
                x: rect.x,
                y: rect.y,
                width: rect.width,
                height: rect.height,
                top: rect.top,
                bottom: rect.bottom,
              },
            };
          };
          const all = Array.from(document.querySelectorAll('body *'));
          const matches = tokens.map(token => {
            const candidates = all.filter(element =>
              visible(element) && normalise(element.innerText) === token
            );
            candidates.sort((left, right) => {
              const descendants = left.querySelectorAll('*').length - right.querySelectorAll('*').length;
              if (descendants !== 0) return descendants;
              return left.getBoundingClientRect().width - right.getBoundingClientRect().width;
            });
            return candidates[0] || null;
          });
          const missing = tokens.filter((token, index) => !matches[index]);
          if (missing.length) {
            return {
              error: `Missing visible labels: ${missing.join(', ')}`,
              found: matches.map((element, index) => ({
                token: tokens[index],
                match: element ? describe(element) : null,
              })),
            };
          }

          let common = matches[0];
          while (common && !matches.every(element => common.contains(element))) {
            common = common.parentElement;
          }
          if (!common) return { error: 'Could not find a common component ancestor.' };
          common.setAttribute('data-exact-laser-component-diagnostic', 'true');

          const directWrapper = element => {
            let current = element;
            while (current.parentElement && current.parentElement !== common) {
              current = current.parentElement;
            }
            return current;
          };
          const wrappers = matches.map(directWrapper);
          const uniqueWrappers = Array.from(new Set(wrappers));
          uniqueWrappers.forEach((wrapper, index) => {
            wrapper.setAttribute('data-exact-laser-wrapper-diagnostic', String(index));
          });

          const labels = matches.map((element, index) => ({
            token: tokens[index],
            element: describe(element),
            wrapper: describe(wrappers[index]),
            ancestry: (() => {
              const chain = [];
              let current = element;
              while (current && chain.length < 10) {
                chain.push(describe(current));
                if (current === common) break;
                current = current.parentElement;
              }
              return chain;
            })(),
          }));
          const gaps = labels.slice(1).map((item, index) => ({
            from: labels[index].token,
            to: item.token,
            pixels: item.element.rect.top - labels[index].element.rect.bottom,
            wrapperPixels: item.wrapper.rect.top - labels[index].wrapper.rect.bottom,
          }));
          const labelPixels = gaps.map(gap => gap.pixels);
          const wrapperPixels = gaps.map(gap => gap.wrapperPixels);
          const first = labels[0].element.rect;
          const last = labels[labels.length - 1].element.rect;
          const clipY = Math.max(0, first.top + window.scrollY - 48);
          const clipBottom = last.bottom + window.scrollY + 48;

          return {
            outerHTML: common.outerHTML,
            component: describe(common),
            componentAncestry: (() => {
              const chain = [];
              let current = common;
              while (current && chain.length < 8) {
                chain.push(describe(current));
                current = current.parentElement;
              }
              return chain;
            })(),
            labels,
            uniqueWrappers: uniqueWrappers.map(describe),
            gaps,
            gapSpread: Math.max(...labelPixels) - Math.min(...labelPixels),
            maxGap: Math.max(...labelPixels),
            minGap: Math.min(...labelPixels),
            wrapperGapSpread: Math.max(...wrapperPixels) - Math.min(...wrapperPixels),
            maxWrapperGap: Math.max(...wrapperPixels),
            minWrapperGap: Math.min(...wrapperPixels),
            clip: {
              x: 0,
              y: clipY,
              width: document.documentElement.clientWidth,
              height: clipBottom - clipY,
            },
          };
        }
        """,
        list(LASER_TOKENS),
    )
    if result.get("error"):
        raise RuntimeError(json.dumps(result, indent=2))
    page.screenshot(
        path=str(screenshot_path),
        animations="disabled",
        clip=result["clip"],
    )
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", default="https://www.aasthaskincentre.in")
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("audit-artifacts/exact-mobile-diagnostic"),
    )
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    report_path = args.output / "diagnostic.json"
    base = args.base.rstrip("/")
    report: dict[str, Any] = {"base": base, "viewport": VIEWPORT}
    write_report(report_path, report)

    failure: Exception | None = None
    with sync_playwright() as playwright:
        browser = playwright.webkit.launch()
        try:
            home = prepare_page(browser)
            try:
                settle(home, f"{base}/")
                report["homepageFaq"] = inspect_faq(
                    home,
                    HOME_QUESTION,
                    args.output / "homepage-faq.png",
                )
                write_report(report_path, report)
                print(json.dumps({"homepageFaq": report["homepageFaq"]}, indent=2))
            finally:
                home.context.close()

            acne = prepare_page(browser)
            try:
                settle(acne, f"{base}/treatments/acne-scar-treatment/")
                report["acneScarFaq"] = inspect_faq(
                    acne,
                    ACNE_QUESTION,
                    args.output / "acne-scar-faq.png",
                )
                write_report(report_path, report)
                print(json.dumps({"acneScarFaq": report["acneScarFaq"]}, indent=2))
            finally:
                acne.context.close()

            laser = prepare_page(browser)
            try:
                settle(laser, f"{base}/treatments/laser-hair-reduction/")
                report["laserComponent"] = inspect_laser_component(
                    laser,
                    args.output / "laser-sideburns-to-toes.png",
                )
                write_report(report_path, report)
            finally:
                laser.context.close()
        except Exception as exc:  # Preserve every completed diagnostic.
            failure = exc
            report["error"] = {"type": type(exc).__name__, "message": str(exc)}
            write_report(report_path, report)
        finally:
            browser.close()

    if "laserComponent" in report:
        laser_summary = report["laserComponent"]
        print(
            json.dumps(
                {
                    "laserComponent": laser_summary["component"],
                    "gaps": laser_summary["gaps"],
                    "gapSpread": laser_summary["gapSpread"],
                    "componentAncestry": laser_summary["componentAncestry"],
                },
                indent=2,
            )
        )
    print(f"Wrote exact mobile diagnostic to {report_path}")
    if failure is not None:
        raise failure
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
