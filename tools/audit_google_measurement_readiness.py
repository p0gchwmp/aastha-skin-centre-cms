#!/usr/bin/env python3
"""Verify that production is ready for Search Console and GA4 measurement.

This audit intentionally checks only public, non-sensitive configuration. It
never calls Google account APIs and therefore cannot prove that a user clicked
"Verify", submitted the sitemap in Search Console, or marked a GA4 event as a
key event. It does prove that the canonical website exposes the technical
signals those account-side actions depend on.
"""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import urljoin, urlsplit
from xml.etree import ElementTree

import requests
from bs4 import BeautifulSoup


USER_AGENT = "AasthaGoogleMeasurementReadiness/1.0"
GA4_ID_RE = re.compile(r"\bG-[A-Z0-9]{6,}\b")
MEASUREMENT_ASSIGNMENT_RE = re.compile(
    r'\bconst\s+measurementId\s*=\s*["\'](?P<value>[^"\']+)["\']\s*;'
)
JS_UNICODE_ESCAPE_RE = re.compile(r"\\u([0-9A-Fa-f]{4})")
JS_HEX_ESCAPE_RE = re.compile(r"\\x([0-9A-Fa-f]{2})")
VERIFICATION_TOKEN_RE = re.compile(r"^[A-Za-z0-9_-]{8,}$")
GENERATE_LEAD_RE = re.compile(
    r'track\(\s*["\']generate_lead["\']\s*,\s*\{(?P<body>.*?)\}\s*\);',
    re.DOTALL,
)
PARAMETER_RE = re.compile(r"\b([A-Za-z_$][A-Za-z0-9_$]*)\s*:")
ALLOWED_LEAD_PARAMETERS = {
    "lead_source",
    "clinic_branch",
    "has_preferred_date",
    "has_preferred_time",
}
SENSITIVE_SELECTORS = {
    '[name="name"]',
    '[name="mobile"]',
    '[name="phone"]',
    '[name="age"]',
    '[name="gender"]',
    '[name="concern"]',
    '[name="notes"]',
    '[name="opd"]',
}


@dataclass(frozen=True)
class Check:
    name: str
    passed: bool
    detail: str


def arguments() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", required=True, help="Canonical HTTPS origin")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("audit-artifacts/google-measurement-readiness"),
    )
    return parser.parse_args()


def canonical_origin(value: str) -> str:
    parsed = urlsplit(value.strip().rstrip("/"))
    if parsed.scheme != "https" or not parsed.netloc:
        raise ValueError(f"Expected an HTTPS origin, received {value!r}")
    if parsed.path or parsed.query or parsed.fragment:
        raise ValueError(f"Base must not include path/query/fragment: {value!r}")
    return f"https://{parsed.netloc.lower()}"


def masked(value: str) -> str:
    if not value:
        return "missing"
    if len(value) <= 6:
        return "*" * len(value)
    return f"{value[:2]}…{value[-4:]} ({len(value)} chars)"


def decode_javascript_literal(value: str) -> str:
    """Decode escape sequences emitted by Django's ``escapejs`` filter.

    Django intentionally renders punctuation such as ``-`` as ``\\u002D`` in
    JavaScript string literals. The browser receives the correct GA4 ID after
    evaluating that string, so the audit must validate the decoded value rather
    than search only the raw HTML source.
    """

    value = JS_UNICODE_ESCAPE_RE.sub(
        lambda match: chr(int(match.group(1), 16)),
        value,
    )
    return JS_HEX_ESCAPE_RE.sub(
        lambda match: chr(int(match.group(1), 16)),
        value,
    )


def extract_measurement_ids(source: str) -> tuple[list[str], list[str]]:
    configured_values = [
        decode_javascript_literal(match.group("value"))
        for match in MEASUREMENT_ASSIGNMENT_RE.finditer(source)
    ]
    valid_values = [
        value for value in configured_values if GA4_ID_RE.fullmatch(value)
    ]
    if not configured_values:
        valid_values = GA4_ID_RE.findall(source)
    return sorted(set(valid_values)), configured_values


def inspect_homepage(source: str, base: str) -> tuple[list[Check], str | None]:
    soup = BeautifulSoup(source, "lxml")
    checks: list[Check] = []

    canonical_nodes = []
    for node in soup.find_all("link"):
        rel = node.get("rel", [])
        if isinstance(rel, str):
            rel = rel.split()
        if "canonical" in [str(item).lower() for item in rel]:
            canonical_nodes.append(str(node.get("href", "")).strip())
    expected_canonical = f"{base}/"
    checks.append(
        Check(
            "homepage_canonical",
            canonical_nodes == [expected_canonical],
            f"found={canonical_nodes!r}; expected={[expected_canonical]!r}",
        )
    )

    verification_tokens = [
        str(node.get("content", "")).strip()
        for node in soup.find_all(
            "meta", attrs={"name": "google-site-verification"}
        )
    ]
    valid_token = (
        len(verification_tokens) == 1
        and bool(VERIFICATION_TOKEN_RE.fullmatch(verification_tokens[0]))
    )
    token_detail = (
        masked(verification_tokens[0])
        if len(verification_tokens) == 1
        else f"found {len(verification_tokens)} tokens"
    )
    checks.append(
        Check("search_console_html_token", valid_token, token_detail)
    )

    body = soup.find("body")
    analytics_enabled = (
        body is not None
        and str(body.get("data-analytics-enabled", "")).lower() == "true"
    )
    checks.append(
        Check(
            "ga4_enabled_on_canonical",
            analytics_enabled,
            f"data-analytics-enabled={body.get('data-analytics-enabled')!r}"
            if body
            else "body element missing",
        )
    )

    measurement_ids, configured_measurement_values = extract_measurement_ids(
        source
    )
    if len(measurement_ids) == 1:
        measurement_detail = masked(measurement_ids[0])
    elif configured_measurement_values:
        measurement_detail = (
            "configured="
            + repr([masked(value) for value in configured_measurement_values])
            + f"; valid={measurement_ids!r}"
        )
    else:
        measurement_detail = "measurementId assignment missing"
    checks.append(
        Check(
            "ga4_measurement_id",
            len(measurement_ids) == 1,
            measurement_detail,
        )
    )

    eager_gtag_sources = [
        str(node.get("src", ""))
        for node in soup.find_all("script", src=True)
        if "googletagmanager.com/gtag/js" in str(node.get("src", ""))
    ]
    deferred_loader_present = all(
        marker in source
        for marker in (
            'document.createElement("script")',
            "googletagmanager.com/gtag/js",
            "window.setTimeout(loadAnalytics, 4000)",
        )
    )
    checks.append(
        Check(
            "ga4_deferred_loader",
            deferred_loader_present and not eager_gtag_sources,
            (
                "deferred loader present; no render-blocking gtag source"
                if deferred_loader_present and not eager_gtag_sources
                else f"eager_sources={eager_gtag_sources!r}; "
                f"deferred_loader={deferred_loader_present}"
            ),
        )
    )

    analytics_sources = [
        urljoin(f"{base}/", str(node.get("src", "")))
        for node in soup.find_all("script", src=True)
        if "analytics-events" in str(node.get("src", ""))
    ]
    checks.append(
        Check(
            "analytics_event_bundle_linked",
            len(analytics_sources) == 1,
            f"found={analytics_sources!r}",
        )
    )
    return checks, analytics_sources[0] if len(analytics_sources) == 1 else None


def inspect_analytics_bundle(source: str) -> list[Check]:
    checks: list[Check] = []
    match = GENERATE_LEAD_RE.search(source)
    checks.append(
        Check(
            "generate_lead_event_present",
            match is not None,
            "event call found" if match else "event call missing",
        )
    )

    if match:
        parameters = set(PARAMETER_RE.findall(match.group("body")))
        checks.append(
            Check(
                "generate_lead_parameter_allowlist",
                parameters == ALLOWED_LEAD_PARAMETERS,
                f"found={sorted(parameters)!r}; "
                f"allowed={sorted(ALLOWED_LEAD_PARAMETERS)!r}",
            )
        )
    else:
        checks.append(
            Check(
                "generate_lead_parameter_allowlist",
                False,
                "cannot inspect parameters because event call is missing",
            )
        )

    sensitive_hits = sorted(
        selector for selector in SENSITIVE_SELECTORS if selector in source
    )
    checks.append(
        Check(
            "analytics_bundle_excludes_patient_fields",
            not sensitive_hits,
            "no patient-field selectors found"
            if not sensitive_hits
            else f"found={sensitive_hits!r}",
        )
    )
    return checks


def inspect_sitemap(content: bytes, base: str) -> list[Check]:
    checks: list[Check] = []
    try:
        root = ElementTree.fromstring(content)
    except ElementTree.ParseError as exc:
        return [Check("sitemap_xml", False, f"invalid XML: {exc}")]

    locations = [
        str(node.text).strip()
        for node in root.iter()
        if node.tag.endswith("loc") and node.text
    ]
    checks.append(
        Check(
            "sitemap_has_urls",
            bool(locations),
            f"URL count={len(locations)}",
        )
    )

    base_host = urlsplit(base).netloc.lower()
    invalid_locations = []
    for location in locations:
        parsed = urlsplit(location)
        if (
            parsed.scheme != "https"
            or parsed.netloc.lower() != base_host
            or parsed.query
            or parsed.fragment
        ):
            invalid_locations.append(location)
    checks.append(
        Check(
            "sitemap_uses_canonical_origin",
            bool(locations) and not invalid_locations,
            "all sitemap URLs use the canonical HTTPS origin"
            if locations and not invalid_locations
            else f"invalid={invalid_locations[:10]!r}",
        )
    )
    return checks


def inspect_robots(source: str, base: str) -> list[Check]:
    lines = [line.strip() for line in source.splitlines() if line.strip()]
    expected_sitemap = f"Sitemap: {base}/sitemap.xml"
    return [
        Check(
            "robots_declares_sitemap",
            expected_sitemap in lines,
            f"expected {expected_sitemap!r}",
        ),
        Check(
            "robots_allows_public_crawl",
            "Disallow: /" not in lines and "Allow: /" in lines,
            f"directives={lines!r}",
        ),
    ]


def get(session: requests.Session, url: str, timeout: float) -> requests.Response:
    response = session.get(url, timeout=timeout, allow_redirects=True)
    return response


def audit(base: str, timeout: float) -> list[Check]:
    session = requests.Session()
    session.headers.update({"User-Agent": USER_AGENT})
    checks: list[Check] = []

    homepage = get(session, f"{base}/", timeout)
    checks.append(
        Check(
            "homepage_http",
            homepage.status_code == 200,
            f"HTTP {homepage.status_code}; final={homepage.url}",
        )
    )
    analytics_url = None
    if homepage.status_code == 200:
        homepage_checks, analytics_url = inspect_homepage(homepage.text, base)
        checks.extend(homepage_checks)

    if analytics_url:
        bundle = get(session, analytics_url, timeout)
        checks.append(
            Check(
                "analytics_event_bundle_http",
                bundle.status_code == 200,
                f"HTTP {bundle.status_code}; url={bundle.url}",
            )
        )
        if bundle.status_code == 200:
            checks.extend(inspect_analytics_bundle(bundle.text))

    sitemap = get(session, f"{base}/sitemap.xml", timeout)
    checks.append(
        Check(
            "sitemap_http",
            sitemap.status_code == 200,
            f"HTTP {sitemap.status_code}; content-type="
            f"{sitemap.headers.get('Content-Type', '')!r}",
        )
    )
    if sitemap.status_code == 200:
        checks.extend(inspect_sitemap(sitemap.content, base))

    robots = get(session, f"{base}/robots.txt", timeout)
    checks.append(
        Check(
            "robots_http",
            robots.status_code == 200,
            f"HTTP {robots.status_code}; content-type="
            f"{robots.headers.get('Content-Type', '')!r}",
        )
    )
    if robots.status_code == 200:
        checks.extend(inspect_robots(robots.text, base))

    return checks


def write_report(output: Path, base: str, checks: list[Check]) -> None:
    output.mkdir(parents=True, exist_ok=True)
    failed = [item for item in checks if not item.passed]
    payload = {
        "base": base,
        "checks": [asdict(item) for item in checks],
        "passed": len(checks) - len(failed),
        "failed": len(failed),
    }
    (output / "google-measurement-readiness.json").write_text(
        json.dumps(payload, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )

    rows = [
        "# Google measurement readiness",
        "",
        f"- Canonical site: `{base}`",
        f"- Passed: **{len(checks) - len(failed)}/{len(checks)}**",
        f"- Failed: **{len(failed)}**",
        "",
        "| Check | Result | Detail |",
        "|---|---|---|",
    ]
    for item in checks:
        detail = item.detail.replace("|", "\\|").replace("\n", " ")
        rows.append(
            f"| `{item.name}` | {'PASS' if item.passed else 'FAIL'} | {detail} |"
        )
    rows.extend(
        [
            "",
            "> This audit proves public technical readiness only. Search Console",
            "> ownership, sitemap submission status and GA4 key-event status must",
            "> still be confirmed inside the authenticated Google accounts.",
            "",
        ]
    )
    (output / "google-measurement-readiness.md").write_text(
        "\n".join(rows),
        encoding="utf-8",
    )


def main() -> int:
    args = arguments()
    base = canonical_origin(args.base)
    try:
        checks = audit(base, args.timeout)
    except requests.RequestException as exc:
        checks = [Check("network", False, str(exc))]

    write_report(args.output, base, checks)
    failed = [item for item in checks if not item.passed]
    print(
        f"Google measurement readiness: {len(checks) - len(failed)}/"
        f"{len(checks)} pass."
    )
    for item in failed:
        print(f"- {item.name}: {item.detail}")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
