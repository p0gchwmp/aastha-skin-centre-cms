from pathlib import Path

from django.conf import settings
from django.test import SimpleTestCase


class AppointmentFrontendContractTests(SimpleTestCase):
    def setUp(self):
        self.base_template = (
            Path(settings.BASE_DIR)
            / "aastha_cms"
            / "templates"
            / "base.html"
        ).read_text(encoding="utf-8")
        self.controller = (
            Path(settings.BASE_DIR)
            / "home"
            / "static"
            / "js"
            / "appointment-form-controller.js"
        ).read_text(encoding="utf-8")

    def test_single_submission_controller_is_loaded_last(self):
        controller_position = self.base_template.index(
            "appointment-form-controller.js"
        )
        self.assertGreater(
            controller_position,
            self.base_template.index("release-v24.js"),
        )
        self.assertGreater(
            controller_position,
            self.base_template.index("site.js"),
        )

    def test_controller_owns_submit_during_capture_phase(self):
        self.assertIn('document.addEventListener(\n    "submit"', self.controller)
        self.assertIn("event.stopImmediatePropagation()", self.controller)
        self.assertIn("true\n  );", self.controller)

    def test_controller_supports_both_legacy_field_names(self):
        for field_name in (
            '"clinic", "branch"',
            '"date", "preferred_date"',
            '"time", "preferred_time"',
        ):
            self.assertIn(field_name, self.controller)
        self.assertIn("window.open(", self.controller)