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
        self.analytics = (
            Path(settings.BASE_DIR)
            / "home"
            / "static"
            / "js"
            / "analytics-events.js"
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
        self.assertGreater(
            controller_position,
            self.base_template.index("analytics-events.js"),
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

    def test_appointment_event_excludes_patient_information(self):
        event_start = self.controller.index(
            'new CustomEvent("aastha:appointment-request-opened"'
        )
        event_end = self.controller.index(
            ")\n      );",
            event_start,
        )
        event_source = self.controller[event_start:event_end]
        for sensitive_name in (
            "name",
            "mobile",
            "concern",
            "patientType",
            "opd",
            "age",
            "gender",
            "note",
        ):
            self.assertNotIn(f"{sensitive_name},", event_source)
        for allowed_name in (
            "clinic",
            "hasPreferredDate",
            "hasPreferredTime",
        ):
            self.assertIn(allowed_name, event_source)

    def test_tracking_is_limited_to_the_public_canonical_site(self):
        condition = (
            "{% if site_is_public and "
            "settings.home.SiteSettings.analytics_id and not "
            "request.in_preview_panel %}"
        )
        self.assertIn(
            f'data-analytics-enabled="{condition}true',
            self.base_template,
        )
        self.assertIn(
            condition + "\n    <script>\n      (() => {",
            self.base_template,
        )
        self.assertIn("document.createElement(\"script\")", self.base_template)
        self.assertIn("window.setTimeout(loadAnalytics, 4000)", self.base_template)
        self.assertNotIn(
            '<script async src="https://www.googletagmanager.com/gtag/js',
            self.base_template,
        )
        self.assertIn('body.dataset.analyticsEnabled !== "true"', self.analytics)

    def test_conversion_events_cover_core_patient_actions(self):
        for event_name in (
            '"contact_click"',
            '"map_click"',
            '"appointment_cta_click"',
            '"outbound_profile_click"',
            '"branch_select"',
            '"generate_lead"',
        ):
            self.assertIn(event_name, self.analytics)

    def test_analytics_source_never_reads_sensitive_form_fields(self):
        for selector in (
            '[name="mobile"]',
            '[name="name"]',
            '[name="concern"]',
            '[name="notes"]',
            '[name="opd"]',
        ):
            self.assertNotIn(selector, self.analytics)


class MobileLayoutContractTests(SimpleTestCase):
    def setUp(self):
        base_dir = Path(settings.BASE_DIR)
        self.base_template = (
            base_dir / "aastha_cms" / "templates" / "base.html"
        ).read_text(encoding="utf-8")
        self.mobile_css = (
            base_dir / "aastha_cms" / "static" / "css" / "mobile-layout-qa.css"
        ).read_text(encoding="utf-8")

    def test_mobile_qa_stylesheet_is_the_final_css_layer(self):
        self.assertGreater(
            self.base_template.index("mobile-layout-qa.css"),
            self.base_template.index("layout-balance.css"),
        )

    def test_phone_card_grids_are_forced_to_one_full_width_column(self):
        self.assertIn(".concern-grid", self.mobile_css)
        self.assertIn(
            "grid-template-columns: minmax(0, 1fr) !important",
            self.mobile_css,
        )
        self.assertIn("grid-auto-flow: row !important", self.mobile_css)
        self.assertIn("grid-column: 1 / -1 !important", self.mobile_css)
        self.assertIn("width: 100% !important", self.mobile_css)
        self.assertIn("min-width: 0 !important", self.mobile_css)

    def test_sticky_mobile_actions_have_safe_content_clearance(self):
        self.assertIn(
            "padding-bottom: calc(94px + env(safe-area-inset-bottom, 0px))",
            self.mobile_css,
        )

    def test_layout_defects_are_fixed_not_hidden(self):
        self.assertNotIn("overflow-x: hidden", self.mobile_css)


class PremiumSystemV9ContractTests(SimpleTestCase):
    def setUp(self):
        base_dir = Path(settings.BASE_DIR)
        self.base_template = (
            base_dir / "aastha_cms" / "templates" / "base.html"
        ).read_text(encoding="utf-8")
        self.css = (
            base_dir / "home" / "static" / "css" / "premium-system-v9.css"
        ).read_text(encoding="utf-8")
        self.js = (
            base_dir / "home" / "static" / "js" / "premium-system-v8.js"
        ).read_text(encoding="utf-8")

    def test_v9_is_the_final_visual_authority(self):
        self.assertGreater(
            self.base_template.index("premium-system-v9.css"),
            self.base_template.index("premium-system-v8.css"),
        )

    def test_mobile_menu_lines_contrast_with_the_button(self):
        self.assertIn(".nav-toggle span:not(.sr-only)", self.css)
        self.assertIn("background: #fff8f3 !important", self.css)

    def test_accordion_marker_has_a_fixed_grid_column(self):
        self.assertIn(
            "grid-template-columns: minmax(0, 1fr) 32px !important",
            self.css,
        )
        self.assertIn("justify-self: center !important", self.css)

    def test_article_rail_uses_scroll_position_tracking(self):
        self.assertIn("const updateFromScroll", self.js)
        self.assertIn('window.addEventListener("scroll", scheduleUpdate', self.js)
        self.assertIn("documentBottom >= scrollHeight - 4", self.js)
        self.assertIn("entry.heading.getClientRects().length > 0", self.js)
        self.assertIn("if (disclosure && !disclosure.open) disclosure.open = true", self.js)
        self.assertLess(
            self.js.index("setupAccordions();\n    setupPageRail();"),
            self.js.index("setupNumberedFeatures();", self.js.index("const boot")),
        )

    def test_clinical_images_are_contained_without_cropping(self):
        self.assertIn(".clinical-results--hero .clinical-results__slide img", self.css)
        self.assertIn("object-fit: contain !important", self.css)
