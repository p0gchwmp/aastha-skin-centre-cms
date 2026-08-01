"""Editor-friendly layout blocks for the Aastha website CMS."""

from __future__ import annotations

from django.core.exceptions import ValidationError
from django.utils.safestring import mark_safe
from wagtail import blocks
from wagtail.blocks import StructValue
from wagtail.embeds.blocks import EmbedBlock
from wagtail.images.blocks import ImageChooserBlock
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
    ("white", "White card"),
    ("dark", "Dark"),
    ("accent", "Accent"),
]

WIDTH_CHOICES = [
    ("narrow", "Narrow reading width"),
    ("content", "Standard content width"),
    ("wide", "Wide"),
    ("full", "Full width"),
]

PLACEMENT_CHOICES = [
    (
        "flow",
        "Normal flow / end of the article on an exact-design page",
    ),
    ("after_hero", "Immediately after the hero"),
    ("before_anchor", "Before an existing section anchor"),
    ("after_anchor", "After an existing section anchor"),
    ("before_sidebar", "Before the consultation sidebar / article end"),
    ("page_end", "At the end of the page"),
]

GRID_COLUMN_CHOICES = [
    ("auto", "Automatic responsive columns"),
    ("2", "Maximum two columns"),
    ("3", "Maximum three columns"),
    ("4", "Maximum four columns"),
]


class SmartTextMixin:
    """Replace safe site-wide tokens at render time."""

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
        collapsed = True


class LayoutBlock(blocks.StructBlock):
    editor_label = blocks.CharBlock(
        required=False,
        max_length=100,
        help_text=(
            "Optional internal label to help editors identify this section. "
            "It is never shown to website visitors."
        ),
    )
    placement = blocks.ChoiceBlock(
        choices=PLACEMENT_CHOICES,
        default="flow",
        help_text=(
            "Used when the page keeps its exact design. Full-builder pages "
            "follow the drag-and-drop order."
        ),
    )
    target_anchor = blocks.RegexBlock(
        regex=r"^[a-z][a-z0-9-]*$",
        required=False,
        help_text=(
            "Required only for Before/After an existing section. Use the ID "
            "shown in that section's on-page link, for example what-is-acne."
        ),
    )
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
        help_text="Optional new page anchor, for example acne-causes.",
    )
    hide_on_mobile = blocks.BooleanBlock(required=False, default=False)
    hide_on_desktop = blocks.BooleanBlock(required=False, default=False)

    def clean(self, value):
        cleaned = super().clean(value)
        placement = cleaned.get("placement")
        target = cleaned.get("target_anchor")
        if placement in {"before_anchor", "after_anchor"} and not target:
            raise ValidationError(
                "Enter the existing section anchor for this placement."
            )
        return cleaned

    class Meta:
        icon = "cogs"
        label = "Placement, spacing and responsive layout"
        collapsed = True


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
        collapsed = True


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
        label_format = "Hero: {heading}"


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
        label_format = "Text: {heading}"


class SplitContentBlock(blocks.StructBlock):
    eyebrow = blocks.CharBlock(required=False, max_length=120)
    heading = blocks.CharBlock(max_length=220)
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
    image = ImageChooserBlock(required=False)
    video_url = EmbedBlock(required=False)
    alt_text = blocks.CharBlock(required=False, max_length=220)
    media_position = blocks.ChoiceBlock(
        choices=[("right", "Media right"), ("left", "Media left")],
        default="right",
    )
    media_shape = blocks.ChoiceBlock(
        choices=[
            ("landscape", "Landscape"),
            ("square", "Square"),
            ("portrait", "Portrait"),
            ("natural", "Natural ratio"),
        ],
        default="landscape",
    )
    buttons = blocks.ListBlock(ButtonBlock(), required=False, max_num=3)
    layout = LayoutBlock()

    def clean(self, value):
        cleaned = super().clean(value)
        if cleaned.get("image") and cleaned.get("video_url"):
            raise ValidationError("Choose either an image or a video, not both.")
        return cleaned

    class Meta:
        template = "home/blocks/split_content.html"
        icon = "placeholder"
        label = "Split text and media"
        label_format = "Split section: {heading}"


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
        label_format = "Video: {heading}"


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
        if cleaned.get("image") and cleaned.get("video_url"):
            raise ValidationError("Choose either an image or video for each slide.")
        return cleaned

    class Meta:
        icon = "image"
        label = "Slide"
        collapsed = True
        label_format = "Slide: {heading}"


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
        label_format = "Carousel: {heading}"


class GalleryItemBlock(blocks.StructBlock):
    image = ImageChooserBlock()
    alt_text = blocks.CharBlock(required=False)
    caption = blocks.CharBlock(required=False)
    link = LinkBlock(required=False)

    class Meta:
        icon = "image"
        label = "Gallery item"
        collapsed = True
        label_format = "Image: {caption}"


class GalleryBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    columns = blocks.ChoiceBlock(
        choices=GRID_COLUMN_CHOICES,
        default="auto",
    )
    items = blocks.ListBlock(GalleryItemBlock(), min_num=1)
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/gallery.html"
        icon = "image"
        label = "Gallery"
        label_format = "Gallery: {heading}"


class CardBlock(blocks.StructBlock):
    image = ImageChooserBlock(required=False)
    eyebrow = blocks.CharBlock(required=False)
    heading = blocks.CharBlock()
    text = blocks.TextBlock(required=False, max_length=450)
    link = LinkBlock(required=False)

    class Meta:
        icon = "form"
        label = "Card"
        collapsed = True
        label_format = "Card: {heading}"


class CardGridBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    introduction = blocks.TextBlock(required=False)
    columns = blocks.ChoiceBlock(
        choices=GRID_COLUMN_CHOICES,
        default="auto",
    )
    cards = blocks.ListBlock(CardBlock(), min_num=1)
    equal_height = blocks.BooleanBlock(required=False, default=True)
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/card_grid.html"
        icon = "grip"
        label = "Card grid"
        label_format = "Cards: {heading}"


class FeatureItemBlock(blocks.StructBlock):
    icon_image = ImageChooserBlock(required=False)
    short_icon = blocks.CharBlock(
        required=False,
        max_length=8,
        help_text="Optional short symbol or number when no icon image is used.",
    )
    heading = blocks.CharBlock(max_length=120)
    text = blocks.TextBlock(required=False, max_length=350)
    link = LinkBlock(required=False)

    class Meta:
        icon = "success"
        label = "Feature"
        collapsed = True
        label_format = "Feature: {heading}"


class FeatureGridBlock(blocks.StructBlock):
    eyebrow = blocks.CharBlock(required=False, max_length=120)
    heading = blocks.CharBlock(required=False, max_length=220)
    introduction = blocks.TextBlock(required=False, max_length=500)
    columns = blocks.ChoiceBlock(
        choices=GRID_COLUMN_CHOICES,
        default="auto",
    )
    items = blocks.ListBlock(FeatureItemBlock(), min_num=1)
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/feature_grid.html"
        icon = "list-ul"
        label = "Feature / service grid"
        label_format = "Features: {heading}"


class StatItemBlock(blocks.StructBlock):
    value = blocks.CharBlock(max_length=40)
    label = blocks.CharBlock(max_length=120)
    context = blocks.CharBlock(required=False, max_length=220)

    class Meta:
        icon = "order"
        label = "Statistic"
        collapsed = True
        label_format = "{value} — {label}"


class StatsBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False, max_length=220)
    introduction = blocks.TextBlock(required=False, max_length=500)
    items = blocks.ListBlock(StatItemBlock(), min_num=1, max_num=6)
    source_note = blocks.CharBlock(
        required=False,
        max_length=300,
        help_text=(
            "Internal source or verification note for numeric claims. "
            "This is not displayed publicly."
        ),
    )
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/stats.html"
        icon = "order"
        label = "Statistics / trust indicators"
        label_format = "Statistics: {heading}"


class ProcessStepBlock(blocks.StructBlock):
    heading = blocks.CharBlock(max_length=160)
    text = blocks.TextBlock(required=False, max_length=450)
    image = ImageChooserBlock(required=False)
    link = LinkBlock(required=False)

    class Meta:
        icon = "list-ol"
        label = "Step"
        collapsed = True
        label_format = "Step: {heading}"


class ProcessBlock(blocks.StructBlock):
    eyebrow = blocks.CharBlock(required=False, max_length=120)
    heading = blocks.CharBlock(required=False, max_length=220)
    introduction = blocks.TextBlock(required=False, max_length=500)
    display = blocks.ChoiceBlock(
        choices=[
            ("timeline", "Vertical timeline"),
            ("cards", "Responsive cards"),
        ],
        default="timeline",
    )
    steps = blocks.ListBlock(ProcessStepBlock(), min_num=1)
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/process.html"
        icon = "list-ol"
        label = "Process / timeline"
        label_format = "Process: {heading}"


class ComparisonBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False, max_length=220)
    introduction = blocks.TextBlock(required=False, max_length=500)
    first_image = ImageChooserBlock()
    first_label = blocks.CharBlock(default="Before", max_length=80)
    first_alt_text = blocks.CharBlock(required=False, max_length=220)
    second_image = ImageChooserBlock()
    second_label = blocks.CharBlock(default="After", max_length=80)
    second_alt_text = blocks.CharBlock(required=False, max_length=220)
    note = blocks.TextBlock(
        default=(
            "Individual response, treatment plans and timelines vary. "
            "Images are informational and do not guarantee a similar result."
        ),
        max_length=500,
    )
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/comparison.html"
        icon = "image"
        label = "Two-image comparison"
        label_format = "Comparison: {heading}"


class FAQItemBlock(blocks.StructBlock):
    question = blocks.CharBlock(max_length=240)
    answer = SmartRichTextBlock(
        features=["bold", "italic", "ol", "ul", "link"],
    )

    class Meta:
        icon = "help"
        label = "Question and answer"
        collapsed = True
        label_format = "Question: {question}"


class FAQBlock(blocks.StructBlock):
    heading = blocks.CharBlock(default="Frequently asked questions")
    items = blocks.ListBlock(FAQItemBlock(), min_num=1)
    open_first = blocks.BooleanBlock(required=False, default=False)
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/faq.html"
        icon = "help"
        label = "FAQ"
        label_format = "FAQ: {heading}"


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
        label_format = "CTA: {heading}"


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
        label_format = "Related pages: {heading}"


class PageDirectoryBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False, max_length=220)
    introduction = blocks.TextBlock(required=False, max_length=500)
    source = blocks.ChoiceBlock(
        choices=[
            ("children", "All live child pages — updates automatically"),
            ("selected", "Manually selected pages"),
        ],
        default="children",
    )
    pages = blocks.ListBlock(
        blocks.PageChooserBlock(),
        required=False,
    )
    max_items = blocks.IntegerBlock(default=12, min_value=1, max_value=100)
    columns = blocks.ChoiceBlock(
        choices=GRID_COLUMN_CHOICES,
        default="auto",
    )
    layout = LayoutBlock()

    def clean(self, value):
        cleaned = super().clean(value)
        if cleaned.get("source") == "selected" and not cleaned.get("pages"):
            raise ValidationError("Select at least one page for a manual directory.")
        return cleaned

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        if value.get("source") == "children":
            current_page = (parent_context or {}).get("page")
            if current_page:
                entries = current_page.get_children().live().public().specific()
            else:
                entries = []
        else:
            entries = [page.specific for page in value.get("pages", [])]
        context["directory_pages"] = list(entries)[: value.get("max_items", 12)]
        return context

    class Meta:
        template = "home/blocks/page_directory.html"
        icon = "folder-open-inverse"
        label = "Automatic page directory"
        label_format = "Directory: {heading}"


class DoctorListBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    introduction = blocks.TextBlock(required=False, max_length=500)
    source = blocks.ChoiceBlock(
        choices=[
            ("all_active", "All active doctors — updates automatically"),
            ("manual", "Manually selected doctors"),
        ],
        default="all_active",
    )
    doctors = blocks.ListBlock(
        SnippetChooserBlock("home.Doctor"),
        required=False,
    )
    max_items = blocks.IntegerBlock(default=12, min_value=1, max_value=50)
    columns = blocks.ChoiceBlock(
        choices=GRID_COLUMN_CHOICES,
        default="auto",
    )
    show_biography = blocks.BooleanBlock(required=False, default=True)
    show_profile_link = blocks.BooleanBlock(required=False, default=True)
    layout = LayoutBlock()

    def clean(self, value):
        cleaned = super().clean(value)
        if cleaned.get("source") == "manual" and not cleaned.get("doctors"):
            raise ValidationError("Select at least one doctor for a manual list.")
        return cleaned

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        if value.get("source") == "all_active":
            from .models import Doctor

            doctors = Doctor.objects.filter(is_active=True, live=True).order_by(
                "sort_order",
                "name",
            )
        else:
            doctors = value.get("doctors", [])
        context["doctors_to_show"] = list(doctors)[: value.get("max_items", 12)]
        return context

    class Meta:
        template = "home/blocks/doctors.html"
        icon = "user"
        label = "Doctors — automatic or manual"
        label_format = "Doctors: {heading}"


class ClinicListBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    introduction = blocks.TextBlock(required=False, max_length=500)
    source = blocks.ChoiceBlock(
        choices=[
            ("all_active", "All active clinics — updates automatically"),
            ("primary", "Active primary clinics only"),
            ("manual", "Manually selected clinics"),
        ],
        default="all_active",
    )
    clinics = blocks.ListBlock(
        SnippetChooserBlock("home.ClinicLocation"),
        required=False,
    )
    max_items = blocks.IntegerBlock(default=12, min_value=1, max_value=50)
    columns = blocks.ChoiceBlock(
        choices=GRID_COLUMN_CHOICES,
        default="auto",
    )
    show_hours = blocks.BooleanBlock(required=False, default=True)
    show_contact = blocks.BooleanBlock(required=False, default=True)
    show_map_link = blocks.BooleanBlock(required=False, default=True)
    show_profile_link = blocks.BooleanBlock(required=False, default=True)
    layout = LayoutBlock()

    def clean(self, value):
        cleaned = super().clean(value)
        if cleaned.get("source") == "manual" and not cleaned.get("clinics"):
            raise ValidationError("Select at least one clinic for a manual list.")
        return cleaned

    def get_context(self, value, parent_context=None):
        context = super().get_context(value, parent_context=parent_context)
        source = value.get("source")
        if source in {"all_active", "primary"}:
            from .models import ClinicLocation

            clinics = ClinicLocation.objects.filter(is_active=True, live=True)
            if source == "primary":
                clinics = clinics.filter(is_primary=True)
            clinics = clinics.order_by("sort_order", "name")
        else:
            clinics = value.get("clinics", [])
        context["clinics_to_show"] = list(clinics)[: value.get("max_items", 12)]
        return context

    class Meta:
        template = "home/blocks/clinics.html"
        icon = "site"
        label = "Clinics — automatic or manual"
        label_format = "Clinics: {heading}"


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
        collapsed = True
        label_format = "Price: {label}"


class PricingBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    items = blocks.ListBlock(PricingItemBlock(), min_num=1)
    note = blocks.TextBlock(required=False)
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/pricing.html"
        icon = "tag"
        label = "Fees and prices"
        label_format = "Pricing: {heading}"


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
        collapsed = True
        label_format = "Item: {heading}"


class AccordionBlock(blocks.StructBlock):
    heading = blocks.CharBlock(required=False)
    items = blocks.ListBlock(AccordionItemBlock(), min_num=1)
    open_first = blocks.BooleanBlock(required=False, default=False)
    layout = LayoutBlock()

    class Meta:
        template = "home/blocks/accordion.html"
        icon = "collapse-down"
        label = "Expandable sections"
        label_format = "Accordion: {heading}"


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
    hero = HeroBlock(group="Page structure")
    text = RichTextSectionBlock(group="Content")
    split_content = SplitContentBlock(group="Content")
    image = ImageSectionBlock(group="Media")
    video = VideoSectionBlock(group="Media")
    carousel = CarouselBlock(group="Media")
    gallery = GalleryBlock(group="Media")
    comparison = ComparisonBlock(group="Media")
    card_grid = CardGridBlock(group="Cards and grids")
    feature_grid = FeatureGridBlock(group="Cards and grids")
    stats = StatsBlock(group="Cards and grids")
    process = ProcessBlock(group="Cards and grids")
    faq = FAQBlock(group="Structured content")
    accordion = AccordionBlock(group="Structured content")
    cta = CTASectionBlock(group="Links and conversion")
    related_pages = RelatedPagesBlock(group="Links and conversion")
    page_directory = PageDirectoryBlock(group="Automatic content")
    doctors = DoctorListBlock(group="Automatic content")
    clinics = ClinicListBlock(group="Automatic content")
    pricing = PricingBlock(group="Structured content")
    reusable = ReusableSectionBlock(group="Reusable content")
    spacer = SpacerBlock(group="Page structure")
    advanced_html = AdvancedHTMLBlock(group="Administrators")

    class Meta:
        block_counts = {
            "hero": {"max_num": 1},
        }


class PageAdditionStreamBlock(blocks.StreamBlock):
    """Safe visual sections that can be inserted into exact-design pages."""

    text = RichTextSectionBlock(group="Content")
    split_content = SplitContentBlock(group="Content")
    image = ImageSectionBlock(group="Media")
    video = VideoSectionBlock(group="Media")
    carousel = CarouselBlock(group="Media")
    gallery = GalleryBlock(group="Media")
    comparison = ComparisonBlock(group="Media")
    card_grid = CardGridBlock(group="Cards and grids")
    feature_grid = FeatureGridBlock(group="Cards and grids")
    stats = StatsBlock(group="Cards and grids")
    process = ProcessBlock(group="Cards and grids")
    faq = FAQBlock(group="Structured content")
    accordion = AccordionBlock(group="Structured content")
    cta = CTASectionBlock(group="Links and conversion")
    related_pages = RelatedPagesBlock(group="Links and conversion")
    page_directory = PageDirectoryBlock(group="Automatic content")
    doctors = DoctorListBlock(group="Automatic content")
    clinics = ClinicListBlock(group="Automatic content")
    pricing = PricingBlock(group="Structured content")
    reusable = ReusableSectionBlock(group="Reusable content")
