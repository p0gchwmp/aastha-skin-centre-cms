#!/usr/bin/env python3
"""Audit practical frontend delivery budgets on representative CMS routes."""

from __future__ import annotations

import argparse
import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import Browser, Page, sync_playwright


DEFAULT_CMS = "https://aastha-skin-centre-cms.onrender.com"
ROUTES = ["/", "/book-appointment/", "/treatments/", "/conditions/", "/blog/"]
VIEWPORTS = {
    "desktop": {"width": 1440, "height": 1000},
    "mobile": {"width": 390, "height": 844},
}
MAX_DOM_NODES = 5000
MAX_ENCODED_BYTES = 12 * 1024 * 1024
MAX_IMAGE_BYTES = 10 * 1024 * 1024
MAX_CSS_JS_REQUESTS = 15
MAX_CLS = 0.10


@dataclass
class PerformanceResult:
    route: str
    viewport: str
    dom_nodes: int = 0
    request_count: int = 0
    encoded_bytes: int = 0
    image_bytes: int = 0
    css_js_requests: int = 0
    first_contentful_paint_ms: float = 0.0
    largest_contentful_paint_ms: float = 0.0
    cumulative_layout_shift: float = 0.0
    image_count: int = 0
    lazy_image_count: int = 0
    errors: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.errors


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cms", default=DEFAULT_CMS)
    parser.add_argument(
        "--output", type=Path, default=Path("audit-artifacts/frontend-performance")
    )
    return parser.parse_args()


def page_with_observers(browser: Browser, viewport: dict[str, int]) -> Page:
    context = browser.new_context(viewport=viewport, color_scheme="light")
    context.add_init_script(
        """
        window.__aasthaPerformance = {cls: 0, lcp: 0};
        try {
          new PerformanceObserver(list => {
            for (const entry of list.getEntries()) {
              if (!entry.hadRecentInput) window.__aasthaPerformance.cls += entry.value;
            }
          }).observe({type: 'layout-shift', buffered: true});
          new PerformanceObserver(list => {
            const entries = list.getEntries();
            if (entries.length) {
              window.__aasthaPerformance.lcp = entries[entries.length - 1].startTime;
            }
          }).observe({type: 'largest-contentful-paint', buffered: true});
        } catch (error) {
          window.__aasthaPerformance.observerError = String(error);
        }
        """
    )
    return context.new_page()


def inspect(page: Page) -> dict[str, object]:
    return page.evaluate(
        """
        () => {
          const resources = performance.getEntriesByType('resource');
          const encoded = entry => Number(entry.encodedBodySize || 0);
          const images = [...document.querySelectorAll('main img')].map((image, index) => {
            const rect = image.getBoundingClientRect();
            return {
              index,
              src: image.currentSrc || image.src,
              loading: image.getAttribute('loading') || 'auto',
              decoding: image.getAttribute('decoding') || 'auto',
              fetchpriority: image.getAttribute('fetchpriority') || 'auto',
              width: Number(image.getAttribute('width') || image.width || 0),
              height: Number(image.getAttribute('height') || image.height || 0),
              visible: rect.width > 0 && rect.height > 0,
            };
          });
          const scripts = [...document.querySelectorAll('script[src]')].map(script => ({
            src: script.src,
            async: script.async,
            defer: script.defer,
            type: script.type,
          }));
          const paints = performance.getEntriesByType('paint');
          const fcp = paints.find(entry => entry.name === 'first-contentful-paint');
          return {
            domNodes: document.querySelectorAll('*').length,
            requestCount: resources.length,
            encodedBytes: resources.reduce((sum, entry) => sum + encoded(entry), 0),
            imageBytes: resources
              .filter(entry => entry.initiatorType === 'img')
              .reduce((sum, entry) => sum + encoded(entry), 0),
            cssJsRequests: resources.filter(entry =>
              ['script', 'link'].includes(entry.initiatorType)
              && /\.(?:css|js)(?:\?|$)/i.test(entry.name)
            ).length,
            fcp: fcp ? fcp.startTime : 0,
            lcp: Number(window.__aasthaPerformance?.lcp || 0),
            cls: Number(window.__aasthaPerformance?.cls || 0),
            observerError: window.__aasthaPerformance?.observerError || '',
            images,
            scripts,
          };
        }
        """
    )


def validate(result: PerformanceResult, details: dict[str, object]) -> None:
    images = list(details["images"])
    scripts = list(details["scripts"])

    if result.dom_nodes > MAX_DOM_NODES:
        result.errors.append(
            f"DOM contains {result.dom_nodes} nodes; budget is {MAX_DOM_NODES}"
        )
    if result.encoded_bytes > MAX_ENCODED_BYTES:
        result.errors.append(
            f"encoded resource weight is {result.encoded_bytes} bytes; "
            f"budget is {MAX_ENCODED_BYTES}"
        )
    if result.image_bytes > MAX_IMAGE_BYTES:
        result.errors.append(
            f"image resource weight is {result.image_bytes} bytes; "
            f"budget is {MAX_IMAGE_BYTES}"
        )
    if result.css_js_requests > MAX_CSS_JS_REQUESTS:
        result.errors.append(
            f"CSS/JS request count is {result.css_js_requests}; "
            f"budget is {MAX_CSS_JS_REQUESTS}"
        )
    if result.cumulative_layout_shift > MAX_CLS:
        result.errors.append(
            f"CLS is {result.cumulative_layout_shift:.4f}; budget is {MAX_CLS:.2f}"
        )
    if details.get("observerError"):
        result.errors.append(f"performance observer failed: {details['observerError']}")

    visible_images = [image for image in images if image["visible"]]
    for image in visible_images:
        if not image["width"] or not image["height"]:
            result.errors.append(
                f"image has no intrinsic dimensions: {image['src']}"
            )
        if image["decoding"] != "async":
            result.errors.append(
                f"image is missing decoding=async: {image['src']}"
            )

    if visible_images:
        first = visible_images[0]
        if first["loading"] == "lazy":
            result.errors.append("first visible content image is lazy-loaded")
        if first["fetchpriority"] != "high":
            result.errors.append("first visible content image lacks fetchpriority=high")
        for image in visible_images[1:]:
            if image["loading"] != "lazy":
                result.errors.append(
                    f"non-primary image is not lazy-loaded: {image['src']}"
                )

    for script in scripts:
        if not script["async"] and not script["defer"] and script["type"] != "module":
            result.errors.append(f"render-blocking external script: {script['src']}")


def markdown(results: list[PerformanceResult], cms: str) -> str:
    lines = [
        "# Frontend performance audit",
        "",
        f"- CMS: {cms}",
        f"- Checks: {len(results)}",
        f"- Passing: {sum(result.passed for result in results)}",
        "",
        "| Route | Viewport | DOM | Requests | Encoded | Images | CSS/JS | FCP | LCP | CLS | Result |",
        "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|---|",
    ]
    for result in results:
        lines.append(
            f"| `{result.route}` | {result.viewport} | {result.dom_nodes} | "
            f"{result.request_count} | {result.encoded_bytes} | {result.image_bytes} | "
            f"{result.css_js_requests} | {result.first_contentful_paint_ms:.0f} ms | "
            f"{result.largest_contentful_paint_ms:.0f} ms | "
            f"{result.cumulative_layout_shift:.4f} | "
            f"{'PASS' if result.passed else 'FAIL'} |"
        )
        for error in result.errors:
            lines.append(f"\n- `{result.route}` / {result.viewport}: {error}")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = arguments()
    args.output.mkdir(parents=True, exist_ok=True)
    results: list[PerformanceResult] = []

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            for route in ROUTES:
                for viewport_name, viewport in VIEWPORTS.items():
                    result = PerformanceResult(route=route, viewport=viewport_name)
                    page = page_with_observers(browser, viewport)
                    try:
                        page.goto(
                            urljoin(args.cms.rstrip("/") + "/", route.lstrip("/")),
                            wait_until="networkidle",
                            timeout=90_000,
                        )
                        page.wait_for_selector("main#main-content", timeout=30_000)
                        page.wait_for_timeout(1_200)
                        details = inspect(page)
                        result.dom_nodes = int(details["domNodes"])
                        result.request_count = int(details["requestCount"])
                        result.encoded_bytes = int(details["encodedBytes"])
                        result.image_bytes = int(details["imageBytes"])
                        result.css_js_requests = int(details["cssJsRequests"])
                        result.first_contentful_paint_ms = float(details["fcp"])
                        result.largest_contentful_paint_ms = float(details["lcp"])
                        result.cumulative_layout_shift = float(details["cls"])
                        result.image_count = len(details["images"])
                        result.lazy_image_count = sum(
                            image["loading"] == "lazy" for image in details["images"]
                        )
                        validate(result, details)
                    except Exception as exc:
                        result.errors.append(f"audit crashed: {exc}")
                    finally:
                        page.context.close()
                    results.append(result)
        finally:
            browser.close()

    payload = {
        "cms": args.cms,
        "budgets": {
            "max_dom_nodes": MAX_DOM_NODES,
            "max_encoded_bytes": MAX_ENCODED_BYTES,
            "max_image_bytes": MAX_IMAGE_BYTES,
            "max_css_js_requests": MAX_CSS_JS_REQUESTS,
            "max_cls": MAX_CLS,
        },
        "results": [asdict(result) | {"passed": result.passed} for result in results],
    }
    (args.output / "frontend-performance.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (args.output / "frontend-performance.md").write_text(
        markdown(results, args.cms), encoding="utf-8"
    )

    failures = [result for result in results if not result.passed]
    print(
        f"Frontend performance audit: {len(results) - len(failures)}/{len(results)} pass."
    )
    for result in failures:
        for error in result.errors:
            print(f"- {result.route} / {result.viewport}: {error}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
