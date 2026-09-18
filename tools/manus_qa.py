#!/usr/bin/env python3
"""Run an optional Manus API v2 read-only QA review against Aastha staging.

Requires MANUS_API_KEY. Designed for manual/CI use only; it never submits forms
or asks Manus to modify the site.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

API_ROOT = "https://api.manus.ai/v2"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--base-url",
        default="https://aastha-editorial-cms-staging.onrender.com",
        help="HTTPS origin to review",
    )
    parser.add_argument("--profile", choices=("lite", "standard", "max"), default="standard")
    parser.add_argument("--wait", action="store_true")
    parser.add_argument("--poll-seconds", type=int, default=15)
    parser.add_argument("--timeout-seconds", type=int, default=900)
    parser.add_argument("--output", type=Path)
    return parser.parse_args()


def schema() -> dict:
    return {
        "type": "object",
        "properties": {
            "summary": {"type": "string"},
            "blockers": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "page": {"type": "string"},
                        "issue": {"type": "string"},
                        "evidence": {"type": "string"},
                    },
                    "required": ["page", "issue", "evidence"],
                    "additionalProperties": False,
                },
            },
            "warnings": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "page": {"type": "string"},
                        "issue": {"type": "string"},
                        "evidence": {"type": "string"},
                    },
                    "required": ["page", "issue", "evidence"],
                    "additionalProperties": False,
                },
            },
            "checks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "name": {"type": "string"},
                        "status": {"type": "string", "enum": ["pass", "warn", "fail", "not_checked"]},
                        "notes": {"type": "string"},
                    },
                    "required": ["name", "status", "notes"],
                    "additionalProperties": False,
                },
            },
        },
        "required": ["summary", "blockers", "warnings", "checks"],
        "additionalProperties": False,
    }


def headers(key: str) -> dict[str, str]:
    return {"Content-Type": "application/json", "x-manus-api-key": key}


def create_task(key: str, base_url: str, profile: str) -> dict:
    routes = [
        "/",
        "/dr-cheena-langer/",
        "/treatments/acne-treatment/",
        "/treatments/acne-scar-treatment/",
        "/book-appointment/",
        "/locations/karan-nagar/",
        "/locations/paloura/",
        "/blog/",
    ]
    absolute_routes = "\n".join(f"- {base_url.rstrip('/')}{route}" for route in routes)
    prompt = f"""Perform a read-only pre-launch QA review of the Aastha Skin Centre editorial staging website.

Review these routes:
{absolute_routes}

Rules:
- Do not submit appointment/contact forms, send WhatsApp messages, make calls, log in, publish, or change any data.
- Review desktop and mobile layouts where possible.
- Check that the editorial UI feels coherent and readable, not template-like or cluttered.
- Verify navigation, Explore/search behavior, concern routing, treatment cards, doctor/clinic sections, obvious broken links, focus/keyboard behavior, and reduced-motion behavior where inspectable.
- Check that staging is not indexable (robots/noindex) and flag canonical/schema/SEO anomalies visible in the rendered pages.
- Flag missing/broken images, overflow, overlapping text, hidden critical content, inaccessible controls, misleading medical claims, or fake-looking metrics.
- Distinguish blockers from non-blocking warnings.
- Base findings only on what you can actually observe. If something cannot be checked, mark it not_checked.
- Return concise evidence tied to the specific page.
"""
    payload = {
        "title": "Aastha editorial staging QA",
        "agent_profile": profile,
        "interactive_mode": False,
        "hide_in_task_list": False,
        "share_visibility": "private",
        "message": {"content": prompt},
        "structured_output_schema": schema(),
    }
    response = requests.post(
        f"{API_ROOT}/task.create",
        headers=headers(key),
        json=payload,
        timeout=45,
    )
    response.raise_for_status()
    data = response.json()
    if not data.get("ok"):
        raise RuntimeError(json.dumps(data, indent=2))
    return data


def poll_result(key: str, task_id: str, timeout_seconds: int, poll_seconds: int) -> dict:
    deadline = time.monotonic() + timeout_seconds
    last_status = "running"
    while time.monotonic() < deadline:
        response = requests.get(
            f"{API_ROOT}/task.listMessages",
            headers={"x-manus-api-key": key},
            params={"task_id": task_id, "order": "desc", "limit": 80},
            timeout=45,
        )
        response.raise_for_status()
        data = response.json()
        if not data.get("ok"):
            raise RuntimeError(json.dumps(data, indent=2))

        for message in data.get("messages", []):
            if message.get("type") == "structured_output_result":
                result = message.get("structured_output_result", {})
                if not result.get("success"):
                    raise RuntimeError(result.get("error") or "Manus structured output failed")
                return result.get("value", {})
            if message.get("type") == "error_message":
                raise RuntimeError(message.get("error_message", {}).get("content", "Manus task failed"))
            if message.get("type") == "status_update":
                last_status = message.get("status_update", {}).get("agent_status", last_status)
                if last_status == "error":
                    raise RuntimeError("Manus task entered error state")
                if last_status == "waiting":
                    raise RuntimeError("Manus task unexpectedly requires user input")

        time.sleep(max(3, poll_seconds))

    raise TimeoutError(f"Timed out waiting for Manus task; last status={last_status}")


def main() -> int:
    args = parse_args()
    key = os.environ.get("MANUS_API_KEY", "").strip()
    if not key:
        print("MANUS_API_KEY is required. Add it as a secret/environment variable.", file=sys.stderr)
        return 2

    task = create_task(key, args.base_url, args.profile)
    print(f"Created Manus QA task: {task['task_url']}")
    output = {
        "task_id": task["task_id"],
        "task_url": task["task_url"],
        "base_url": args.base_url,
    }

    if args.wait:
        output["result"] = poll_result(
            key,
            task["task_id"],
            args.timeout_seconds,
            args.poll_seconds,
        )
        print(json.dumps(output["result"], indent=2, ensure_ascii=False))

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
        print(f"Wrote {args.output}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
