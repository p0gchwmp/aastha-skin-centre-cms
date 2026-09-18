from __future__ import annotations

import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.core.management import call_command
from django.test import TestCase
from wagtail.models import Page, Site


class SeoContentAuditScopeTests(TestCase):
    def test_audit_is_scoped_to_default_site_tree(self):
        site = Site.objects.get(is_default_site=True)
        wagtail_root = Page.get_first_root_node()
        expected_ids = set(
            site.root_page.get_descendants(inclusive=True)
            .live()
            .public()
            .values_list("id", flat=True)
        )

        with TemporaryDirectory() as tmp:
            output = Path(tmp) / "seo-audit.json"
            call_command("audit_seo_content", json_path=output)
            payload = json.loads(output.read_text(encoding="utf-8"))

        audited_ids = {row["id"] for row in payload["pages"]}

        self.assertEqual(payload["pages_audited"], len(expected_ids))
        self.assertEqual(audited_ids, expected_ids)
        if wagtail_root.pk not in expected_ids:
            self.assertNotIn(wagtail_root.pk, audited_ids)
