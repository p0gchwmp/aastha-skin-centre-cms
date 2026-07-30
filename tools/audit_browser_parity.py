#!/usr/bin/env python3
"""Browser-level desktop/mobile parity and interaction smoke tests."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass, field
from datetime import date, timedelta
from pathlib import Path
from urllib.parse import urljoin

from PIL import Image, ImageChops
from playwright.sync_api import Browser, Locator, Page, sync_playwright


DEFAULT_CMS = "https://aastha-skin-centre-cms.onrender.com"
DEFAULT_STATIC = "https://aastha-skin-centre-staging.onrender.com"
VISUAL_POLISH_CSS = (
    Path(__file__).resolve().parents[1]
    / "home"
    / "static"
    / "css"
    / "visual-polish.css"
)
POLISHED_ROUTES = {"/", "/conditions/", "/treatments/"}
MAX_LAYOUT_HEIGHT_DELTA_RATIO = 0.04
ROUTES = [
    "/",
    "/treatments/acne-treatment/",
    "/conditions/",
    "/treatments/",
    "/blog/",
    "/book-appointment/",
    "/locations/karan-nagar/",
    "/locations/paloura/",
]
VIEWPORTS = {
    "desktop": {"width": 1440, "height": 1000},
    "mobile": {"width": 390, "height": 844},
}
LAYOUT_GROUPS = {
    "/": [
        {"grid": ".concern-grid", "item": ".concern-card", "action": ".card-link"},
        {"grid": ".treatment-grid", "item": ".treatment-card", "action": ".text-link"},
        {"grid": ".why-grid", "item": ".why-card"},
        {"grid": ".location-pro-grid", "item": ".location-pro-card", "action": ".location-actions"},
    ],
    "/conditions/": [
        {"grid": ".hub-category-grid", "item": ".hub-category"},
        {"grid": ".hub-link-grid", "item": ".hub-link", "center_orphans": True},
    ],
    "/treatments/": [
        {"grid": ".hub-category-grid", "item": ".hub-category"},
        {"grid": ".hub-link-grid", "item": ".hub-link", "center_orphans": True},
    ],
}


@dataclass
class VisualResult:
    route: str
    viewport: str
    validation_mode: str = "pixel-parity"
    similarity: float = 0.0
    static_size: tuple[int, int] = (0, 0)
    cms_size: tuple[int, int] = (0, 0)
    layout_checks: list[str] = field(default_factory=list)
    console_errors: list[str] = field(default_factory=list)
    page_errors: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.errors and not self.console_errors and not self.page_errors


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cms", default=DEFAULT_CMS)
    parser.add_argument("--static", default=DEFAULT_STATIC)
    parser.add_argument("--output", type=Path, default=Path("audit-artifacts/browser"))
    parser.add_argument("--minimum-similarity", type=float, default=0.985)
    return parser.parse_args()


def validation_mode(route: str) -> str:
    return "layout-metrics" if route in POLISHED_ROUTES else "pixel-parity"


def height_delta_ratio(left: tuple[int, int], right: tuple[int, int]) -> float:
    denominator = max(left[1], right[1], 1)
    return abs(left[1] - right[1]) / denominator


def navigate(page: Page, origin: str, route: str) -> None:
    page.goto(
        urljoin(origin.rstrip("/") + "/", route.lstrip("/")),
        wait_until="networkidle",
        timeout=90_000,
    )
    page.wait_for_selector("main#main-content", timeout=30_000)
    page.wait_for_timeout(750)


def apply_visual_polish(page: Page) -> None:
    """Apply the proposed shared visual layer to a comparison page."""
    page.add_style_tag(content=VISUAL_POLISH_CSS.read_text(encoding="utf-8"))
    page.wait_for_timeout(100)


def screenshot(page: Page, path: Path) -> tuple[int, int]:
    page.screenshot(path=str(path), full_page=True, animations="disabled")
    with Image.open(path) as image:
        return image.size


def similarity(left_path: Path, right_path: Path, diff_path: Path) -> float:
    with Image.open(left_path).convert("RGB") as left, Image.open(right_path).convert("RGB") as right:
        if left.size != right.size:
            width = max(left.width, right.width)
            height = max(left.height, right.height)
            left_canvas = Image.new("RGB", (width, height), "white")
            right_canvas = Image.new("RGB", (width, height), "white")
            left_canvas.paste(left, (0, 0))
            right_canvas.paste(right, (0, 0))
            left = left_canvas
            right = right_canvas
        diff = ImageChops.difference(left, right)
        diff.save(diff_path)
        histogram = diff.histogram()
        squared = sum((index % 256) ** 2 * count for index, count in enumerate(histogram))
        rms = math.sqrt(squared / (left.width * left.height * 3))
        return max(0.0, 1.0 - rms / 255.0)


def collect_page(browser: Browser, viewport: dict[str, int]) -> tuple[Page, list[str], list[str]]:
    context = browser.new_context(viewport=viewport, color_scheme="light")
    page = context.new_page()
    console_errors: list[str] = []
    page_errors: list[str] = []
    page.on(
        "console",
        lambda message: console_errors.append(message.text)
        if message.type == "error"
        else None,
    )
    page.on("pageerror", lambda error: page_errors.append(str(error)))
    return page, console_errors, page_errors


def layout_issues(page: Page, route: str, viewport_name: str) -> list[str]:
    groups = LAYOUT_GROUPS.get(route, [])
    return page.evaluate(
        """
        ({groups, mobile}) => {
          const issues = [];
          const tolerance = 5;
          const visible = element => {
            const style = getComputedStyle(element);
            const rect = element.getBoundingClientRect();
            return style.display !== "none" && style.visibility !== "hidden" && rect.width > 0 && rect.height > 0;
          };
          const rectOf = element => {
            const rect = element.getBoundingClientRect();
            return {
              left: rect.left,
              right: rect.right,
              top: rect.top,
              bottom: rect.bottom,
              width: rect.width,
              height: rect.height
            };
          };
          const rowsFor = rects => {
            const rows = [];
            [...rects].sort((a, b) => a.top - b.top || a.left - b.left).forEach(rect => {
              let row = rows.find(candidate => Math.abs(candidate.top - rect.top) <= tolerance);
              if (!row) {
                row = {top: rect.top, items: []};
                rows.push(row);
              }
              row.items.push(rect);
            });
            rows.forEach(row => row.items.sort((a, b) => a.left - b.left));
            return rows;
          };

          if (document.documentElement.scrollWidth > document.documentElement.clientWidth + 1) {
            issues.push(`horizontal overflow: ${document.documentElement.scrollWidth}px > ${document.documentElement.clientWidth}px`);
          }

          groups.forEach(group => {
            const grids = [...document.querySelectorAll(group.grid)].filter(visible);
            if (!grids.length) {
              issues.push(`${group.grid}: expected at least one visible grid`);
              return;
            }

            grids.forEach((grid, gridIndex) => {
              const gridRect = rectOf(grid);
              const itemElements = [...grid.children].filter(
                element => element.matches(group.item) && visible(element)
              );
              if (!itemElements.length) {
                issues.push(`${group.grid}[${gridIndex}]: no visible ${group.item} items`);
                return;
              }
              const items = itemElements.map((element, index) => ({
                ...rectOf(element),
                element,
                index
              }));

              items.forEach(item => {
                if (item.left < gridRect.left - 1 || item.right > gridRect.right + 1) {
                  issues.push(`${group.grid}[${gridIndex}] item ${item.index}: escapes grid horizontally`);
                }
                if (item.element.scrollWidth > item.element.clientWidth + 1) {
                  issues.push(`${group.grid}[${gridIndex}] item ${item.index}: content overflows horizontally`);
                }
              });

              for (let leftIndex = 0; leftIndex < items.length; leftIndex += 1) {
                for (let rightIndex = leftIndex + 1; rightIndex < items.length; rightIndex += 1) {
                  const left = items[leftIndex];
                  const right = items[rightIndex];
                  const overlapX = Math.min(left.right, right.right) - Math.max(left.left, right.left);
                  const overlapY = Math.min(left.bottom, right.bottom) - Math.max(left.top, right.top);
                  if (overlapX > 1 && overlapY > 1) {
                    issues.push(`${group.grid}[${gridIndex}] items ${left.index}/${right.index}: overlap`);
                  }
                }
              }

              const rows = rowsFor(items);
              if (mobile) {
                const lefts = items.map(item => item.left);
                const widths = items.map(item => item.width);
                if (Math.max(...lefts) - Math.min(...lefts) > 2) {
                  issues.push(`${group.grid}[${gridIndex}]: mobile card edges are not aligned`);
                }
                if (Math.max(...widths) - Math.min(...widths) > 2) {
                  issues.push(`${group.grid}[${gridIndex}]: mobile card widths differ`);
                }
              } else {
                rows.filter(row => row.items.length > 1).forEach((row, rowIndex) => {
                  const heights = row.items.map(item => item.height);
                  if (Math.max(...heights) - Math.min(...heights) > 4) {
                    issues.push(`${group.grid}[${gridIndex}] row ${rowIndex}: card heights differ`);
                  }

                  if (group.action) {
                    const actionBottoms = row.items.map(item => {
                      const action = item.element.querySelector(group.action);
                      return action && visible(action) ? action.getBoundingClientRect().bottom : null;
                    }).filter(value => value !== null);
                    if (actionBottoms.length === row.items.length && Math.max(...actionBottoms) - Math.min(...actionBottoms) > 6) {
                      issues.push(`${group.grid}[${gridIndex}] row ${rowIndex}: actions are not bottom-aligned`);
                    }
                  }
                });

                if (group.center_orphans && rows.length > 1) {
                  const fullRowCount = Math.max(...rows.map(row => row.items.length));
                  const lastRow = rows[rows.length - 1].items;
                  if (lastRow.length < fullRowCount) {
                    const rowLeft = Math.min(...lastRow.map(item => item.left));
                    const rowRight = Math.max(...lastRow.map(item => item.right));
                    const rowCenter = (rowLeft + rowRight) / 2;
                    const gridCenter = (gridRect.left + gridRect.right) / 2;
                    const allowed = Math.max(8, gridRect.width * 0.04);
                    if (Math.abs(rowCenter - gridCenter) > allowed) {
                      issues.push(`${group.grid}[${gridIndex}]: incomplete final row is not centred`);
                    }
                  }
                }
              }
            });
          });
          return issues;
        }
        """,
        {"groups": groups, "mobile": viewport_name == "mobile"},
    )


def fill_control(locator: Locator, preferred: str = "Website QA") -> None:
    """Fill an input-like control or choose a safe non-empty select option."""
    if not locator.count():
        return
    control = locator.first
    tag = control.evaluate("element => element.tagName")
    if tag == "SELECT":
        choices = control.evaluate(
            """
            element => [...element.options].map(option => ({
              value: option.value,
              label: option.textContent.trim(),
              disabled: option.disabled
            }))
            """
        )
        preferred_lower = preferred.lower()
        choice = next(
            (
                item
                for item in choices
                if item["value"]
                and not item["disabled"]
                and preferred_lower in (item["value"] + " " + item["label"]).lower()
            ),
            None,
        )
        if choice is None:
            choice = next(
                (item for item in choices if item["value"] and not item["disabled"]),
                None,
            )
        if choice:
            control.select_option(value=choice["value"])
        return

    input_type = str(control.get_attribute("type") or "").lower()
    if input_type in {"checkbox", "radio"}:
        control.check()
    elif input_type == "date":
        control.fill((date.today() + timedelta(days=3)).isoformat())
    elif input_type == "number":
        control.fill("30")
    elif input_type not in {"button", "submit", "reset", "hidden", "file"}:
        control.fill(preferred)


def test_interactions(browser: Browser, cms: str) -> list[str]:
    errors: list[str] = []
    context = browser.new_context(viewport=VIEWPORTS["mobile"], color_scheme="light")
    page = context.new_page()
    try:
        navigate(page, cms, "/")
        nav_toggle = page.locator(".nav-toggle")
        if nav_toggle.count() != 1:
            errors.append("mobile navigation toggle is missing")
        else:
            nav_toggle.click()
            if nav_toggle.get_attribute("aria-expanded") != "true":
                errors.append("mobile navigation did not open")

        theme = page.locator(".theme-toggle")
        if theme.count() != 1:
            errors.append("theme toggle is missing")
        else:
            before = page.locator("html").get_attribute("data-theme")
            theme.click()
            after = page.locator("html").get_attribute("data-theme")
            if before == after:
                errors.append("theme toggle did not change the active theme")

        navigate(page, cms, "/book-appointment/")
        form = page.locator("[data-appointment-form]")
        if form.count() != 1:
            errors.append(f"expected one appointment form; found {form.count()}")
            return errors

        page.evaluate(
            """
            () => {
              window.__appointmentOpens = [];
              window.open = (...args) => {
                window.__appointmentOpens.push(args);
                return null;
              };
            }
            """
        )
        for name, value in {
            "name": "Website QA",
            "mobile": "9876543210",
            "age": "30",
            "concern": "Skin concern",
        }.items():
            fill_control(form.locator(f'[name="{name}"]'), value)

        for alternatives, value in [
            (("clinic", "branch"), "Karan Nagar"),
            (("patient_type",), "New patient"),
        ]:
            for name in alternatives:
                locator = form.locator(f'[name="{name}"]')
                if locator.count():
                    fill_control(locator, value)
                    break

        for control in form.locator("[required]").all():
            current_value = control.evaluate(
                "element => 'value' in element ? element.value : ''"
            )
            input_type = str(control.get_attribute("type") or "").lower()
            if not current_value and input_type not in {"checkbox", "radio"}:
                fill_control(control)
            elif input_type in {"checkbox", "radio"} and not control.is_checked():
                fill_control(control)

        form.evaluate("form => form.requestSubmit()")
        page.wait_for_timeout(400)
        open_count = page.evaluate("window.__appointmentOpens.length")
        if open_count != 1:
            errors.append(
                f"appointment submission opened {open_count} WhatsApp windows; expected 1"
            )
        else:
            target = page.evaluate("window.__appointmentOpens[0][0]")
            if "wa.me" not in target or "9876543210" not in target:
                errors.append("appointment WhatsApp payload is incomplete")
    except Exception as exc:
        errors.append(f"interaction audit crashed: {exc}")
    finally:
        context.close()
    return errors


def markdown(results: list[VisualResult], interaction_errors: list[str], cms: str, static: str) -> str:
    lines = [
        "# Browser parity audit",
        "",
        f"- CMS: {cms}",
        f"- Static reference: {static}",
        f"- Visual checks: {len(results)}",
        f"- Passing visual checks: {sum(item.passed for item in results)}",
        "",
        "## Visual results",
        "",
        "| Route | Viewport | Mode | Similarity | Static size | CMS size | Result |",
        "|---|---:|---|---:|---:|---:|---|",
    ]
    for item in results:
        lines.append(
            f"| `{item.route}` | {item.viewport} | {item.validation_mode} | "
            f"{item.similarity:.4f} | {item.static_size[0]}×{item.static_size[1]} | "
            f"{item.cms_size[0]}×{item.cms_size[1]} | "
            f"{'PASS' if item.passed else 'FAIL'} |"
        )
        for check in item.layout_checks:
            lines.append(f"\n- `{item.route}` / {item.viewport}: {check}")
        for error in item.errors + item.console_errors + item.page_errors:
            lines.append(f"\n- `{item.route}` / {item.viewport}: {error}")
    lines.extend(["", "## Interaction checks", ""])
    if interaction_errors:
        lines.extend(f"- {error}" for error in interaction_errors)
    else:
        lines.append("All interaction checks passed.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = arguments()
    args.output.mkdir(parents=True, exist_ok=True)
    results: list[VisualResult] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        for route in ROUTES:
            slug = "home" if route == "/" else route.strip("/").replace("/", "__")
            for viewport_name, viewport in VIEWPORTS.items():
                result = VisualResult(
                    route=route,
                    viewport=viewport_name,
                    validation_mode=validation_mode(route),
                )
                static_page, static_console, static_page_errors = collect_page(browser, viewport)
                cms_page, cms_console, cms_page_errors = collect_page(browser, viewport)
                try:
                    navigate(static_page, args.static, route)
                    navigate(cms_page, args.cms, route)
                    apply_visual_polish(static_page)
                    apply_visual_polish(cms_page)
                    static_path = args.output / f"{slug}--{viewport_name}--static.png"
                    cms_path = args.output / f"{slug}--{viewport_name}--cms.png"
                    diff_path = args.output / f"{slug}--{viewport_name}--diff.png"
                    result.static_size = screenshot(static_page, static_path)
                    result.cms_size = screenshot(cms_page, cms_path)
                    result.similarity = similarity(static_path, cms_path, diff_path)

                    if result.validation_mode == "pixel-parity":
                        if result.static_size != result.cms_size:
                            result.errors.append("full-page dimensions differ")
                        if result.similarity < args.minimum_similarity:
                            result.errors.append(
                                f"visual similarity {result.similarity:.4f} is below "
                                f"{args.minimum_similarity:.4f}"
                            )
                    else:
                        ratio = height_delta_ratio(result.static_size, result.cms_size)
                        result.layout_checks.append(
                            f"layout height delta {ratio:.2%}; allowed {MAX_LAYOUT_HEIGHT_DELTA_RATIO:.2%}"
                        )
                        if ratio > MAX_LAYOUT_HEIGHT_DELTA_RATIO:
                            result.errors.append(
                                f"layout height delta {ratio:.2%} exceeds "
                                f"{MAX_LAYOUT_HEIGHT_DELTA_RATIO:.2%}"
                            )
                        for label, page in (("static", static_page), ("CMS", cms_page)):
                            for issue in layout_issues(page, route, viewport_name):
                                result.errors.append(f"{label} layout: {issue}")
                        if not result.errors:
                            result.layout_checks.append(
                                "no horizontal overflow, overlap, uneven row heights, "
                                "misaligned actions or off-centre orphan cards"
                            )
                except Exception as exc:
                    result.errors.append(str(exc))
                finally:
                    result.console_errors.extend(static_console)
                    result.console_errors.extend(cms_console)
                    result.page_errors.extend(static_page_errors)
                    result.page_errors.extend(cms_page_errors)
                    static_page.context.close()
                    cms_page.context.close()
                results.append(result)

        interaction_errors = test_interactions(browser, args.cms)
        browser.close()

    payload = {
        "cms": args.cms,
        "static": args.static,
        "results": [asdict(item) | {"passed": item.passed} for item in results],
        "interaction_errors": interaction_errors,
    }
    (args.output / "browser-parity.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (args.output / "browser-parity.md").write_text(
        markdown(results, interaction_errors, args.cms, args.static),
        encoding="utf-8",
    )

    failed = [item for item in results if not item.passed]
    print(
        f"Browser audit: {len(results) - len(failed)}/{len(results)} visual checks pass; "
        f"{len(interaction_errors)} interaction errors."
    )
    return 1 if failed or interaction_errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
