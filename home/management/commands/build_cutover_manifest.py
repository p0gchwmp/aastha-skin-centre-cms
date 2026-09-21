"""Read-only production cutover manifest for the editorial CMS release."""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor
from wagtail.models import Page, Site

from home.context_processors import _env_flag
from home.management.commands.audit_release_signoff import (
    build_release_signoff_report,
)
from home.seo_verification import build_seo_verification_state


EXPECTED_PUBLIC_ROUTE_COUNT = 96


def _pending_migrations() -> list[str]:
    executor = MigrationExecutor(connection)
    targets = executor.loader.graph.leaf_nodes()
    plan = executor.migration_plan(targets)
    return [f"{migration.app_label}.{migration.name}" for migration, _ in plan]


def build_cutover_manifest() -> dict[str, object]:
    site = Site.objects.filter(is_default_site=True).first()
    if site is None:
        raise CommandError("No default Wagtail site exists.")

    signoff = build_release_signoff_report(site)
    seo = build_seo_verification_state()
    route_count = (
        site.root_page.get_descendants(inclusive=True).live().public().count()
    )
    migrations = _pending_migrations()
    editorial_enabled = _env_flag("AASTHA_EDITORIAL_V37", False)

    unsafe_local_routes = [
        item
        for item in seo["areas"]
        if item["indexable"] and not item["fact_verified"]
    ]

    technical_blockers = []
    if route_count != EXPECTED_PUBLIC_ROUTE_COUNT:
        technical_blockers.append(
            f"public route count is {route_count}; expected {EXPECTED_PUBLIC_ROUTE_COUNT}"
        )
    if migrations:
        technical_blockers.append(
            f"{len(migrations)} unapplied migration(s) remain"
        )
    if unsafe_local_routes:
        technical_blockers.append(
            "one or more locality pages are indexable without verified service-area facts"
        )

    summary = signoff["summary"]
    human_blockers = []
    if summary["medical_pages_pending"]:
        human_blockers.append(
            f"{summary['medical_pages_pending']} medical page review(s) pending"
        )
    if summary["clinics_pending"]:
        human_blockers.append(
            f"{summary['clinics_pending']} clinic verification group(s) pending"
        )
    if summary["doctors_pending"]:
        human_blockers.append(
            f"{summary['doctors_pending']} doctor verification group(s) pending"
        )
    if summary["site_items_pending"]:
        human_blockers.append(
            f"{summary['site_items_pending']} site/media approval(s) pending"
        )
    if summary["local_search_areas_pending"]:
        human_blockers.append(
            f"{summary['local_search_areas_pending']} locality verification(s) pending"
        )

    release = (
        os.environ.get("RENDER_GIT_COMMIT")
        or os.environ.get("GIT_COMMIT")
        or "unknown"
    )
    service = os.environ.get("RENDER_SERVICE_NAME", "")

    technical_ready = not technical_blockers
    human_ready = not human_blockers

    manifest_fingerprint_source = {
        "release": release,
        "route_count": route_count,
        "pending_migrations": migrations,
        "seo_verification": seo["counts"],
        "signoff_summary": summary,
        "technical_blockers": technical_blockers,
        "human_blockers": human_blockers,
    }
    manifest_fingerprint = hashlib.sha256(
        json.dumps(manifest_fingerprint_source, sort_keys=True, ensure_ascii=False, default=str).encode("utf-8")
    ).hexdigest()

    return {
        "manifest_fingerprint": manifest_fingerprint,
        "release": release,
        "service": service,
        "site_hostname": site.hostname,
        "public_site_url": settings.PUBLIC_SITE_URL,
        "public_site_host": settings.PUBLIC_SITE_HOST,
        "editorial_v37_enabled": editorial_enabled,
        "route_count": route_count,
        "expected_route_count": EXPECTED_PUBLIC_ROUTE_COUNT,
        "pending_migrations": migrations,
        "unsafe_indexable_localities": [
            {
                "slug": item["slug"],
                "name": item["name"],
                "path": item["path"],
            }
            for item in unsafe_local_routes
        ],
        "seo_verification": seo["counts"],
        "signoff_summary": summary,
        "technical_blockers": technical_blockers,
        "human_blockers": human_blockers,
        "technical_ready": technical_ready,
        "human_ready": human_ready,
        "production_activation_ready": bool(technical_ready and human_ready),
        "explicit_go_live_required": True,
        "activation_sequence": [
            "Create and verify production database backup.",
            "Create and verify production media backup/snapshot.",
            "Record current production deploy ID and commit.",
            "Merge approved release with AASTHA_EDITORIAL_V37 still off.",
            "Deploy and verify the legacy frontend remains healthy.",
            "Run production launch configuration and release smoke tests.",
            "Only after explicit approval, enable AASTHA_EDITORIAL_V37.",
            "Smoke-test custom domain, booking, call, WhatsApp, maps, schema and sitemap.",
        ],
        "rollback": {
            "feature_flag": "AASTHA_EDITORIAL_V37=0",
            "note": (
                "Frontend parity work is feature-flagged. Disable the flag first; "
                "do not roll back the database for a frontend-only issue."
            ),
        },
    }


class Command(BaseCommand):
    help = (
        "Generate the read-only production cutover manifest. "
        "This command never changes content, indexation, flags or production data."
    )

    def add_arguments(self, parser):
        parser.add_argument("--json", type=Path, dest="json_path")
        parser.add_argument(
            "--require-ready",
            action="store_true",
            help="Return non-zero unless both technical and human signoff gates are ready.",
        )

    def handle(self, *args, **options):
        manifest = build_cutover_manifest()

        self.stdout.write(
            "Cutover manifest: "
            f"technical={'READY' if manifest['technical_ready'] else 'BLOCKED'}; "
            f"human-signoff={'READY' if manifest['human_ready'] else 'BLOCKED'}; "
            f"production-activation="
            f"{'READY' if manifest['production_activation_ready'] else 'BLOCKED'}."
        )
        self.stdout.write(
            f"Release {manifest['release']} · "
            f"{manifest['route_count']}/{manifest['expected_route_count']} routes · "
            f"{len(manifest['pending_migrations'])} pending migration(s)."
        )

        for blocker in manifest["technical_blockers"]:
            self.stdout.write(self.style.ERROR(f"TECHNICAL — {blocker}"))
        for blocker in manifest["human_blockers"]:
            self.stdout.write(self.style.WARNING(f"SIGNOFF — {blocker}"))

        if options.get("json_path"):
            path = options["json_path"]
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                json.dumps(manifest, indent=2, ensure_ascii=False, default=str),
                encoding="utf-8",
            )

        if options.get("require_ready") and not manifest["production_activation_ready"]:
            raise CommandError("Production activation is not ready.")
