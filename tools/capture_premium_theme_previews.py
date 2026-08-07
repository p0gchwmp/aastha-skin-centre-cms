#!/usr/bin/env python3
"""Capture exact rendered luxury-theme previews from the local CMS.

QA helper for the approved redesign branch. It does not mutate content or
settings. The route set intentionally covers each major page family so a
site-wide design regression is visible before production rollout.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from playwright.sync_api import sync_playwright


ROUTES = {
    "home": "/",
    "acne-treatment": "/treatments/acne-treatment/",
    "laser-hair-reduction": "/treatments/laser-hair-reduction/",
    "treatments-index": "/treatments/",
    "conditions-index": "/conditions/",
    "doctor": "/dr-cheena-langer/",
    "locations-index": "/locations/",
    "book-appointment": "/book-appointment/",
    "contact": "/contact/",
    "blog-index": "/blog/",
}

VIEWPORTS = {
    "desktop": {"width": 1440, "height": 1000},
    "mobile": {"width": 430, "height": 932},
}


def warm_lazy_media(page) -> None:
    """Scroll through the document so lazy-loaded images enter the viewport."""
    height = int(page.evaluate("Math.max(document.body.scrollHeight, document.documentElement.scrollHeight)"))
    viewport_height = int(page.evaluate("window.innerHeight"))
    step = max(520, int(viewport_height * 0.72))
    for y in range(0, height, step):
        page.evaluate("y => window.scrollTo(0, y)", y)
        page.wait_for_timeout(90)
    page.evaluate("window.scrollTo(0, 0)")
    page.wait_for_timeout(350)


def capture_acne_debug(page, output: Path) -> None:
    payload = page.evaluate(
        """
        async () => {
          const describe = node => {
            if (!node) return null;
            const rect = node.getBoundingClientRect();
            const style = getComputedStyle(node);
            return {
              tag: node.tagName,
              id: node.id,
              className: node.className,
              rect: {x: rect.x, y: rect.y, width: rect.width, height: rect.height},
              display: style.display,
              position: style.position,
              width: style.width,
              maxWidth: style.maxWidth,
              gridTemplateColumns: style.gridTemplateColumns,
              gap: style.gap,
              parent: node.parentElement ? {
                tag: node.parentElement.tagName,
                id: node.parentElement.id,
                className: node.parentElement.className,
              } : null,
              children: [...node.children].map(child => {
                const childRect = child.getBoundingClientRect();
                const childStyle = getComputedStyle(child);
                return {
                  tag: child.tagName,
                  id: child.id,
                  className: child.className,
                  rect: {x: childRect.x, y: childRect.y, width: childRect.width, height: childRect.height},
                  display: childStyle.display,
                  position: childStyle.position,
                };
              }),
            };
          };
          const assetUrls = [
            '/static/css/premium-v5-reference.css',
            '/static/js/premium-v5-reference.js',
            '/static/css/premium-production.css',
            '/static/css/premium-production-polish.css',
            '/static/js/premium-production.js',
          ];
          const assetFetches = {};
          for (const url of assetUrls) {
            try {
              const response = await fetch(url, {cache: 'no-store'});
              assetFetches[url] = {
                status: response.status,
                ok: response.ok,
                contentType: response.headers.get('content-type'),
                bytes: (await response.text()).length,
              };
            } catch (error) {
              assetFetches[url] = {error: String(error)};
            }
          }
          return {
            body: {className: document.body.className, dataset: {...document.body.dataset}},
            main: describe(document.querySelector('#main-content')),
            hero: describe(document.querySelector('.page-hero')),
            contentLayout: describe(document.querySelector('.content-layout')),
            prose: describe(document.querySelector('.prose')),
            careSidebar: describe(document.querySelector('.care-sidebar')),
            careSidebarCard: describe(document.querySelector('.care-sidebar-card')),
            v5Rail: describe(document.querySelector('.v5-page-rail')),
            luxuryRail: describe(document.querySelector('.luxury-page-rail')),
            releaseTocDisplay: document.querySelector('.release-toc') ? getComputedStyle(document.querySelector('.release-toc')).display : null,
            assetFetches,
            styleSheets: [...document.styleSheets].map(sheet => sheet.href).filter(Boolean).filter(href => href.includes('premium')),
            nearestContainers: [...document.querySelectorAll('#main-content .container')].slice(0, 8).map(describe),
          };
        }
        """
    )
    (output / "acne-layout-debug.json").write_text(json.dumps(payload, indent=2), encoding="utf-8")
    (output / "acne-rendered.html").write_text(page.content(), encoding="utf-8")


def capture(base_url: str, output: Path) -> None:
    output.mkdir(parents=True, exist_ok=True)
    base_url = base_url.rstrip("/")

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=True)
        for device_name, viewport in VIEWPORTS.items():
            for theme in ("light", "dark"):
                context = browser.new_context(
                    viewport=viewport,
                    color_scheme=theme,
                    device_scale_factor=1,
                    reduced_motion="reduce",
                )
                context.add_init_script(
                    script=(
                        "localStorage.setItem('aastha-theme', " + repr(theme) + ");"
                        "document.documentElement.dataset.theme = " + repr(theme) + ";"
                    )
                )
                page = context.new_page()
                for label, route in ROUTES.items():
                    response = page.goto(f"{base_url}{route}", wait_until="networkidle", timeout=60000)
                    if response is None or response.status >= 400:
                        status = response.status if response else "no response"
                        raise RuntimeError(f"Preview route {route} returned {status}")
                    page.evaluate(
                        "theme => {"
                        " localStorage.setItem('aastha-theme', theme);"
                        " document.documentElement.dataset.theme = theme;"
                        "}",
                        theme,
                    )
                    page.wait_for_timeout(500)
                    warm_lazy_media(page)
                    if label == "acne-treatment" and device_name == "desktop" and theme == "dark":
                        capture_acne_debug(page, output)
                    page.screenshot(
                        path=str(output / f"{label}--{device_name}--{theme}.png"),
                        full_page=True,
                        animations="disabled",
                    )
                context.close()
        browser.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://127.0.0.1:8000")
    parser.add_argument("--output", default="audit-artifacts/premium-v4-preview")
    args = parser.parse_args()
    capture(args.base_url, Path(args.output))
