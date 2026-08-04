"""Idempotent data synchronization for the exact-page simple editor."""

from __future__ import annotations

from .exact_editor import (
    extract_exact_editor_payload,
    sync_uploaded_homepage_images,
)


def sync_exact_layout_editor_fields(layout) -> list[str]:
    """Populate all simple-editor fields once and preserve every later edit.

    Every exact page contains visible text. Once any of the editor streams has
    content, the layout has already been initialized and must not be regenerated.
    This also prevents image-free pages from being rewritten on every deploy.
    """

    if layout.editable_text or layout.editable_images or layout.editable_links:
        return []

    payload = extract_exact_editor_payload(layout.html)
    layout.editable_text = [
        ("text", value) for value in payload["editable_text"]
    ]
    layout.editable_images = [
        ("image", value) for value in payload["editable_images"]
    ]
    layout.editable_links = [
        ("link", value) for value in payload["editable_links"]
    ]
    fields = ["editable_text", "editable_images", "editable_links"]
    layout.save(update_fields=fields)
    return fields


def sync_all_exact_layout_editor_fields() -> int:
    from .models import ExactPageLayout

    updated = 0
    for layout in ExactPageLayout.objects.all().iterator():
        if sync_exact_layout_editor_fields(layout):
            updated += 1
    return updated


__all__ = [
    "sync_all_exact_layout_editor_fields",
    "sync_exact_layout_editor_fields",
    "sync_uploaded_homepage_images",
]
