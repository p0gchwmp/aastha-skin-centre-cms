#!/usr/bin/env python3
"""Summarize Lighthouse JSON reports as a stable Markdown scorecard."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from urllib.parse import urlsplit


def _score(report: dict, category: str) -> int:
    value = report["categories"][category]["score"]
    return round(float(value) * 100)


def _numeric_value(report: dict, audit: str) -> float:
    return float(report["audits"][audit].get("numericValue") or 0)


def _route(url: str) -> str:
    return urlsplit(url).path or "/"


def collect_reports(root: Path) -> list[dict]:
    rows: list[dict] = []
    for directory in sorted(root.glob("lighthouse-*")):
        if not directory.is_dir():
            continue
        form_factor = directory.name.removeprefix("lighthouse-").title()
        for report_path in sorted(directory.glob("*.report.json")):
            report = json.loads(report_path.read_text(encoding="utf-8"))
            rows.append(
                {
                    "form_factor": form_factor,
                    "route": _route(report.get("finalUrl") or report["requestedUrl"]),
                    "performance": _score(report, "performance"),
                    "accessibility": _score(report, "accessibility"),
                    "best_practices": _score(report, "best-practices"),
                    "seo": _score(report, "seo"),
                    "fcp": _numeric_value(report, "first-contentful-paint"),
                    "lcp": _numeric_value(report, "largest-contentful-paint"),
                    "cls": _numeric_value(report, "cumulative-layout-shift"),
                    "tbt": _numeric_value(report, "total-blocking-time"),
                }
            )
    return sorted(rows, key=lambda row: (row["form_factor"], row["route"]))


def render_markdown(rows: list[dict]) -> str:
    lines = [
        "# Lighthouse scorecard",
        "",
    ]
    if not rows:
        lines.extend(["No Lighthouse JSON reports were found.", ""])
        return "\n".join(lines)

    lines.extend(
        [
            "| Form factor | Route | Performance | Accessibility | Best Practices | SEO | FCP | LCP | CLS | TBT |",
            "|---|---|---:|---:|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in rows:
        display = {
            **row,
            "fcp_seconds": row["fcp"] / 1000,
            "lcp_seconds": row["lcp"] / 1000,
        }
        lines.append(
            "| {form_factor} | `{route}` | {performance} | {accessibility} | "
            "{best_practices} | {seo} | {fcp_seconds:.2f}s | "
            "{lcp_seconds:.2f}s | {cls:.3f} | {tbt:.0f}ms |".format(**display)
        )

    lines.extend(
        [
            "",
            "## Minimum observed scores",
            "",
            f"- Performance: **{min(row['performance'] for row in rows)}**",
            f"- Accessibility: **{min(row['accessibility'] for row in rows)}**",
            f"- Best Practices: **{min(row['best_practices'] for row in rows)}**",
            f"- SEO: **{min(row['seo'] for row in rows)}**",
            f"- Maximum LCP: **{max(row['lcp'] for row in rows) / 1000:.2f}s**",
            f"- Maximum CLS: **{max(row['cls'] for row in rows):.3f}**",
            f"- Maximum TBT: **{max(row['tbt'] for row in rows):.0f}ms**",
            "",
        ]
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", type=Path, default=Path("audit-artifacts"))
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("audit-artifacts/lighthouse-summary.md"),
    )
    args = parser.parse_args()

    markdown = render_markdown(collect_reports(args.root))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(markdown, encoding="utf-8")
    print(markdown)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
