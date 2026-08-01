import json
from pathlib import Path
from tempfile import TemporaryDirectory

from django.test import SimpleTestCase

from tools.summarize_lighthouse import collect_reports, render_markdown


class LighthouseSummaryTests(SimpleTestCase):
    def test_report_collection_and_markdown_scorecard(self):
        with TemporaryDirectory() as directory:
            root = Path(directory)
            reports = root / "lighthouse-mobile"
            reports.mkdir()
            report = {
                "finalUrl": "http://127.0.0.1:8000/example/",
                "requestedUrl": "http://127.0.0.1:8000/example/",
                "categories": {
                    "performance": {"score": 0.97},
                    "accessibility": {"score": 1.0},
                    "best-practices": {"score": 1.0},
                    "seo": {"score": 1.0},
                },
                "audits": {
                    "first-contentful-paint": {"numericValue": 1234},
                    "largest-contentful-paint": {"numericValue": 2456},
                    "cumulative-layout-shift": {"numericValue": 0.012},
                    "total-blocking-time": {"numericValue": 89},
                },
            }
            (reports / "example.report.json").write_text(
                json.dumps(report),
                encoding="utf-8",
            )

            rows = collect_reports(root)
            markdown = render_markdown(rows)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["route"], "/example/")
        self.assertEqual(rows[0]["performance"], 97)
        self.assertIn("| Mobile | `/example/` | 97 | 100 | 100 | 100 |", markdown)
        self.assertIn("1.23s", markdown)
        self.assertIn("2.46s", markdown)
        self.assertIn("0.012", markdown)
        self.assertIn("89ms", markdown)
        self.assertIn("Performance: **97**", markdown)
