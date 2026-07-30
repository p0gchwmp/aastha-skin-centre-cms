#!/usr/bin/env python3
"""Verify canonical, alternate and Render hosts after DNS cutover."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup


USER_AGENT = "AasthaDomainCutoverAudit/1.0"


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--canonical",
        required=True,
        help="Final canonical origin, for example https://www.aasthaskincentre.in",
    )
    parser.add_argument(
        "--alternate",
        action="append",
        default=[],
        help="Alternate custom origin expected to redirect; may be repeated.",
    )
    parser.add_argument(
        "--render",
        required=True,
        help="Render service origin that must remain available and noindex.",
    )
    parser.add_argument("--expected-release", default="")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument(
        "--output", type=Path, default=Path("audit-artifacts/domain-cutover")
    )
    return parser.parse_args()


def origin(value: str) -> str:
    parsed = urlsplit(value.strip().rstrip("/"))
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"Expected an https origin; received {value!r}")
    if parsed.path or parsed.query or parsed.fragment:
        raise ValueError(f"Origin must not contain a path/query/fragment: {value!r}")
    return f"https://{parsed.netloc.lower()}"


def fetch(client: requests.Session, url: str, timeout: float, redirects: bool = True):
    return client.get(url, timeout=timeout, allow_redirects=redirects)


def meta_content(soup: BeautifulSoup, name: str) -> str:
    node = soup.find("meta", attrs={"name": name})
    return str(node.get("content", "")).strip() if node else ""


def property_content(soup: BeautifulSoup, name: str) -> str:
    node = soup.find("meta", attrs={"property": name})
    return str(node.get("content", "")).strip() if node else ""


def canonical_href(soup: BeautifulSoup) -> str:
    node = soup.find(
        "link",
        attrs={"rel": lambda value: value and "canonical" in value},
    )
    return str(node.get("href", "")).strip() if node else ""


def schema_urls(soup: BeautifulSoup) -> list[str]:
    output: list[str] = []

    def walk(value):
        if isinstance(value, dict):
            for key, item in value.items():
                if key in {"url", "@id"} and isinstance(item, str):
                    output.append(item)
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)

    for node in soup.find_all("script", attrs={"type": "application/ld+json"}):
        try:
            walk(json.loads(node.string or node.get_text()))
        except json.JSONDecodeError:
            output.append("<invalid-json-ld>")
    return output


def main() -> int:
    args = arguments()
    canonical = origin(args.canonical)
    render = origin(args.render)
    alternates = [origin(value) for value in args.alternate]
    args.output.mkdir(parents=True, exist_ok=True)

    client = requests.Session()
    client.headers.update({"User-Agent": USER_AGENT})
    checks: list[dict[str, object]] = []
    failures: list[str] = []

    def record(name: str, passed: bool, detail: str):
        checks.append({"name": name, "passed": passed, "detail": detail})
        if not passed:
            failures.append(f"{name}: {detail}")

    home = fetch(client, canonical + "/", args.timeout)
    record("canonical home status", home.status_code == 200, f"HTTP {home.status_code}")
    soup = BeautifulSoup(home.text, "lxml")
    robots_meta = meta_content(soup, "robots").lower()
    record(
        "canonical page indexable",
        "index" in robots_meta and "noindex" not in robots_meta,
        f"meta robots={robots_meta!r}",
    )
    record(
        "canonical response has no noindex header",
        "noindex" not in home.headers.get("X-Robots-Tag", "").lower(),
        f"X-Robots-Tag={home.headers.get('X-Robots-Tag', '')!r}",
    )
    record(
        "canonical link uses final origin",
        canonical_href(soup) == canonical + "/",
        f"canonical={canonical_href(soup)!r}",
    )
    record(
        "Open Graph URL uses final origin",
        property_content(soup, "og:url") == canonical + "/",
        f"og:url={property_content(soup, 'og:url')!r}",
    )
    bad_schema = [
        value
        for value in schema_urls(soup)
        if value == "<invalid-json-ld>"
        or (
            value.startswith(("http://", "https://"))
            and urlsplit(value).netloc.lower()
            in {
                urlsplit(canonical).netloc.lower(),
                urlsplit(render).netloc.lower(),
                *(urlsplit(item).netloc.lower() for item in alternates),
            }
            and not value.startswith(canonical)
        )
    ]
    record(
        "JSON-LD uses canonical origin",
        not bad_schema,
        "bad values=" + repr(bad_schema[:10]),
    )

    robots = fetch(client, canonical + "/robots.txt", args.timeout)
    record("canonical robots status", robots.status_code == 200, f"HTTP {robots.status_code}")
    record(
        "canonical robots allows crawling",
        "Disallow: /" not in robots.text and "Allow: /" in robots.text,
        robots.text.strip().replace("\n", " | "),
    )
    record(
        "canonical robots declares sitemap",
        f"Sitemap: {canonical}/sitemap.xml" in robots.text,
        robots.text.strip().replace("\n", " | "),
    )

    sitemap = fetch(client, canonical + "/sitemap.xml", args.timeout)
    sitemap_urls: list[str] = []
    if sitemap.status_code == 200:
        try:
            root = ElementTree.fromstring(sitemap.content)
            sitemap_urls = [
                node.text.strip()
                for node in root.iter()
                if node.tag.endswith("loc") and node.text
            ]
        except ElementTree.ParseError as exc:
            failures.append(f"canonical sitemap XML: {exc}")
    record("canonical sitemap status", sitemap.status_code == 200, f"HTTP {sitemap.status_code}")
    record(
        "sitemap contains URLs",
        bool(sitemap_urls),
        f"URLs found={len(sitemap_urls)}",
    )
    wrong_sitemap_urls = [value for value in sitemap_urls if not value.startswith(canonical)]
    record(
        "sitemap URLs use canonical origin",
        not wrong_sitemap_urls,
        "wrong URLs=" + repr(wrong_sitemap_urls[:10]),
    )

    health = fetch(client, canonical + "/healthz/", args.timeout)
    health_payload = {}
    try:
        health_payload = health.json()
    except ValueError:
        pass
    record(
        "canonical health status",
        health.status_code == 200 and health_payload.get("status") == "ok",
        f"HTTP {health.status_code}, payload={health_payload!r}",
    )
    if args.expected_release:
        record(
            "canonical release matches",
            health_payload.get("release") == args.expected_release,
            f"release={health_payload.get('release')!r}",
        )

    for alternate in alternates:
        response = fetch(
            client,
            alternate + "/treatments/acne-treatment/?cutover=1",
            args.timeout,
            redirects=False,
        )
        expected = canonical + "/treatments/acne-treatment/?cutover=1"
        record(
            f"alternate redirects permanently ({alternate})",
            response.status_code in {301, 308} and response.headers.get("Location") == expected,
            f"HTTP {response.status_code}, Location={response.headers.get('Location')!r}",
        )

    render_home = fetch(client, render + "/", args.timeout)
    render_soup = BeautifulSoup(render_home.text, "lxml")
    render_robots_meta = meta_content(render_soup, "robots").lower()
    render_header = render_home.headers.get("X-Robots-Tag", "").lower()
    record("Render alias remains available", render_home.status_code == 200, f"HTTP {render_home.status_code}")
    record(
        "Render alias remains noindex",
        "noindex" in render_robots_meta or "noindex" in render_header,
        f"meta={render_robots_meta!r}, header={render_header!r}",
    )
    record(
        "Render canonical points to final origin",
        canonical_href(render_soup) == canonical + "/",
        f"canonical={canonical_href(render_soup)!r}",
    )
    render_robots = fetch(client, render + "/robots.txt", args.timeout)
    record(
        "Render robots blocks crawling",
        render_robots.status_code == 200 and "Disallow: /" in render_robots.text,
        f"HTTP {render_robots.status_code}, body={render_robots.text.strip()!r}",
    )

    payload = {
        "canonical": canonical,
        "alternates": alternates,
        "render": render,
        "checks": checks,
        "failures": failures,
    }
    (args.output / "domain-cutover.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8"
    )
    (args.output / "domain-cutover.md").write_text(
        "# Domain cutover audit\n\n"
        + "\n".join(
            f"- {'PASS' if check['passed'] else 'FAIL'} — {check['name']}: {check['detail']}"
            for check in checks
        )
        + "\n",
        encoding="utf-8",
    )

    print(f"Domain cutover audit: {len(checks) - len(failures)}/{len(checks)} pass.")
    for failure in failures:
        print(f"- {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
