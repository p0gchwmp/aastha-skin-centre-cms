import os
from unittest.mock import patch

from django.test import TestCase


class HealthzTests(TestCase):
    @patch.dict(
        os.environ,
        {
            "RENDER_GIT_COMMIT": "2605e3d8034f26323b359beaa9cd9eb9d26ece51",
            "RENDER_SERVICE_NAME": "aastha-skin-centre-cms",
        },
        clear=False,
    )
    def test_healthz_reports_database_and_release(self):
        response = self.client.get("/healthz/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "status": "ok",
                "release": "2605e3d8034f26323b359beaa9cd9eb9d26ece51",
                "service": "aastha-skin-centre-cms",
            },
        )
        self.assertEqual(response["Cache-Control"], "no-store")

    @patch.dict(
        os.environ,
        {
            "RENDER_GIT_COMMIT": "",
            "GIT_COMMIT": "",
            "RENDER_SERVICE_NAME": "",
        },
        clear=False,
    )
    def test_healthz_has_safe_fallback_outside_render(self):
        response = self.client.get("/healthz/")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok", "release": "unknown"})
