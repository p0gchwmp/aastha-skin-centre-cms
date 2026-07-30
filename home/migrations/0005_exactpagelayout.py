# Generated for the exact static-to-Wagtail parity release.

from __future__ import annotations

import base64
import gzip
import hashlib
import json
from pathlib import Path

from django.conf import settings
from django.db import migrations, models


def import_exact_page_layouts(apps, schema_editor):
    ExactPageLayout = apps.get_model("home", "ExactPageLayout")
    bundle_path = (
        Path(settings.BASE_DIR)
        / "seed_data"
        / "exact-pages.json.gz.b64"
    )
    if not bundle_path.exists():
        raise RuntimeError(
            f"Exact-page bundle is missing: {bundle_path}"
        )

    compressed = base64.b64decode(bundle_path.read_text("ascii"))
    bundle = json.loads(gzip.decompress(compressed).decode("utf-8"))
    for path, record in bundle["pages"].items():
        source = record["html"]
        source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
        if source_hash != record["sha256"]:
            raise RuntimeError(
                f"Exact-page snapshot checksum failed for {path}"
            )
        ExactPageLayout.objects.update_or_create(
            path=path,
            defaults={
                "html": source,
                "enabled": True,
                "source_hash": source_hash,
            },
        )


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0004_cliniclocation_expire_at_cliniclocation_expired_and_more"),
    ]

    operations = [
        migrations.CreateModel(
            name="ExactPageLayout",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "path",
                    models.CharField(
                        help_text=(
                            "Public path including leading and trailing slash."
                        ),
                        max_length=255,
                        unique=True,
                    ),
                ),
                (
                    "html",
                    models.TextField(
                        help_text=(
                            "Trusted complete <main> element. Only "
                            "administrators should edit this HTML."
                        )
                    ),
                ),
                (
                    "enabled",
                    models.BooleanField(
                        default=True,
                        help_text=(
                            "When disabled, the route uses its ordinary "
                            "Wagtail page-builder layout."
                        ),
                    ),
                ),
                (
                    "source_hash",
                    models.CharField(
                        blank=True,
                        editable=False,
                        max_length=64,
                    ),
                ),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
            options={
                "verbose_name": "Exact page layout",
                "verbose_name_plural": "Exact page layouts",
                "ordering": ["path"],
            },
        ),
        migrations.RunPython(
            import_exact_page_layouts,
            migrations.RunPython.noop,
        ),
    ]
