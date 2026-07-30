#!/usr/bin/env python3
"""Audit the deployed CMS against the retained static reference site.

This script deliberately checks the live HTTP responses rather than trusting the
snapshot bundle alone. It compares all 75 legacy routes, validates metadata and
structured data, checks internal destinations, and writes machine-readable and
human-readable reports.
"""

from __future__ import annotations

import argparse
import base64
import gzip
import hashlib
import json
import re
import sys
import time
from collections import Counter
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable
from urllib.parse import urljoin, urlsplit, urlunsplit

import requests
from bs4 import BeautifulSoup, NavigableString, Tag


ROOT = Path(__file__).resolve().parents[1]
BUNDLE = ROOT / "seed_data" / "exact-pages.json.gz.b64"
DEFAULT_CMS = "https://aastha-skin-centre-cms.onrender.com"
DEFAULT_STATIC = "https://aastha-skin-centre-staging.onrender.com"
USER_AGENT = "AasthaPrelaunchAudit/1.0 (+website parity verification)"
SPACE = re.compile(r"\s+")


@dataclass
class RouteResult:
    path: str
    static_status: int | None = None
    cms_status: int | None = None
    static_main_hash: str = ""
    cms_main_hash: str = ""
    h1_static: list[str] = field(default_factory=list)
    h1_cms: list[str] = field(default_factory=list)
    headings_match: bool = False
    disclosure_match: bool = False
    forms_match: bool = False
    main_match: bool = False
    metadata_errors: list[str] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return not self.errors and not self.metadata_errors


def parser() -> argparse.ArgumentParser:
    command = argparse.ArgumentParser()
    command.add_argument("--cms", default=DEFAULT_CMS)
    command.add_argument("--static", default=DEFAULT_STATIC)
    command.add_argument("--output", type=Path, default=Path("audit-artifacts"))
    command.add_argument("--timeout", type=float, default=45.0)
    command.add_argument("--retries", type=int, default=4)
    command.add_argument(
        "--allow-main-differences",
        action="store_true",
        help="Record exact-main differences without failing the audit.",
    )
    return command


def load_routes() -> list[str]:
    raw = base64.b64decode(BUNDLE.read_text("ascii"))
    data = json.loads(gzip.decompress(raw).decode("utf-8"))
    pages = data.get("pages", {})
    if len(pages) != 75:
        raise RuntimeError(f"Expected 75 legacy routes; found {len(pages)}")
    return sorted(pages)


def session() -> requests.Session:
    value = requests.Session()
    value.headers.update(
        {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml",
        }
    )
    return value


def fetch(
    client: requests.Session,
    url: str,
    timeout: float,
    retries: int,
) -> requests.Response:
    last_error: Exception | None = None
    for attempt in range(1, retries + 1):
        try:
            response = client.get(url, timeout=timeout, allow_redirects=True)
            if response.status_code < 500:
                return response
            last_error = RuntimeError(f"HTTP {response.status_code}")
        except requests.RequestException as exc:
            last_error = exc
        if attempt < retries:
            time.sleep(min(12, 2**attempt))
    raise RuntimeError(f"Could not fetch {url}: {last_error}")


def text(value: Tag | None) -> str:
    if value is None:
        return ""
    return SPACE.sub(" ", value.get_text(" ", strip=True)).strip()


def localise_url(value: str, hosts: set[str]) -> str:
    if not value:
        return value
    parts = urlsplit(value)
    if parts.netloc.lower() in hosts:
        return urlunsplit(("", "", parts.path or "/", parts.query, parts.fragment))
    return value


def normalise_main(main: Tag, hosts: set[str]) -> str:
    clone = BeautifulSoup(str(main), "lxml").find("main")
    if clone is None:
        return ""

    for node in clone.find_all(string=lambda item: isinstance(item, NavigableString)):
        collapsed = SPACE.sub(" ", str(node))
        if not collapsed.strip():
            node.extract()
        else:
            node.replace_with(collapsed)

    for element in clone.find_all(True):
        for attr in ("href", "src", "action", "poster"):
            if element.has_attr(attr):
                element[attr] = localise_url(str(element[attr]), hosts)
        if element.has_attr("class"):
            element["class"] = sorted(element.get("class", []))
        # Browser-generated and CSRF values are not part of visual parity.
        if element.name == "input" and element.get("name") == "csrfmiddlewaretoken":
            element["value"] = "<csrf>"
    return clone.decode(formatter="minimal")


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def headings(main: Tag) -> list[tuple[str, str]]:
    return [
        (node.name.lower(), text(node))
        for node in main.find_all(["h1", "h2", "h3", "h4", "h5", "h6"])
    ]


def forms(main: Tag) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    for form in main.find_all("form"):
        fields = []
        for field_node in form.find_all(["input", "select", "textarea", "button"]):
            fields.append(
                (
                    field_node.name,
                    field_node.get("name", ""),
                    field_node.get("type", ""),
                    field_node.get("data-appointment-date") is not None,
                )
            )
        output.append(
            {
                "action": form.get("action", ""),
                "method": form.get("method", "get").lower(),
                "appointment": form.get("data-appointment-form") is not None,
                "fields": fields,
            }
        )
    return output


def validate_cms_head(
    response: requests.Response,
    soup: BeautifulSoup,
    path: str,
    cms_origin: str,
) -> list[str]:
    errors: list[str] = []
    title = text(soup.title)
    description = soup.find("meta", attrs={"name": "description"})
    canonical = soup.find("link", attrs={"rel": lambda value: value and "canonical" in value})
    robots = soup.find("meta", attrs={"name": "robots"})

    if not title:
        errors.append("missing document title")
    if not description or not str(description.get("content", "")).strip():
        errors.append("missing meta description")
    if not canonical or not str(canonical.get("href", "")).strip():
        errors.append("missing canonical")
    else:
        expected_path = path if path == "/" else path.rstrip("/") + "/"
        actual_path = urlsplit(str(canonical.get("href"))).path
        if actual_path != expected_path:
            errors.append(f"canonical path is {actual_path!r}, expected {expected_path!r}")

    # Both Render URLs are staging services and must remain non-indexable.
    meta_robots = str(robots.get("content", "")).lower() if robots else ""
    header_robots = response.headers.get("X-Robots-Tag", "").lower()
    if "noindex" not in meta_robots and "noindex" not in header_robots:
        errors.append("staging response is indexable")

    for index, script in enumerate(soup.find_all("script", attrs={"type": "application/ld+json"}), 1):
        try:
            json.loads(script.string or script.get_text())
        except (TypeError, json.JSONDecodeError) as exc:
            errors.append(f"invalid JSON-LD block {index}: {exc}")

    if response.url.rstrip("/") != urljoin(cms_origin.rstrip("/") + "/", path).rstrip("/"):
        errors.append(f"unexpected redirect target {response.url}")
    return errors


def internal_destinations(soup: BeautifulSoup, origin: str) -> set[str]:
    host = urlsplit(origin).netloc.lower()
    output: set[str] = set()
    for node in soup.find_all(["a", "img", "script", "link"], href=True):
        raw = str(node.get("href", ""))
        parts = urlsplit(urljoin(origin + "/", raw))
        if parts.netloc.lower() == host:
            output.add(urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, "")))
    for node in soup.find_all(["img", "script"], src=True):
        raw = str(node.get("src", ""))
        parts = urlsplit(urljoin(origin + "/", raw))
        if parts.netloc.lower() == host:
            output.add(urlunsplit((parts.scheme, parts.netloc, parts.path, parts.query, "")))
    return output


def check_destinations(
    client: requests.Session,
    urls: Iterable[str],
    timeout: float,
    retries: int,
) -> dict[str, int | str]:
    results: dict[str, int | str] = {}
    for url in sorted(urls):
        try:
            response = fetch(client, url, timeout, retries)
            results[url] = response.status_code
        except RuntimeError as exc:
            results[url] = str(exc)
    return results


def render_markdown(
    results: list[RouteResult],
    link_results: dict[str, int | str],
    cms: str,
    static: str,
) -> str:
    passed = sum(item.passed for item in results)
    lines = [
        "# Deployed website parity audit",
        "",
        f"- CMS: {cms}",
        f"- Static reference: {static}",
        f"- Legacy routes checked: {len(results)}",
        f"- Routes passing all checks: {passed}",
        f"- Internal destinations checked: {len(link_results)}",
        "",
    ]
    failures = [item for item in results if not item.passed]
    if failures:
        lines.extend(["## Route differences", ""])
        for item in failures:
            lines.append(f"### `{item.path}`")
            for error in item.errors + item.metadata_errors:
                lines.append(f"- {error}")
            lines.append("")
    else:
        lines.extend(["## Route differences", "", "None.", ""])

    broken = {
        url: status
        for url, status in link_results.items()
        if not isinstance(status, int) or status >= 400
    }
    lines.extend(["## Broken internal destinations", ""])
    if broken:
        lines.extend(f"- `{url}` — {status}" for url, status in broken.items())
    else:
        lines.append("None.")
    lines.append("")
    return "\n".join(lines)


def main() -> int:
    args = parser().parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    routes = load_routes()
    client = session()
    hosts = {
        urlsplit(args.cms).netloc.lower(),
        urlsplit(args.static).netloc.lower(),
    }
    results: list[RouteResult] = []
    cms_destinations: set[str] = set()

    for index, path in enumerate(routes, 1):
        print(f"[{index:02d}/{len(routes)}] {path}", flush=True)
        item = RouteResult(path=path)
        try:
            static_response = fetch(
                client,
                urljoin(args.static.rstrip("/") + "/", path.lstrip("/")),
                args.timeout,
                args.retries,
            )
            cms_response = fetch(
                client,
                urljoin(args.cms.rstrip("/") + "/", path.lstrip("/")),
                args.timeout,
                args.retries,
            )
            item.static_status = static_response.status_code
            item.cms_status = cms_response.status_code
            if static_response.status_code != 200:
                item.errors.append(f"static returned HTTP {static_response.status_code}")
            if cms_response.status_code != 200:
                item.errors.append(f"CMS returned HTTP {cms_response.status_code}")

            static_soup = BeautifulSoup(static_response.text, "lxml")
            cms_soup = BeautifulSoup(cms_response.text, "lxml")
            static_main = static_soup.find("main", id="main-content")
            cms_main = cms_soup.find("main", id="main-content")
            if static_main is None:
                item.errors.append("static main#main-content is missing")
            if cms_main is None:
                item.errors.append("CMS main#main-content is missing")
            if static_main is not None and cms_main is not None:
                static_normal = normalise_main(static_main, hosts)
                cms_normal = normalise_main(cms_main, hosts)
                item.static_main_hash = digest(static_normal)
                item.cms_main_hash = digest(cms_normal)
                item.main_match = static_normal == cms_normal
                item.h1_static = [text(node) for node in static_main.find_all("h1")]
                item.h1_cms = [text(node) for node in cms_main.find_all("h1")]
                item.headings_match = headings(static_main) == headings(cms_main)
                item.disclosure_match = Counter(
                    node.name for node in static_main.find_all(["details", "summary"])
                ) == Counter(
                    node.name for node in cms_main.find_all(["details", "summary"])
                )
                item.forms_match = forms(static_main) == forms(cms_main)

                if len(item.h1_cms) != 1:
                    item.errors.append(f"CMS has {len(item.h1_cms)} H1 elements")
                if not item.headings_match:
                    item.errors.append("heading hierarchy/text differs")
                if not item.disclosure_match:
                    item.errors.append("disclosure/accordion structure differs")
                if not item.forms_match:
                    item.errors.append("form structure differs")
                if not item.main_match and not args.allow_main_differences:
                    item.errors.append(
                        "normalised main markup differs "
                        f"({item.static_main_hash[:12]} != {item.cms_main_hash[:12]})"
                    )

            item.metadata_errors.extend(
                validate_cms_head(cms_response, cms_soup, path, args.cms)
            )
            cms_destinations.update(internal_destinations(cms_soup, args.cms))
        except Exception as exc:  # Keep auditing remaining routes.
            item.errors.append(str(exc))
        results.append(item)

    link_results = check_destinations(
        client,
        cms_destinations,
        args.timeout,
        args.retries,
    )
    payload = {
        "cms": args.cms,
        "static": args.static,
        "routes": [asdict(item) | {"passed": item.passed} for item in results],
        "internal_destinations": link_results,
    }
    (args.output / "deployed-parity.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (args.output / "deployed-parity.md").write_text(
        render_markdown(results, link_results, args.cms, args.static),
        encoding="utf-8",
    )

    broken_links = [
        status
        for status in link_results.values()
        if not isinstance(status, int) or status >= 400
    ]
    failed_routes = [item for item in results if not item.passed]
    print(
        f"Completed: {len(results) - len(failed_routes)}/{len(results)} routes pass; "
        f"{len(broken_links)} broken internal destinations.",
        flush=True,
    )
    return 1 if failed_routes or broken_links else 0


if __name__ == "__main__":
    raise SystemExit(main())