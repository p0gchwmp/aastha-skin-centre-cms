"""Editor-friendly layout blocks for the Aastha website CMS."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
from wagtail import blocks
from wagtail.blocks import StructValue
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock
from wagtail.snippets.blocks import SnippetChooserBlock


SPACING_CHOICES = [
    ("none", "None"),
    ("xs", "Extra small"),
    ("sm", "Small"),
    ("md", "Medium"),
    ("lg", "Large"),
    ("xl", "Extra large"),
]

THEME_CHOICES = [
    ("default", "Default"),
    ("soft", "Soft clinic tint"),
    ("white", "White"),
    ("dark", "Dark"),
    ("accent", "Accent"),
]

WIDTH_CHOICES = [
    ("narrow", "Narrow reading width"),
    ("content", "Standard content width"),
    ("wide", "Wide"),
    ("full", "Full width"),
]


class SmartTextMixin:
    """Replace safe site-wide tokens at render time.

    Editors can write tokens such as {{ consultation_fee }} inside supported
    text fields. The value is read from Site Settings every time the page is
    rendered, so one global edit updates every use.
    """

    def render_basic(self, value, context=None):
        rendered = super().render_basic(value, context=context)
        request = (context or {}).get("request")
        if request is None:
            return rendered
        from .models import SiteSettings

        settings = SiteSettings.for_request(request)
        tokens = settings.smart_tokens()
        output = str(rendered)
        for token, replacement in tokens.items():
            output = output.replace("{{ " + token + " }}", str(replacement))
            output = output.replace("{{" + token + "}}", str(replacement))
        return mark_safe(output)


class SmartRichTextBlock(SmartTextMixin, blocks.RichTextBlock):
    pass


class LinkValue(StructValue):
    @property
    def url(self):
        global_action = self.get("global_action")
        if global_action == "primary_phone":
            return "tel:{{ primary_phone_digits }}"
        if global_action == "secondary_phone":
            return "tel:{{ secondary_phone_digits }}"
        if global_action == "whatsapp":
            return "{{ whatsapp_url }}"
        if global_action == "email":
            return "mailto:{{ email }}"
        page = self.get("page")
        if page:
            return page.url
        return self.get("external_url") or "#"


class LinkBlock(blocks.StructBlock):
    label = blocks.CharBlock(max_length=120)
    global_action = blocks.ChoiceBlock(
        required=False,
        choices=[
            ("", "No global action"),
            ("primary_phone", "Call primary clinic number"),
            ("secondary_phone", "Call secondary clinic number"),
            ("whatsapp", "Open clinic WhatsApp"),
            ("email", "Email the clinic"),
        ],
        help_text=(
            "Global actions update automatically when contact details change "
            "in Settings."
        ),
    )
    page = blocks.PageChooserBlock(required=False)
    external_url = blocks.URLBlock(required=False)
    new_tab = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Use only for an external destination when appropriate.",
    )

    def clean(self, value):
        cleaned = super().clean(value)
        destinations = [
            bool(cleaned.get("global_action")),
            bool(cleaned.get("page")),
            bool(cleaned.get("external_url")),
        ]
        if sum(destinations) == 0:
            raise ValidationError(
                "Choose a global action, an internal page or an external URL."
            )
        if sum(destinations) > 1:
            raise ValidationError(
                "Choose only one destination for this link."
            )
        return cleaned

    class Meta:
        value_class = LinkValue
        icon = "link"
        label = "Link"


class LayoutBlock(blocks.StructBlock):
    width = blocks.ChoiceBlock(choices=WIDTH_CHOICES, default="content")
    theme = blocks.ChoiceBlock(choices=THEME_CHOICES, default="default")
    text_alignment = blocks.ChoiceBlock(
        choices=[
            ("left", "Left"),
            ("center", "Centre"),
            ("right", "Right"),
        ],
        default="left",
    )
    top_spacing = blocks.ChoiceBlock(choices=SPACING_CHOICES, default="lg")
    bottom_spacing = blocks.ChoiceBlock(choices=SPACING_CHOICES, default="lg")
    anchor_id = blocks.RegexBlock(
        regex=r"^[a-z][a-z0-9-]*$",
        required=False,
        help_text="Optional page anchor, for example acne-causes.",
    )
    hide_on_mobile = blocks.BooleanBlock(required=False, default=False)
    hide_on_desktop = blocks.BooleanBlock(required=False, default=False)

    class Meta:
        icon = "cogs"
        label = "Layout and position"


class ButtonBlock(blocks.StructBlock):
    link = LinkBlock()
    style = blocks.ChoiceBlock(
        choices=[
            ("primary", "Primary"),
            ("secondary", "Secondary"),
            ("text", "Text link"),
        ],
        default="primary",
    )

    class Meta:
        icon = "link"
        label = "Button"


class HeroBlock(blocks.StructBlock):
    eyebrow = blocks.CharBlock(required=False, max_length=120)
    heading = blocks.CharBlock(max_length=180)
    introduction = blocks.TextBlock(required=False, max_length=500)
    image = ImageChooserBlock(required=False)
    video_url = blocks.URLBlock(
        required=False,
        help_text="Optional YouTube, Vimeo or directly hosted video URL.",
    )
    media_position = blocks.ChoiceBlock(
        choices=[
            ("right", "Media right"),
            ("left", "Media left"),
            ("background", "Media background"),
            ("none", "No media"),
        ],
        default="right",
    )
    buttons = blocks.ListBlock(ButtonBlock(), required=False, max_num=3)
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/hero.html"
        icon = "image"
        label = "Hero"


class RichTextSectionBlock(blocks.StructBlock):
    eyebrow = blocks.CharBlock(required=False, max_length=120)
    heading = blocks.CharBlock(required=False, max_length=220)
    body = SmartRichTextBlock(
        required=False,
        features=[
            "h2",
            "h3",
            "h4",
            "bold",
            "italic",
            "ol",
            "ul",
            "hr",
            "link",
            "document-link",
            "image",
            "blockquote",
        ],
    )
    buttons = blocks.ListBlock(ButtonBlock(), required=False, max_num=3)
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/rich_text_section.html"
        icon = "pilcrow"
        label = "Text section"


class ImageSectionBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    alt_text = blocks.CharBlock(
        required=False,
        help_text="Describe meaningful content. Leave blank for a decorative image.",
    )
    caption = blocks.CharBlock(required=False)
    link = LinkBlock(required=False)
    crop = blocks.ChoiceBlock(
        choices=[
            ("original", "Original ratio"),
            ("landscape", "Landscape"),
            ("square", "Square"),
            ("portrait", "Portrait"),
        ],
        default="landscape",
    )
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/image_section.html"
        icon = "image"
        label = "Image"


class VideoSectionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    video_url = EmbedBlock(
        help_text="Paste a YouTube, Vimeo or other supported video URL."
    )
    poster = ImageChooserBlock(required=False)
    caption = blocks.CharBlock(required=False)
    autoplay_muted = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="Autoplay is used only when the video is muted.",
    )
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/video_section.html"
        icon = "media"
        label = "Video"


class CarouselSlideBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False)
    video_url = EmbedBlock(
        required=False,
        help_text="Paste a YouTube, Vimeo or other supported video URL.",
    )
    heading = blocks.CharBlock(required=False)
    text = blocks.TextBlock(required=False, max_length=350)
    link = LinkBlock(required=False)

    def clean(self, value):
        cleaned = super().clean(value)
        if not cleaned.get("image") and not cleaned.get("video_url"):
            raise ValidationError("Each slide needs an image or video.")
        return cleaned

    class Meta:
        icon = "image"
        label = "Slide"


class CarouselBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    slides = blocks.ListBlock(CarouselSlideBlock(), min_num=1)
    autoplay = blocks.BooleanBlock(required=False, default=False)
    interval_seconds = blocks.IntegerBlock(
        required=False,
        default=6,
        min_value=3,
        max_value=15,
    )
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/carousel.html"
        icon = "image"
        label = "Image / video carousel"


class GalleryItemBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    alt_text = blocks.CharBlock(required=False)
    caption = blocks.CharBlock(required=False)
    link = LinkBlock(required=False)

    class Meta:
        icon = "image"
        label = "Gallery item"


class GalleryBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    columns = blocks.ChoiceBlock(
        choices=[("2", "Two"), ("3", "Three"), ("4", "Four")],
        default="3",
    )
    items = blocks.ListBlock(GalleryItemBlock(), min_num=1)
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/gallery.html"
        icon = "image"
        label = "Gallery"


class CardBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False)
    eyebrow = blocks.CharBlock(required=False)
    heading = blocks.CharBlock()
    text = blocks.TextBlock(required=False, max_length=450)
    link = LinkBlock(required=False)

    class Meta:
        icon = "form"
        label = "Card"


class CardGridBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    introduction = blocks.TextBlock(required=False)
    columns = blocks.ChoiceBlock(
        choices=[("2", "Two"), ("3", "Three"), ("4", "Four")],
        default="3",
    )
    cards = blocks.ListBlock(CardBlock(), min_num=1)
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/card_grid.html"
        icon = "grip"
        label = "Card grid"


class FAQItemBlock(blocks.StructBlock):
    question = blocks.CharBlock(max_length=240)
    answer = SmartRichTextBlock(
        features=["bold", "italic", "ol", "ul", "link"],
    )

    class Meta:
        icon = "help"
        label = "Question and answer"


class FAQBlock(blocks.StructBlock):
    heading = blocks.CharBlock(default="Frequently asked questions")
    items = blocks.ListBlock(FAQItemBlock(), min_num=1)
    open_first = blocks.BooleanBlock(required=False, default=False)
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/faq.html"
        icon = "help"
        label = "FAQ"


class CTASectionBlock(blocks.StructBlock):
    eyebrow = blocks.CharBlock(required=False)
    heading = blocks.CharBlock()
    text = blocks.TextBlock(required=False)
    buttons = blocks.ListBlock(ButtonBlock(), min_num=1, max_num=3)
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/cta.html"
        icon = "pick"
        label = "Call to action"


class RelatedPagesBlock(blocks.StructBlock):
    heading = blocks.CharBlock(default="Related reading")
    pages = blocks.ListBlock(
        blocks.PageChooserBlock(),
        min_num=1,
        help_text="Drag to change the order. Links stay valid if pages move.",
    )
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/related_pages.html"
        icon = "link"
        label = "Related internal pages"


class DoctorListBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    doctors = blocks.ListBlock(
        SnippetChooserBlock("home.Doctor"),
        min_num=1,
    )
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/doctors.html"
        icon = "user"
        label = "Doctors"


class ClinicListBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    clinics = blocks.ListBlock(
        SnippetChooserBlock("home.ClinicLocation"),
        min_num=1,
    )
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/clinics.html"
        icon = "site"
        label = "Clinics"


class PricingItemBlock(blocks.StructBlock):
    label = blocks.CharBlock()
    price = blocks.DecimalBlock(
        required=False,
        max_digits=10,
        decimal_places=2,
    )
    description = blocks.CharBlock(required=False)
    use_global_consultation_fee = blocks.BooleanBlock(
        required=False,
        default=False,
        help_text="When enabled, the current consultation fee is shown automatically.",
    )

    class Meta:
        icon = "tag"
        label = "Price item"


class PricingBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    items = blocks.ListBlock(PricingItemBlock(), min_num=1)
    note = blocks.TextBlock(required=False)
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/pricing.html"
        icon = "tag"
        label = "Fees and prices"


class AccordionItemBlock(blocks.StructBlock):
    heading = blocks.CharBlock()
    body = SmartRichTextBlock(
        features=[
            "h3",
            "h4",
            "bold",
            "italic",
            "ol",
            "ul",
            "link",
            "image",
        ]
    )

    class Meta:
        icon = "collapse-down"
        label = "Expandable item"


class AccordionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    items = blocks.ListBlock(AccordionItemBlock(), min_num=1)
    open_first = blocks.BooleanBlock(required=False, default=False)
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/accordion.html"
        icon = "collapse-down"
        label = "Expandable sections"


class ReusableSectionBlock(blocks.StructBlock):
    section = SnippetChooserBlock("home.ReusableSection")
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/reusable_section.html"
        icon = "snippet"
        label = "Reusable section"


class SpacerBlock(blocks.StructBlock):
    size = blocks.ChoiceBlock(choices=SPACING_CHOICES, default="md")

    class Meta:
        template = "home/blocks/spacer.html"
        icon = "arrows-up-down"
        label = "Spacer"


class AdvancedHTMLBlock(blocks.StructBlock):
    html = blocks.RawHTMLBlock(
        help_text=(
            "For trusted embed or legacy markup only. Prefer the visual "
            "blocks above for ordinary editing."
        )
    )
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/advanced_html.html"
        icon = "code"
        label = "Advanced HTML (administrators only)"


class PageBodyStreamBlock(blocks.StreamBlock):
    hero = HeroBlock()
    text = RichTextSectionBlock()
    image = ImageSectionBlock()
    video = VideoSectionBlock()
    carousel = CarouselBlock()
    gallery = GalleryBlock()
    card_grid = CardGridBlock()
    faq = FAQBlock()
    accordion = AccordionBlock()
    cta = CTASectionBlock()
    related_pages = RelatedPagesBlock()
    doctors = DoctorListBlock()
    clinics = ClinicListBlock()
    pricing = PricingBlock()
    reusable = ReusableSectionBlock()
    spacer = SpacerBlock()
    advanced_html = AdvancedHTMLBlock()

    class Meta:
        block_counts = {
            "hero": {"max_num": 1},
        }
