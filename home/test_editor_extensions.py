from django.core.exceptions import ValidationError
from django.template.loader import get_template
from django.test import SimpleTestCase

from home import blocks as registered_blocks
from home.admin_extensions import extract_anchor_options
from home.editor_extensions import (
    EnhancedCardGridBlock,
    TestimonialItemBlock,
)


class ExtendedEditorBlockTests(SimpleTestCase):
    def test_full_builder_exposes_extended_structural_blocks(self):
        stream = registered_blocks.PageBodyStreamBlock()
        self.assertTrue(
            {
                "columns",
                "notice",
                "testimonials",
                "logo_strip",
                "card_grid",
            }.issubset(stream.child_blocks)
        )
        self.assertIsInstance(stream.child_blocks["card_grid"], EnhancedCardGridBlock)

    def test_exact_design_additions_expose_same_extended_blocks(self):
        stream = registered_blocks.PageAdditionStreamBlock()
        self.assertTrue(
            {
                "columns",
                "notice",
                "testimonials",
                "logo_strip",
                "card_grid",
            }.issubset(stream.child_blocks)
        )

    def test_extended_templates_are_loadable(self):
        for template_name in (
            "home/blocks/enhanced_card_grid.html",
            "home/blocks/general_columns.html",
            "home/blocks/notice.html",
            "home/blocks/testimonials.html",
            "home/blocks/logo_strip.html",
        ):
            self.assertIsNotNone(get_template(template_name))

    def test_patient_story_requires_confirmed_consent(self):
        block = TestimonialItemBlock()
        value = block.to_python(
            {
                "quote": "The consultation helped me understand my options.",
                "person_name": "A patient",
                "role_or_context": "",
                "photo": None,
                "is_patient_story": True,
                "consent_confirmed": False,
                "internal_source_note": "",
            }
        )
        with self.assertRaisesMessage(
            ValidationError,
            "Written consent must be confirmed for a patient story.",
        ):
            block.clean(value)


class PlacementMapExtractionTests(SimpleTestCase):
    def test_extracts_only_compatible_article_section_anchors(self):
        source = """
        <main>
          <section class="page-hero" id="hero"><h1>Acne</h1></section>
          <section class="article-section">
            <h2 id="what-is-acne">What is acne?</h2>
            <p>Body</p>
          </section>
          <section class="article-section other-class">
            <div id="treatment-options"></div>
            <h2><span>Treatment</span> options</h2>
          </section>
          <footer id="footer-anchor"></footer>
        </main>
        """
        self.assertEqual(
            extract_anchor_options(source),
            [
                {"id": "what-is-acne", "label": "What is acne?"},
                {"id": "treatment-options", "label": "Treatment options"},
            ],
        )

    def test_duplicate_anchor_is_returned_once(self):
        source = """
        <section class="article-section"><h2 id="same-anchor">First</h2></section>
        <section class="article-section"><h2 id="same-anchor">Second</h2></section>
        """
        self.assertEqual(
            extract_anchor_options(source),
            [{"id": "same-anchor", "label": "First"}],
        )
