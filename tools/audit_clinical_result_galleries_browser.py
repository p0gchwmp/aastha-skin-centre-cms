#!/usr/bin/env python3
"""Exercise every route-specific clinical gallery in a real browser.

This audit is intentionally separate from legacy screenshot parity. It verifies
that all Drive-backed photographs render for an anonymous visitor, that only
multi-image folders become carousels, and that controls remain usable without
horizontal overflow on a phone-sized dark-mode viewport.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import urljoin

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from playwright.sync_api import Page, TimeoutError as PlaywrightTimeoutError, sync_playwright

from home.clinical_results import CLINICAL_RESULT_GALLERIES


@dataclass
class GalleryResult:
    route: str
    expected_images: int
    rendered_images: int = 0
    carousel_expected: bool = False
    carousel_present: bool = False
    horizontal_overflow: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.errors


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser()
    command.add_argument("--cms", default="http://127.0.0.1:8000")
    command.add_argument(
        "--output",
        type=Path,
        default=Path("audit-artifacts/clinical-gallery-browser"),
    )
    command.add_argument("--timeout", type=float, default=45.0)
    return command.parse_args()


def wait_for_image(page: Page, selector: str, timeout_ms: int) -> None:
    page.wait_for_function(
        """
        selector => {
          const image = document.querySelector(selector);
          return Boolean(image && image.complete && image.naturalWidth > 0);
        }
        """,
        selector,
        timeout=timeout_ms,
    )


def audit_route(page: Page, base: str, route: str, expected: int, timeout_ms: int) -> GalleryResult:
    result = GalleryResult(
        route=route,
        expected_images=expected,
        carousel_expected=expected > 1,
    )
    page_errors: list[str] = []
    page.on("pageerror", lambda error: page_errors.append(str(error)))

    try:
        page.goto(
            urljoin(base.rstrip("/") + "/", route.lstrip("/")),
            wait_until="domcontentloaded",
            timeout=timeout_ms,
        )
        page.wait_for_selector(
            ".clinical-results[data-clinical-ready=\"true\"]",
            state="attached",
            timeout=timeout_ms,
        )

        section = page.locator("section.clinical-results")
        slides = section.locator("[data-clinical-slide]")
        result.rendered_images = slides.count()
        result.carousel_present = section.get_attribute("data-clinical-carousel") is not None

        if result.rendered_images != expected:
            result.errors.append(
                f"rendered {result.rendered_images} slides; expected {expected}"
            )
        if result.carousel_present != result.carousel_expected:
            result.errors.append(
                "carousel presence does not match the page-specific image count"
            )

        overflow = page.evaluate(
            "Math.max(0, document.documentElement.scrollWidth - window.innerWidth)"
        )
        result.horizontal_overflow = int(round(float(overflow)))
        if result.horizontal_overflow > 2:
            result.errors.append(
                f"page overflows horizontally by {result.horizontal_overflow}px"
            )

        if expected == 1:
            if section.locator("[data-clinical-controls]").count():
                result.errors.append("single-image page rendered carousel controls")
            wait_for_image(page, ".clinical-results [data-clinical-slide] img", timeout_ms)
        else:
            controls = section.locator("[data-clinical-controls]")
            previous = section.locator("[data-clinical-previous]")
            next_button = section.locator("[data-clinical-next]")
            if controls.count() != 1 or previous.count() != 1 or next_button.count() != 1:
                result.errors.append("multi-image page is missing carousel controls")
            elif controls.is_hidden():
                result.errors.append("carousel controls remain hidden after hydration")
            else:
                sizes = page.evaluate(
                    """
                    () => [...document.querySelectorAll(
                      '.clinical-results__button'
                    )].map(button => {
                      const rect = button.getBoundingClientRect();
                      return [rect.width, rect.height];
                    })
                    """
                )
                if any(width < 44 or height < 44 for width, height in sizes):
                    result.errors.append("carousel controls are smaller than 44px")

            for index in range(expected):
                if index:
                    next_button.click()
                    page.wait_for_function(
                        """
                        expectedIndex => {
                          const current = document.querySelector(
                            '.clinical-results [data-clinical-current]'
                          );
                          return current && Number(current.textContent) === expectedIndex + 1;
                        }
                        """,
                        index,
                        timeout=timeout_ms,
                    )
                selector = (
                    ".clinical-results [data-clinical-slide]"
                    f"[data-slide-index=\"{index}\"] img"
                )
                wait_for_image(page, selector, timeout_ms)
                hidden = slides.nth(index).get_attribute("hidden")
                if hidden is not None:
                    result.errors.append(f"slide {index + 1} stayed hidden when selected")

            # No autoplay: the selected final slide must remain selected.
            final_value = expected
            page.wait_for_timeout(850)
            current_value = section.locator("[data-clinical-current]").inner_text()
            if current_value.strip() != str(final_value):
                result.errors.append("carousel advanced without user input")

            # Keyboard contract on every carousel.
            section.press("Home")
            page.wait_for_function(
                """
                () => document.querySelector(
                  '.clinical-results [data-clinical-current]'
                )?.textContent.trim() === '1'
                """,
                timeout=timeout_ms,
            )
            section.press("End")
            page.wait_for_function(
                """
                expected => document.querySelector(
                  '.clinical-results [data-clinical-current]'
                )?.textContent.trim() === String(expected)
                """,
                expected,
                timeout=timeout_ms,
            )

        if page_errors:
            result.errors.extend(f"page error: {message}" for message in page_errors)
    except PlaywrightTimeoutError as error:
        result.errors.append(f"browser timeout: {error}")
    except Exception as error:  # Keep evidence for all routes instead of aborting early.
        result.errors.append(str(error))
    return result


def markdown(results: list[GalleryResult], cms: str) -> str:
    lines = [
        "# Clinical gallery browser audit",
        "",
        f"- CMS: {cms}",
        f"- Routes audited: {len(results)}",
        f"- Passing routes: {sum(result.passed for result in results)}",
        f"- Photographs exercised: {sum(result.rendered_images for result in results)}",
        "",
        "| Route | Images | Carousel | Overflow | Result |",
        "|---|---:|---|---:|---|",
    ]
    for result in results:
        lines.append(
            f"| `{result.route}` | {result.rendered_images}/{result.expected_images} | "
            f"{'yes' if result.carousel_present else 'no'} | "
            f"{result.horizontal_overflow}px | "
            f"{'PASS' if result.passed else 'FAIL'} |"
        )
        for error in result.errors:
            lines.append(f"\n- `{result.route}`: {error}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parser()
    args.output.mkdir(parents=True, exist_ok=True)
    timeout_ms = int(args.timeout * 1000)
    results: list[GalleryResult] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        context = browser.new_context(
            viewport={"width": 390, "height": 844},
            device_scale_factor=2,
            is_mobile=True,
            has_touch=True,
            color_scheme="dark",
            locale="en-IN",
        )
        for route, gallery in sorted(CLINICAL_RESULT_GALLERIES.items()):
            page = context.new_page()
            result = audit_route(
                page,
                args.cms,
                route,
                len(gallery["images"]),
                timeout_ms,
            )
            results.append(result)
            if route in {
                "/treatments/acne-treatment/",
                "/treatments/hair-fall-treatment/",
            }:
                page.screenshot(
                    path=args.output / (
                        route.strip("/").replace("/", "__") + "--mobile-dark.png"
                    ),
                    full_page=True,
                )
            page.close()
        context.close()
        browser.close()

    payload = {
        "cms": args.cms,
        "routes": [asdict(result) | {"passed": result.passed} for result in results],
    }
    (args.output / "clinical-gallery-browser.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (args.output / "clinical-gallery-browser.md").write_text(
        markdown(results, args.cms),
        encoding="utf-8",
    )

    failures = [result for result in results if not result.passed]
    print(
        f"Clinical gallery browser audit: "
        f"{len(results) - len(failures)}/{len(results)} routes pass; "
        f"{sum(result.rendered_images for result in results)} photographs exercised."
    )
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
