#!/usr/bin/env python3
"""Audit balanced editorial lists and dark FAQ panel readability."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urljoin

from playwright.sync_api import Browser, Page, sync_playwright


DEFAULT_CMS = "https://aastha-skin-centre-cms.onrender.com"
LIST_ROUTES = (
    "/treatments/fungal-infection-treatment/",
    "/treatments/laser-hair-reduction/",
)
FAQ_ROUTE = "/book-appointment/"


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--cms", default=DEFAULT_CMS)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("audit-artifacts/content-rhythm"),
    )
    return parser.parse_args()


def route_url(origin: str, route: str) -> str:
    return urljoin(origin.rstrip("/") + "/", route.lstrip("/"))


def open_page(
    browser: Browser,
    origin: str,
    route: str,
    *,
    width: int,
    height: int,
    dark: bool = False,
) -> Page:
    context = browser.new_context(
        viewport={"width": width, "height": height},
        color_scheme="dark" if dark else "light",
    )
    if dark:
        context.add_init_script("localStorage.setItem('aastha-theme', 'dark');")
    page = context.new_page()
    page.goto(
        route_url(origin, route),
        wait_until="networkidle",
        timeout=90_000,
    )
    page.wait_for_selector("main#main-content", timeout=30_000)
    page.wait_for_timeout(350)
    return page


def inspect_long_list(page: Page) -> dict[str, object]:
    return page.evaluate(
        r"""
        () => {
          const visible = element => {
            const rect = element.getBoundingClientRect();
            const style = getComputedStyle(element);
            return rect.width > 0 && rect.height > 0
              && style.display !== 'none'
              && style.visibility !== 'hidden';
          };
          const candidates = [...document.querySelectorAll(
            'article.prose ul, article.prose .clean-list:not(.clean-list--three), article.prose .premium-bullet-grid'
          )]
            .map(list => ({
              list,
              items: [...list.children].filter(
                item => item.matches('li') && visible(item)
              ),
            }))
            .filter(candidate => visible(candidate.list) && candidate.items.length >= 6)
            .sort((left, right) => right.items.length - left.items.length);

          const candidate = candidates[0];
          if (!candidate) return {found: false};

          const list = candidate.list;
          const style = getComputedStyle(list);
          const itemRecords = candidate.items.map(item => {
            const rect = item.getBoundingClientRect();
            const itemStyle = getComputedStyle(item);
            return {
              text: item.textContent.trim().replace(/\s+/g, ' ').slice(0, 100),
              left: rect.left,
              top: rect.top,
              right: rect.right,
              bottom: rect.bottom,
              width: rect.width,
              height: rect.height,
              breakInside: itemStyle.breakInside,
            };
          });

          const groups = new Map();
          itemRecords.forEach(item => {
            const key = Math.round(item.left / 4) * 4;
            if (!groups.has(key)) groups.set(key, []);
            groups.get(key).push(item);
          });
          const columns = [...groups.entries()]
            .sort(([left], [right]) => left - right)
            .map(([left, items]) => {
              items.sort((a, b) => a.top - b.top);
              const gaps = items.slice(1).map((item, index) =>
                item.top - items[index].bottom
              );
              return {left, items, gaps};
            });

          return {
            found: true,
            itemCount: itemRecords.length,
            display: style.display,
            columnCount: style.columnCount,
            columnGap: style.columnGap,
            gridTemplateColumns: style.gridTemplateColumns,
            width: list.getBoundingClientRect().width,
            scrollWidth: list.scrollWidth,
            columns,
          };
        }
        """
    )


def parse_rgb(value: str) -> tuple[int, int, int]:
    numbers = value[value.find("(") + 1 : value.find(")")].split(",")
    return tuple(int(float(number.strip())) for number in numbers[:3])  # type: ignore[return-value]


def luminance(colour: tuple[int, int, int]) -> float:
    converted = []
    for value in colour:
        channel = value / 255
        converted.append(
            channel / 12.92
            if channel <= 0.04045
            else ((channel + 0.055) / 1.055) ** 2.4
        )
    return 0.2126 * converted[0] + 0.7152 * converted[1] + 0.0722 * converted[2]


def contrast_ratio(first: str, second: str) -> float:
    one = luminance(parse_rgb(first))
    two = luminance(parse_rgb(second))
    return (max(one, two) + 0.05) / (min(one, two) + 0.05)


def inspect_faq(page: Page) -> dict[str, object]:
    details = page.locator(".faq-pro-list details, .faq-clean-list details")
    if details.count() < 2:
        return {"found": False, "count": details.count()}

    first = details.nth(0)
    second = details.nth(1)
    first.locator("summary").click()
    page.wait_for_timeout(200)

    return page.evaluate(
        r"""
        () => {
          const items = [...document.querySelectorAll(
            '.faq-pro-list details, .faq-clean-list details'
          )];
          const openItem = items.find(item => item.open) || items[0];
          const closedItem = items.find(item => !item.open) || items[1];
          const answer = openItem.querySelector('.faq-answer');
          const answerText = answer?.querySelector('p, li, span') || answer;
          const openStyle = getComputedStyle(openItem);
          const closedStyle = getComputedStyle(closedItem);
          const answerStyle = answerText ? getComputedStyle(answerText) : null;
          return {
            found: Boolean(openItem && closedItem && answerText),
            openBackground: openStyle.backgroundColor,
            closedBackground: closedStyle.backgroundColor,
            openBorder: openStyle.borderColor,
            closedBorder: closedStyle.borderColor,
            answerColor: answerStyle?.color || '',
            answerOpacity: answerStyle?.opacity || '',
            answerBackground: answerStyle?.backgroundColor || '',
          };
        }
        """
    )


def main() -> int:
    args = arguments()
    args.output.mkdir(parents=True, exist_ok=True)
    failures: list[str] = []
    results: dict[str, object] = {"cms": args.cms, "lists": {}, "faq": {}}

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch()
        try:
            for route in LIST_ROUTES:
                route_results: dict[str, object] = {}
                for label, width, height in (
                    ("desktop", 1440, 1000),
                    ("mobile", 390, 844),
                ):
                    page = open_page(
                        browser,
                        args.cms,
                        route,
                        width=width,
                        height=height,
                    )
                    try:
                        record = inspect_long_list(page)
                        route_results[label] = record
                        slug = route.strip("/").replace("/", "__")
                        page.screenshot(
                            path=str(args.output / f"{slug}--{label}.png"),
                            full_page=True,
                            animations="disabled",
                        )
                        if not record.get("found"):
                            failures.append(f"{route} {label}: no long clinical list found")
                            continue

                        columns = record.get("columns", [])
                        if label == "desktop":
                            if record.get("columnCount") != "2":
                                failures.append(
                                    f"{route}: expected two balanced columns; "
                                    f"got columnCount={record.get('columnCount')!r}"
                                )
                            if len(columns) != 2:
                                failures.append(
                                    f"{route}: expected two rendered columns; got {len(columns)}"
                                )
                            for column_index, column in enumerate(columns, start=1):
                                gaps = [float(gap) for gap in column.get("gaps", [])]
                                if gaps and (min(gaps) < -1 or max(gaps) > 24):
                                    failures.append(
                                        f"{route}: column {column_index} has uneven gaps "
                                        f"{gaps!r}"
                                    )
                                for item in column.get("items", []):
                                    if "avoid" not in str(item.get("breakInside", "")):
                                        failures.append(
                                            f"{route}: item may split across columns: "
                                            f"{item.get('text')!r}"
                                        )
                        else:
                            if record.get("display") != "grid":
                                failures.append(
                                    f"{route}: mobile list is not a single-column grid"
                                )
                            if float(record.get("scrollWidth", 0)) > float(
                                record.get("width", 0)
                            ) + 1:
                                failures.append(
                                    f"{route}: mobile list overflows horizontally"
                                )
                    finally:
                        page.context.close()
                results["lists"][route] = route_results

            faq_page = open_page(
                browser,
                args.cms,
                FAQ_ROUTE,
                width=1440,
                height=1000,
                dark=True,
            )
            try:
                faq = inspect_faq(faq_page)
                results["faq"] = faq
                faq_page.screenshot(
                    path=str(args.output / "book-appointment--dark-faq.png"),
                    full_page=True,
                    animations="disabled",
                )
                if not faq.get("found"):
                    failures.append("book appointment: FAQ open/closed states not found")
                else:
                    if faq.get("openBackground") == faq.get("closedBackground"):
                        failures.append(
                            "book appointment: open FAQ surface is not distinct"
                        )
                    if faq.get("openBorder") == faq.get("closedBorder"):
                        failures.append(
                            "book appointment: open FAQ border is not distinct"
                        )
                    if faq.get("answerOpacity") != "1":
                        failures.append(
                            f"book appointment: answer opacity is {faq.get('answerOpacity')!r}"
                        )
                    ratio = contrast_ratio(
                        str(faq.get("answerColor")),
                        str(faq.get("openBackground")),
                    )
                    faq["answerContrast"] = ratio
                    if ratio < 7:
                        failures.append(
                            f"book appointment: answer contrast {ratio:.2f} is below 7.00"
                        )
            finally:
                faq_page.context.close()
        finally:
            browser.close()

    results["failures"] = failures
    (args.output / "content-rhythm.json").write_text(
        json.dumps(results, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    checks = 5
    print(f"Content rhythm audit: {checks - len(failures)}/{checks} core checks pass.")
    for failure in failures:
        print(f"- {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
