#!/usr/bin/env python3
"""Verify the merged message-led visual release on the Render service."""

from __future__ import annotations

import re
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup


ORIGIN = "https://aastha-skin-centre-cms.onrender.com/"
EXPECTED_ASSETS = (
    "acne-care",
    "pigmentation-care",
    "hair-scalp-care",
    "dermatologist-diagnosis",
    "medical-experience",
    "two-clinic-locations",
    "complete-care",
    "personalised-plan",
)


def fetch(session: requests.Session, url: str) -> requests.Response:
    response = session.get(url, timeout=45)
    response.raise_for_status()
    return response


def main() -> int:
    session = requests.Session()
    session.headers["User-Agent"] = "Aastha release verifier/1.0"

    homepage = fetch(session, ORIGIN)
    soup = BeautifulSoup(homepage.text, "html.parser")

    stylesheets = [
        urljoin(homepage.url, link.get("href", ""))
        for link in soup.select('link[rel="stylesheet"][href]')
        if "site-visual-cues" in link.get("href", "")
    ]
    scripts = [
        urljoin(homepage.url, script.get("src", ""))
        for script in soup.select("script[src]")
        if "site-visual-cues" in script.get("src", "")
    ]

    if len(stylesheets) != 1:
        raise AssertionError(
            f"Expected one site-visual-cues stylesheet, found {stylesheets!r}"
        )
    if len(scripts) != 1:
        raise AssertionError(
            f"Expected one site-visual-cues script, found {scripts!r}"
        )

    stylesheet = fetch(session, stylesheets[0])
    script = fetch(session, scripts[0])
    if "message-visual--acne" not in stylesheet.text:
        raise AssertionError("Deployed stylesheet is not the message-led release")
    if "installHomepageCues" not in script.text:
        raise AssertionError("Deployed script is not the message-led release")

    referenced_urls = [
        match.strip(" \"'")
        for match in re.findall(r"url\(([^)]+message-visuals[^)]+)\)", stylesheet.text)
    ]
    resolved = [urljoin(stylesheet.url, value) for value in referenced_urls]

    for expected in EXPECTED_ASSETS:
        matches = [url for url in resolved if expected in url]
        if not matches:
            raise AssertionError(f"Missing deployed visual asset reference: {expected}")
        response = fetch(session, matches[0])
        if "svg" not in response.headers.get("content-type", "").lower():
            raise AssertionError(
                f"Unexpected content type for {expected}: "
                f"{response.headers.get('content-type')!r}"
            )

    print("Live message-led visual release verified:")
    print(f"- stylesheet: {stylesheets[0]}")
    print(f"- script: {scripts[0]}")
    print(f"- public SVG assets: {len(EXPECTED_ASSETS)}/{len(EXPECTED_ASSETS)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
