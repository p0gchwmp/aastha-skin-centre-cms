#!/usr/bin/env python3
"""Crawl the canonical sitemap and verify the clinic's SEO foundation."""

from __future__ import annotations

import argparse
import json
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from urllib.parse import urljoin, urlsplit, urlunsplit
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup


USER_AGENT = "AasthaSEOFoundationAudit/1.0"


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="Canonical HTTPS origin")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--max-pages", type=int, default=0)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("audit-artifacts/seo-foundation"),
    )
    return parser.parse_args()


def origin(value: str) -> str:
    parsed = urlsplit(value.strip().rstrip("/"))
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"Expected an HTTPS origin, received {value!r}")
    if parsed.path or parsed.query or parsed.fragment:
        raise ValueError(f"Base must not include path/query/fragment: {value!r}")
    return f"https://{parsed.netloc.lower()}"


def canonicalize_url(value: str) -> str:
    parsed = urlsplit(value)
    path = parsed.path or "/"
    return urlunsplit((parsed.scheme.lower(), parsed.netloc.lower(), path, "", ""))


def meta_content(soup: BeautifulSoup, name: str) -> list[str]:
    return [
        str(node.get("content", "")).strip()
        for node in soup.find_all("meta", attrs={"name": name})
    ]


def canonical_links(soup: BeautifulSoup) -> list[str]:
    output = []
    for node in soup.find_all("link"):
        rel = node.get("rel", [])
        if isinstance(rel, str):
            rel = rel.split()
        if "canonical" in [str(item).lower() for item in rel]:
            output.append(str(node.get("href", "")).strip())
    return output


def schema_types(value) -> list[str]:
    output: list[str] = []
    if isinstance(value, dict):
        entity_type = value.get("@type")
        if isinstance(entity_type, str):
            output.append(entity_type)
        elif isinstance(entity_type, list):
            output.extend(str(item) for item in entity_type)
        for item in value.values():
            output.extend(schema_types(item))
    elif isinstance(value, list):
        for item in value:
            output.extend(schema_types(item))
    return output


def parse_json_ld(soup: BeautifulSoup) -> tuple[list[object], list[str]]:
    payloads: list[object] = []
    errors: list[str] = []
    for index, node in enumerate(
        soup.find_all("script", attrs={"type": "application/ld+json"}),
        start=1,
    ):
        try:
            payloads.append(json.loads(node.string or node.get_text()))
        except json.JSONDecodeError as exc:
            errors.append(f"JSON-LD script {index}: {exc}")
    return payloads, errors


def internal_links(soup: BeautifulSoup, page_url: str, base: str) -> set[str]:
    base_host = urlsplit(base).netloc.lower()
    output: set[str] = set()
    for node in soup.find_all("a", href=True):
        raw = str(node.get("href", "")).strip()
        if not raw or raw.startswith(("#", "mailto:", "tel:", "javascript:")):
            continue
        target = urljoin(page_url, raw)
        parsed = urlsplit(target)
        if parsed.scheme not in {"http", "https"} or parsed.netloc.lower() != base_host:
            continue
        output.add(canonicalize_url(target))
    return output


def page_kind(path: str) -> str:
    parts = [part for part in path.split("/") if part]
    if len(parts) >= 2 and parts[0] == "conditions":
        return "condition"
    if len(parts) >= 2 and parts[0] == "treatments":
        return "treatment"
    if len(parts) >= 2 and parts[0] == "blog":
        return "blog"
    if parts and parts[0].startswith("dr-"):
        return "doctor"
    return "general"


def audit_page(url: str, base: str, timeout: float) -> dict[str, object]:
    client = requests.Session()
    client.headers.update({"User-Agent": USER_AGENT})
    failures: list[str] = []
    warnings: list[str] = []
    response = client.get(url, timeout=timeout)
    if response.status_code != 200:
        failures.append(f"HTTP {response.status_code}")
        return {
            "url": url,
            "status": response.status_code,
            "failures": failures,
            "warnings": warnings,
            "links": [],
            "title": "",
            "description": "",
        }

    soup = BeautifulSoup(response.text, "lxml")
    titles = [node.get_text(" ", strip=True) for node in soup.find_all("title")]
    if len(titles) != 1 or not titles[0]:
        failures.append(f"expected one non-empty title, found {titles!r}")
    title = titles[0] if titles else ""
    if title and not 20 <= len(title) <= 70:
        warnings.append(f"title length={len(title)}")

    descriptions = meta_content(soup, "description")
    if len(descriptions) != 1 or not descriptions[0]:
        failures.append(
            f"expected one non-empty meta description, found {descriptions!r}"
        )
    description = descriptions[0] if descriptions else ""
    if description and not 70 <= len(description) <= 170:
        warnings.append(f"description length={len(description)}")

    canonicals = canonical_links(soup)
    expected_canonical = canonicalize_url(url)
    if len(canonicals) != 1:
        failures.append(f"expected one canonical, found {canonicals!r}")
    elif canonicalize_url(canonicals[0]) != expected_canonical:
        failures.append(
            f"canonical={canonicals[0]!r}, expected={expected_canonical!r}"
        )

    robots_values = [value.lower() for value in meta_content(soup, "robots")]
    if any("noindex" in value for value in robots_values):
        failures.append(f"indexable sitemap URL has robots={robots_values!r}")
    if "noindex" in response.headers.get("X-Robots-Tag", "").lower():
        failures.append(
            "indexable sitemap URL has X-Robots-Tag="
            + repr(response.headers.get("X-Robots-Tag"))
        )

    h1_values = [node.get_text(" ", strip=True) for node in soup.find_all("h1")]
    if len(h1_values) != 1 or not h1_values[0]:
        failures.append(f"expected one non-empty H1, found {h1_values!r}")

    payloads, schema_errors = parse_json_ld(soup)
    failures.extend(schema_errors)
    if not payloads:
        failures.append("no JSON-LD found")
    types = schema_types(payloads)
    path = urlsplit(url).path
    if path != "/":
        for required in ("Organization", "WebSite", "BreadcrumbList"):
            if required not in types:
                failures.append(f"missing {required} schema")
        if types.count("MedicalClinic") < 2:
            failures.append("fewer than two MedicalClinic branch entities")

    kind = page_kind(path)
    if kind in {"condition", "treatment"} and "MedicalWebPage" not in types:
        failures.append("missing MedicalWebPage schema")
    if kind == "condition" and "MedicalCondition" not in types:
        failures.append("missing MedicalCondition schema")
    if kind == "treatment" and "MedicalProcedure" not in types:
        failures.append("missing MedicalProcedure schema")
    if kind == "blog" and "BlogPosting" not in types:
        failures.append("missing BlogPosting schema")
    if kind == "doctor" and "ProfilePage" not in types:
        failures.append("missing ProfilePage schema")

    return {
        "url": url,
        "status": response.status_code,
        "title": title,
        "description": description,
        "schema_types": sorted(set(types)),
        "failures": failures,
        "warnings": warnings,
        "links": sorted(internal_links(soup, url, base)),
    }


def fetch_sitemap(base: str, timeout: float) -> list[str]:
    response = requests.get(
        f"{base}/sitemap.xml",
        timeout=timeout,
        headers={"User-Agent": USER_AGENT},
    )
    response.raise_for_status()
    root = ElementTree.fromstring(response.content)
    urls = [
        canonicalize_url(node.text.strip())
        for node in root.iter()
        if node.tag.endswith("loc") and node.text
    ]
    return list(dict.fromkeys(urls))


def check_link(url: str, timeout: float) -> tuple[str, int, str]:
    try:
        response = requests.get(
            url,
            timeout=timeout,
            allow_redirects=True,
            headers={"User-Agent": USER_AGENT},
        )
        return url, response.status_code, response.url
    except requests.RequestException as exc:
        return url, 0, str(exc)


def main() -> int:
    args = arguments()
    base = origin(args.base)
    args.output.mkdir(parents=True, exist_ok=True)

    urls = fetch_sitemap(base, args.timeout)
    if args.max_pages:
        urls = urls[: args.max_pages]
    if not urls:
        raise SystemExit("Canonical sitemap contained no URLs")

    results: list[dict[str, object]] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        future_map = {
            pool.submit(audit_page, url, base, args.timeout): url for url in urls
        }
        for future in as_completed(future_map):
            results.append(future.result())
    results.sort(key=lambda item: str(item["url"]))

    sitemap_set = {canonicalize_url(url) for url in urls}
    discovered_links = {
        canonicalize_url(link)
        for result in results
        for link in result.get("links", [])
    }
    extra_links = sorted(discovered_links - sitemap_set)
    link_failures: list[str] = []
    with ThreadPoolExecutor(max_workers=max(1, args.workers)) as pool:
        for url, status, final_url in pool.map(
            lambda value: check_link(value, args.timeout), extra_links
        ):
            if status == 0 or status >= 400:
                link_failures.append(
                    f"{url}: HTTP {status or 'error'}; final={final_url!r}"
                )

    titles = Counter(
        str(result["title"]) for result in results if result.get("title")
    )
    descriptions = Counter(
        str(result["description"])
        for result in results
        if result.get("description")
    )
    duplicate_titles = sorted(value for value, count in titles.items() if count > 1)
    duplicate_descriptions = sorted(
        value for value, count in descriptions.items() if count > 1
    )

    failures = [
        f"{result['url']}: {failure}"
        for result in results
        for failure in result.get("failures", [])
    ]
    failures.extend(f"internal link: {failure}" for failure in link_failures)
    warnings = [
        f"{result['url']}: {warning}"
        for result in results
        for warning in result.get("warnings", [])
    ]
    warnings.extend(f"duplicate title: {value!r}" for value in duplicate_titles)
    warnings.extend(
        f"duplicate description: {value!r}" for value in duplicate_descriptions
    )

    payload = {
        "base": base,
        "urls_audited": len(results),
        "results": results,
        "duplicate_titles": duplicate_titles,
        "duplicate_descriptions": duplicate_descriptions,
        "link_failures": link_failures,
        "failures": failures,
        "warnings": warnings,
    }
    (args.output / "seo-foundation.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    (args.output / "seo-foundation.md").write_text(
        "# SEO foundation audit\n\n"
        f"- URLs audited: {len(results)}\n"
        f"- Failures: {len(failures)}\n"
        f"- Warnings: {len(warnings)}\n\n"
        + "## Failures\n\n"
        + ("\n".join(f"- {item}" for item in failures) or "- None")
        + "\n\n## Warnings\n\n"
        + ("\n".join(f"- {item}" for item in warnings) or "- None")
        + "\n",
        encoding="utf-8",
    )

    print(
        f"SEO foundation audit: {len(results)} URLs, "
        f"{len(failures)} failures, {len(warnings)} warnings."
    )
    for failure in failures:
        print(f"- {failure}")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
