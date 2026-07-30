#!/usr/bin/env python3
"""Browser-level desktop/mobile parity and interaction smoke tests."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import urljoin

from PIL import Image, ImageChops
from playwright.sync_api import Browser, Page, sync_playwright


DEFAULT_CMS = "https://aastha-skin-centre-cms.onrender.com"
DEFAULT_STATIC = "https://aastha-skin-centre-staging.onrender.com"
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


@dataclass
class VisualResult:
    route: str
    viewport: str
    similarity: float = 0.0
    static_size: tuple[int, int] = (0, 0)
    cms_size: tuple[int, int] = (0, 0)
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


def navigate(page: Page, origin: str, route: str) -> None:
    page.goto(
        urljoin(origin.rstrip("/") + "/", route.lstrip("/")),
        wait_until="networkidle",
        timeout=90_000,
    )
    page.wait_for_selector("main#main-content", timeout=30_000)
    page.wait_for_timeout(750)


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


def test_interactions(browser: Browser, cms: str) -> list[str]:
    errors: list[str] = []
    context = browser.new_context(viewport=VIEWPORTS["mobile"], color_scheme="light")
    page = context.new_page()
    opened: list[str] = []
    page.on("popup", lambda popup: opened.append(popup.url))

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
    else:
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
        fields = {
            "name": "Website QA",
            "mobile": "9876543210",
            "age": "30",
            "concern": "Skin concern",
        }
        for name, value in fields.items():
            locator = form.locator(f'[name="{name}"]')
            if locator.count():
                locator.first.fill(value)
        for alternatives, value in [
            (("clinic", "branch"), "Karan Nagar"),
            (("patient_type",), "New patient"),
        ]:
            for name in alternatives:
                locator = form.locator(f'[name="{name}"]')
                if not locator.count():
                    continue
                tag = locator.first.evaluate("element => element.tagName")
                if tag == "SELECT":
                    options = locator.first.locator("option").all()
                    option_values = [option.get_attribute("value") or option.inner_text() for option in options]
                    selectable = next((item for item in option_values if item), None)
                    if selectable:
                        locator.first.select_option(selectable)
                else:
                    locator.first.fill(value)
                break
        form.evaluate("form => form.requestSubmit()")
        page.wait_for_timeout(400)
        open_count = page.evaluate("window.__appointmentOpens.length")
        if open_count != 1:
            errors.append(f"appointment submission opened {open_count} WhatsApp windows; expected 1")
        else:
            target = page.evaluate("window.__appointmentOpens[0][0]")
            if "wa.me" not in target or "9876543210" not in target:
                errors.append("appointment WhatsApp payload is incomplete")
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
        "| Route | Viewport | Similarity | Static size | CMS size | Result |",
        "|---|---:|---:|---:|---:|---|",
    ]
    for item in results:
        lines.append(
            f"| `{item.route}` | {item.viewport} | {item.similarity:.4f} | "
            f"{item.static_size[0]}×{item.static_size[1]} | "
            f"{item.cms_size[0]}×{item.cms_size[1]} | "
            f"{'PASS' if item.passed else 'FAIL'} |"
        )
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
                result = VisualResult(route=route, viewport=viewport_name)
                static_page, static_console, static_page_errors = collect_page(browser, viewport)
                cms_page, cms_console, cms_page_errors = collect_page(browser, viewport)
                try:
                    navigate(static_page, args.static, route)
                    navigate(cms_page, args.cms, route)
                    static_path = args.output / f"{slug}--{viewport_name}--static.png"
                    cms_path = args.output / f"{slug}--{viewport_name}--cms.png"
                    diff_path = args.output / f"{slug}--{viewport_name}--diff.png"
                    result.static_size = screenshot(static_page, static_path)
                    result.cms_size = screenshot(cms_page, cms_path)
                    result.similarity = similarity(static_path, cms_path, diff_path)
                    if result.static_size != result.cms_size:
                        result.errors.append("full-page dimensions differ")
                    if result.similarity < args.minimum_similarity:
                        result.errors.append(
                            f"visual similarity {result.similarity:.4f} is below "
                            f"{args.minimum_similarity:.4f}"
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