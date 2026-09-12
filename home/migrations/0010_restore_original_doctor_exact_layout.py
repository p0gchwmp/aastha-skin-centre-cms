# Restore the original verified Dr. Cheena Langer exact-page snapshot.

from __future__ import annotations

import base64
import gzip
import hashlib
import json
from pathlib import Path

from django.conf import settings
from django.db import migrations


PROFILE_PATH = "/dr-cheena-langer/"


def restore_original_doctor_layout(apps, schema_editor):
    ExactPageLayout = apps.get_model("home", "ExactPageLayout")
    bundle_path = Path(settings.BASE_DIR) / "seed_data" / "exact-pages.json.gz.b64"
    if not bundle_path.exists():
        raise RuntimeError(f"Exact-page bundle is missing: {bundle_path}")

    compressed = base64.b64decode(bundle_path.read_text("ascii"))
    bundle = json.loads(gzip.decompress(compressed).decode("utf-8"))
    record = bundle["pages"].get(PROFILE_PATH)
    if record is None:
        raise RuntimeError(f"Original exact-page snapshot is missing: {PROFILE_PATH}")

    source = record["html"]
    source_hash = hashlib.sha256(source.encode("utf-8")).hexdigest()
    if source_hash != record["sha256"]:
        raise RuntimeError("Dr. Cheena exact-page snapshot checksum failed")

    ExactPageLayout.objects.update_or_create(
        path=PROFILE_PATH,
        defaults={
            "html": source,
            "enabled": True,
            "source_hash": source_hash,
        },
    )


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0009_simple_exact_page_editor"),
    ]

    operations = [
        migrations.RunPython(
            restore_original_doctor_layout,
            migrations.RunPython.noop,
        ),
    ]
