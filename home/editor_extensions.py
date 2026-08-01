"""Additional no-code blocks for complex future website editing.

The first future-editor release deliberately kept the block set conservative.
These extensions complete the documented architecture without changing existing
StreamField JSON. They subclass the original stream blocks so old content keeps
working while new section types become available immediately.
"""

from __future__ import annotations

from django.core.exceptions import ValidationError
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock

from .blocks import (
    ButtonBlock,
    CardBlock,
    CardGridBlock,
    GRID_COLUMN_CHOICES,
    LayoutBlock,
    PageAdditionStreamBlock as BasePageAdditionStreamBlock,
    PageBodyStreamBlock as BasePageBodyStreamBlock,
    SmartRichTextBlock,
)


class EnhancedCardBlock(CardBlock):
    """A card with optional visual emphasis and accessible image text."""

    image_alt_text = blocks.CharBlock(
        required=False,
        max_length=220,
        help_text=(
            "Describe meaningful image content. Leave blank only when the image "
            "is decorative."
        ),
    )
    badge = blocks.CharBlock(
        required=False,
        max_length=60,
        help_text="Optional short label such as New clinic or Popular.",
    )
    featured = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Visually emphasise this card within the grid.",
    )

    class Meta:
        icon = "form"
        label = "Card"
        collapsed = True
        label_format = "Card: {heading}"


class EnhancedCardGridBlock(CardGridBlock):
    """Card grid with editor-selectable appearance presets."""

    cards = blocks.ListBlock(EnhancedCardBlock(), min_num=1, max_num=24)
    card_style = blocks.ChoiceBlock(
        choices=[
            ("elevated", "Elevated cards"),
            ("outlined", "Outlined cards"),
            ("soft", "Soft tinted cards"),
            ("minimal", "Minimal cards"),
        ],
        default="elevated",
        help_text="Choose a consistent visual treatment for every card.",
    )
    image_ratio = blocks.ChoiceBlock(
        choices=[
            ("landscape", "Landscape images"),
            ("square", "Square images"),
            ("portrait", "Portrait images"),
            ("natural", "Keep original image ratio"),
        ],
        default="landscape",
    )
    hover_effect = blocks.BooleanBlock(
        required=False,
        default=True,
        help_text="Add a subtle hover/focus lift on devices that support it.",
    )

    class Meta:
        template = "home/blocks/enhanced_card_grid.html"
        icon = "grip"
        label = "Card grid — designable"
        label_format = "Cards: {heading}"


class ColumnItemBlock(blocks.StructBlock):
    eyebrow = blocks.CharBlock(required=False, max_length=100)
    heading = blocks.CharBlock(required=False, max_length=180)
    image = ImageChooserBlock(required=False)
    image_alt_text = blocks.CharBlock(required=False, max_length=220)
    body = SmartRichTextBlock(
        required=False,
        features=[
            "h3",
            "h4",
            "bold",
            "italic",
            "ol",
            "ul",
            "link",
            "blockquote",
        ],
    )
    buttons = blocks.ListBlock(ButtonBlock(), required=False, max_num=2)
    content_alignment = blocks.ChoiceBlock(
        choices=[
            ("top", "Align content to top"),
            ("center", "Align content to centre"),
            ("bottom", "Align content to bottom"),
        ],
        default="top",
    )

    class Meta:
        icon = "placeholder"
        label = "Column"
        collapsed = True
        label_format = "Column: {heading}"


class GeneralColumnsBlock(blocks.StructBlock):
    eyebrow = blocks.CharBlock(required=False, max_length=120)
    heading = blocks.CharBlock(required=False, max_length=220)
    introduction = blocks.TextBlock(required=False, max_length=500)
    columns = blocks.ChoiceBlock(
        choices=GRID_COLUMN_CHOICES,
        default="auto",
        help_text="The website automatically stacks columns on smaller screens.",
    )
    items = blocks.ListBlock(ColumnItemBlock(), min_num=2, max_num=6)
    equal_height = blocks.BooleanBlock(required=False, default=True)
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/general_columns.html"
        icon = "grip"
        label = "Flexible columns"
        label_format = "Columns: {heading}"


class NoticeBlock(blocks.StructBlock):
    tone = blocks.ChoiceBlock(
        choices=[
            ("information", "Information"),
            ("update", "Update / announcement"),
            ("medical", "Medical guidance"),
            ("warning", "Important warning"),
        ],
        default="information",
    )
    heading = blocks.CharBlock(max_length=180)
    body = SmartRichTextBlock(
        required=False,
        features=["bold", "italic", "ol", "ul", "link"],
    )
    buttons = blocks.ListBlock(ButtonBlock(), required=False, max_num=2)
    show_icon = blocks.BooleanBlock(required=False, default=True)
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/notice.html"
        icon = "warning"
        label = "Notice / alert"
        label_format = "Notice: {heading}"


class TestimonialItemBlock(blocks.StructBlock):
    quote = blocks.TextBlock(max_length=900)
    person_name = blocks.CharBlock(
        required=False,
        max_length=120,
        help_text="Use initials or Anonymous when privacy requires it.",
    )
    role_or_context = blocks.CharBlock(required=False, max_length=160)
    photo = ImageChooserBlock(required=False)
    is_patient_story = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Enable when this quotation is from a patient or discusses care.",
    )
    consent_confirmed = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text=(
            "Confirm written permission is on file before publishing a patient "
            "quotation or identifiable photograph."
        ),
    )
    internal_source_note = blocks.CharBlock(
        required=False,
        max_length=300,
        help_text="Internal consent/source reference. Never shown publicly.",
    )

    def clean(self, value):
        cleaned = super().clean(value)
        if cleaned.get("is_patient_story") and not cleaned.get("consent_confirmed"):
            raise ValidationError(
                "Written consent must be confirmed for a patient story."
            )
        return cleaned

    class Meta:
        icon = "openquote"
        label = "Quotation"
        collapsed = True
        label_format = "Quote: {person_name}"


class TestimonialsBlock(blocks.StructBlock):
    eyebrow = blocks.CharBlock(required=False, max_length=120)
    heading = blocks.CharBlock(required=False, max_length=220)
    introduction = blocks.TextBlock(required=False, max_length=500)
    columns = blocks.ChoiceBlock(choices=GRID_COLUMN_CHOICES, default="auto")
    items = blocks.ListBlock(TestimonialItemBlock(), min_num=1, max_num=12)
    disclaimer = blocks.CharBlock(
        required=False,
        max_length=300,
        default=(
            "Experiences are individual and do not guarantee the same outcome "
            "for another person."
        ),
    )
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/testimonials.html"
        icon = "openquote"
        label = "Testimonials / quotations"
        label_format = "Testimonials: {heading}"


class LogoItemBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    alt_text = blocks.CharBlock(max_length=180)
    label = blocks.CharBlock(required=False, max_length=120)
    link = blocks.URLBlock(required=False)

    class Meta:
        icon = "image"
        label = "Logo"
        collapsed = True
        label_format = "Logo: {label}"


class LogoStripBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False, max_length=220)
    introduction = blocks.TextBlock(required=False, max_length=400)
    items = blocks.ListBlock(LogoItemBlock(), min_num=1, max_num=16)
    monochrome = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Display logos in a quiet monochrome treatment.",
    )
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/logo_strip.html"
        icon = "image"
        label = "Logo / accreditation strip"
        label_format = "Logos: {heading}"


class ExtendedPageBodyStreamBlock(BasePageBodyStreamBlock):
    """Complete page builder including the extended structural block library."""

    card_grid = EnhancedCardGridBlock(group="Cards and grids")
    columns = GeneralColumnsBlock(group="Cards and grids")
    notice = NoticeBlock(group="Structured content")
    testimonials = TestimonialsBlock(group="Structured content")
    logo_strip = LogoStripBlock(group="Cards and grids")


class ExtendedPageAdditionStreamBlock(BasePageAdditionStreamBlock):
    """Extended sections that can be safely inserted into exact-design pages."""

    card_grid = EnhancedCardGridBlock(group="Cards and grids")
    columns = GeneralColumnsBlock(group="Cards and grids")
    notice = NoticeBlock(group="Structured content")
    testimonials = TestimonialsBlock(group="Structured content")
    logo_strip = LogoStripBlock(group="Cards and grids")
