"""Content models for the Aastha no-code website editor."""

from __future__ import annotations

from decimal import Decimal

from django.core.paginator import Paginator
from django.db import models
from django.utils import timezone
from modelcluster.fields import ParentalManyToManyField
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    HelpPanel,
    MultiFieldPanel,
    PublishingPanel,
)
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField, StreamField
from wagtail.images import get_image_model_string
from wagtail.models import DraftStateMixin, LockableMixin, Page, RevisionMixin
from wagtail.search import index
from wagtail.snippets.models import register_snippet

from .blocks import LinkBlock, PageAdditionStreamBlock, PageBodyStreamBlock


REVIEW_CHOICES = [
    ("draft", "Draft"),
    ("editorial", "Editorial review"),
    ("medical", "Medical review required"),
    ("approved", "Medically approved"),
    ("update_due", "Review update due"),
]

LAYOUT_MODE_CHOICES = [
    (
        "hybrid",
        "Exact design + editor additions (recommended)",
    ),
    (
        "builder",
        "Full visual page builder",
    ),
    (
        "exact",
        "Exact design only — hide editor additions",
    ),
]


@register_snippet
class ContentCategory(index.Indexed, models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    colour = models.CharField(
        max_length=7,
        default="#7b1e3a",
        help_text="Hex colour used for labels, for example #7b1e3a.",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("slug"),
        FieldPanel("description"),
        FieldPanel("colour"),
    ]

    search_fields = [
        index.SearchField("name"),
        index.SearchField("description"),
    ]

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Content categories"

    def __str__(self):
        return self.name


@register_snippet
class Doctor(
    DraftStateMixin,
    LockableMixin,
    RevisionMixin,
    index.Indexed,
    models.Model,
):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=160, unique=True)
    qualifications = models.CharField(max_length=240, blank=True)
    role = models.CharField(max_length=180, blank=True)
    registration_details = models.CharField(max_length=240, blank=True)
    photo = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    short_bio = models.TextField(blank=True)
    biography = RichTextField(blank=True)
    areas_of_interest = RichTextField(blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=30, blank=True)
    booking_label = models.CharField(
        max_length=100,
        default="Book a consultation",
    )
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    create_public_page = models.BooleanField(
        default=True,
        help_text=(
            "When this published record has no linked Doctor page, create one "
            "automatically as a draft."
        ),
    )
    publish_public_page_automatically = models.BooleanField(
        default=False,
        help_text=(
            "Publish the generated Doctor page immediately. Leave disabled to "
            "review and publish the page manually."
        ),
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("slug"),
                FieldPanel("qualifications"),
                FieldPanel("role"),
                FieldPanel("registration_details"),
            ],
            heading="Identity and credentials",
        ),
        FieldPanel("photo"),
        FieldPanel("short_bio"),
        FieldPanel("biography"),
        FieldPanel("areas_of_interest"),
        MultiFieldPanel(
            [
                FieldPanel("email"),
                FieldPanel("phone"),
                FieldPanel("booking_label"),
            ],
            heading="Contact and booking",
        ),
        MultiFieldPanel(
            [
                FieldPanel("create_public_page"),
                FieldPanel("publish_public_page_automatically"),
            ],
            heading="Website page automation",
            help_text=(
                "Automatic doctor lists update from active published records. "
                "These options additionally create and maintain a dedicated page."
            ),
        ),
        FieldRowPanel([FieldPanel("is_active"), FieldPanel("sort_order")]),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("name"),
        index.SearchField("qualifications"),
        index.SearchField("role"),
        index.SearchField("short_bio"),
    ]

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


@register_snippet
class ClinicLocation(
    DraftStateMixin,
    LockableMixin,
    RevisionMixin,
    index.Indexed,
    models.Model,
):
    name = models.CharField(max_length=160)
    slug = models.SlugField(max_length=160, unique=True)
    address = models.TextField()
    locality = models.CharField(max_length=160, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    landline = models.CharField(max_length=30, blank=True)
    mobile = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    google_maps_url = models.URLField(blank=True)
    map_embed_url = models.URLField(blank=True)
    reception_hours = models.TextField(blank=True)
    doctor_hours = models.TextField(blank=True)
    procedure_hours = models.TextField(blank=True)
    directions = RichTextField(blank=True)
    hero_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    is_primary = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    sort_order = models.PositiveIntegerField(default=0)
    create_public_page = models.BooleanField(
        default=True,
        help_text=(
            "When this published record has no linked Clinic page, create one "
            "automatically as a draft."
        ),
    )
    publish_public_page_automatically = models.BooleanField(
        default=False,
        help_text=(
            "Publish the generated Clinic page immediately. Leave disabled to "
            "review and publish the page manually."
        ),
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("name"),
                FieldPanel("slug"),
                FieldPanel("address"),
                FieldRowPanel(
                    [FieldPanel("locality"), FieldPanel("postal_code")]
                ),
            ],
            heading="Location",
        ),
        MultiFieldPanel(
            [
                FieldPanel("landline"),
                FieldPanel("mobile"),
                FieldPanel("email"),
                FieldPanel("google_maps_url"),
                FieldPanel("map_embed_url"),
            ],
            heading="Contact and maps",
        ),
        MultiFieldPanel(
            [
                FieldPanel("reception_hours"),
                FieldPanel("doctor_hours"),
                FieldPanel("procedure_hours"),
            ],
            heading="Hours",
        ),
        FieldPanel("directions"),
        FieldPanel("hero_image"),
        MultiFieldPanel(
            [
                FieldPanel("create_public_page"),
                FieldPanel("publish_public_page_automatically"),
            ],
            heading="Website page automation",
            help_text=(
                "Automatic clinic lists update from active published records. "
                "These options additionally create and maintain a dedicated page."
            ),
        ),
        FieldRowPanel(
            [
                FieldPanel("is_primary"),
                FieldPanel("is_active"),
                FieldPanel("sort_order"),
            ]
        ),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("name"),
        index.SearchField("address"),
        index.SearchField("locality"),
    ]

    class Meta:
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name


@register_snippet
class ReusableSection(
    DraftStateMixin,
    LockableMixin,
    RevisionMixin,
    index.Indexed,
    models.Model,
):
    name = models.CharField(max_length=160, unique=True)
    description = models.CharField(max_length=300, blank=True)
    body = StreamField(
        PageBodyStreamBlock(),
        blank=True,
        use_json_field=True,
    )
    is_active = models.BooleanField(default=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("name"),
        FieldPanel("description"),
        HelpPanel(
            content=(
                "<p>Reusable sections can be inserted on many pages. Editing "
                "and publishing this record updates every page that uses it.</p>"
            )
        ),
        FieldPanel("body"),
        FieldPanel("is_active"),
        PublishingPanel(),
    ]

    search_fields = [
        index.SearchField("name"),
        index.SearchField("description"),
    ]

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


@register_setting(icon="cog")
class SiteSettings(BaseSiteSetting):
    clinic_name = models.CharField(
        max_length=180,
        default="Aastha Skin & Dermato-Cosmetic Centre",
    )
    short_name = models.CharField(
        max_length=100,
        default="Aastha Skin Centre",
    )
    tagline = models.CharField(
        max_length=180,
        default="Dermatologist-led skin, hair and laser care in Jammu",
    )
    logo = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    favicon = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    default_social_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    consultation_fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal("500.00"),
    )
    currency_symbol = models.CharField(max_length=5, default="₹")
    follow_up_days = models.PositiveIntegerField(default=10)
    follow_up_included = models.BooleanField(default=True)
    fee_note = models.CharField(
        max_length=300,
        default=(
            "One follow-up consultation for the same concern is included "
            "within the stated period. Medicines, tests and procedures are separate."
        ),
    )

    primary_mobile = models.CharField(max_length=30, default="7006613362")
    secondary_mobile = models.CharField(max_length=30, default="9796676541")
    whatsapp_mobile = models.CharField(max_length=30, default="7006613362")
    email = models.EmailField(default="aasthaskinsurgs@gmail.com")
    appointment_confirmation_text = models.TextField(
        default=(
            "Submitting the form requests an appointment. It is confirmed "
            "only after the clinic contacts you."
        )
    )
    emergency_note = models.TextField(
        default="Clinic phone numbers are not emergency-service numbers."
    )

    instagram_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)

    header_navigation = StreamField(
        [("link", LinkBlock())],
        blank=True,
        use_json_field=True,
    )
    footer_navigation = StreamField(
        [("link", LinkBlock())],
        blank=True,
        use_json_field=True,
    )
    footer_text = RichTextField(blank=True)
    global_banner_text = models.CharField(max_length=240, blank=True)
    global_banner_link = models.URLField(blank=True)
    show_global_banner = models.BooleanField(default=False)

    medical_disclaimer = models.TextField(
        default=(
            "Results may vary from person to person. This content is for "
            "informational purposes only and does not substitute a consultation "
            "with a qualified medical professional."
        )
    )
    default_meta_description = models.CharField(
        max_length=160,
        default=(
            "Dermatologist-led skin, hair, laser and cosmetic care at Aastha "
            "Skin Centre in Jammu."
        ),
    )
    analytics_id = models.CharField(max_length=80, blank=True)
    search_console_verification = models.CharField(max_length=180, blank=True)

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("clinic_name"),
                FieldPanel("short_name"),
                FieldPanel("tagline"),
                FieldPanel("logo"),
                FieldPanel("favicon"),
                FieldPanel("default_social_image"),
            ],
            heading="Brand",
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("consultation_fee"),
                        FieldPanel("currency_symbol"),
                        FieldPanel("follow_up_days"),
                    ]
                ),
                FieldPanel("follow_up_included"),
                FieldPanel("fee_note"),
            ],
            heading="Global fees and policy",
        ),
        MultiFieldPanel(
            [
                FieldPanel("primary_mobile"),
                FieldPanel("secondary_mobile"),
                FieldPanel("whatsapp_mobile"),
                FieldPanel("email"),
                FieldPanel("appointment_confirmation_text"),
                FieldPanel("emergency_note"),
            ],
            heading="Contact and appointments",
        ),
        MultiFieldPanel(
            [
                FieldPanel("instagram_url"),
                FieldPanel("youtube_url"),
                FieldPanel("facebook_url"),
            ],
            heading="Social media",
        ),
        MultiFieldPanel(
            [
                FieldPanel("header_navigation"),
                FieldPanel("footer_navigation"),
                FieldPanel("footer_text"),
                FieldPanel("show_global_banner"),
                FieldPanel("global_banner_text"),
                FieldPanel("global_banner_link"),
            ],
            heading="Navigation, footer and announcement",
        ),
        MultiFieldPanel(
            [
                FieldPanel("medical_disclaimer"),
                FieldPanel("default_meta_description"),
                FieldPanel("analytics_id"),
                FieldPanel("search_console_verification"),
            ],
            heading="Compliance, SEO and analytics",
        ),
    ]

    def smart_tokens(self) -> dict[str, str]:
        fee = f"{self.currency_symbol}{self.consultation_fee:,.0f}"
        whatsapp = re_digits(self.whatsapp_mobile)
        return {
            "clinic_name": self.clinic_name,
            "clinic_short_name": self.short_name,
            "consultation_fee": fee,
            "follow_up_days": str(self.follow_up_days),
            "primary_phone": self.primary_mobile,
            "primary_phone_digits": self.primary_phone_digits,
            "secondary_phone": self.secondary_mobile,
            "secondary_phone_digits": self.secondary_phone_digits,
            "whatsapp_phone": self.whatsapp_mobile,
            "whatsapp_phone_digits": whatsapp,
            "whatsapp_url": f"https://wa.me/91{whatsapp[-10:]}",
            "email": self.email,
        }

    @property
    def primary_phone_digits(self) -> str:
        return re_digits(self.primary_mobile)

    @property
    def secondary_phone_digits(self) -> str:
        return re_digits(self.secondary_mobile)

    @property
    def whatsapp_url(self) -> str:
        digits = re_digits(self.whatsapp_mobile)
        return f"https://wa.me/91{digits[-10:]}"


def re_digits(value: str) -> str:
    return "".join(character for character in value if character.isdigit())


@register_snippet
class ExactPageLayout(models.Model):
    """Verified static-page markup used by the public parity renderer."""

    path = models.CharField(
        max_length=255,
        unique=True,
        help_text="Public path including leading and trailing slash.",
    )
    html = models.TextField(
        help_text=(
            "Trusted complete <main> element. Only administrators should edit "
            "this HTML."
        )
    )
    enabled = models.BooleanField(
        default=True,
        help_text=(
            "When disabled, the route uses its ordinary Wagtail page-builder "
            "layout."
        ),
    )
    source_hash = models.CharField(max_length=64, blank=True, editable=False)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("path"),
        FieldPanel("enabled"),
        FieldPanel("html"),
    ]

    class Meta:
        ordering = ["path"]
        verbose_name = "Exact page layout"
        verbose_name_plural = "Exact page layouts"

    def __str__(self):
        return self.path


class BaseFlexiblePage(Page):
    layout_mode = models.CharField(
        max_length=20,
        choices=LAYOUT_MODE_CHOICES,
        default="hybrid",
        help_text=(
            "Hybrid keeps the verified design and inserts sections from the "
            "Exact-design additions field. Builder replaces the exact design "
            "with the Full page builder."
        ),
    )
    eyebrow = models.CharField(max_length=120, blank=True)
    introduction = models.TextField(blank=True)
    hero_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    hero_video_url = models.URLField(blank=True)
    hero_media_position = models.CharField(
        max_length=20,
        choices=[
            ("right", "Right"),
            ("left", "Left"),
            ("background", "Background"),
            ("none", "None"),
        ],
        default="right",
    )
    layout_additions = StreamField(
        PageAdditionStreamBlock(),
        blank=True,
        use_json_field=True,
        help_text=(
            "Sections added here appear inside the current exact design. "
            "Each section has its own Placement, spacing and responsive layout."
        ),
    )
    body = StreamField(
        PageBodyStreamBlock(),
        blank=True,
        use_json_field=True,
        help_text=(
            "Complete replacement layout used when Rendering mode is Full "
            "visual page builder."
        ),
    )
    categories = ParentalManyToManyField(
        ContentCategory,
        blank=True,
        related_name="+",
    )
    show_consultation_sidebar = models.BooleanField(default=True)
    show_clinic_choices = models.BooleanField(default=True)
    show_medical_disclaimer = models.BooleanField(default=True)
    review_status = models.CharField(
        max_length=20,
        choices=REVIEW_CHOICES,
        default="medical",
    )
    reviewed_by = models.ForeignKey(
        Doctor,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    medical_review_date = models.DateField(null=True, blank=True)
    next_review_date = models.DateField(null=True, blank=True)
    canonical_url_override = models.URLField(blank=True)
    social_image = models.ForeignKey(
        get_image_model_string(),
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    noindex = models.BooleanField(
        default=False,
        help_text="Hide this page from search engines while keeping it accessible.",
    )
    hide_from_internal_search = models.BooleanField(default=False)

    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [FieldPanel("layout_mode")],
            heading="Rendering mode",
            help_text=(
                "Recommended: keep Exact design + editor additions. Switch to "
                "Full visual page builder only when replacing the complete page."
            ),
        ),
        MultiFieldPanel(
            [
                FieldPanel("eyebrow"),
                FieldPanel("introduction"),
                FieldPanel("hero_image"),
                FieldPanel("hero_video_url"),
                FieldPanel("hero_media_position"),
            ],
            heading="Page introduction and builder hero",
            classname="collapsible collapsed",
        ),
        HelpPanel(
            content=(
                "<div class='aastha-editor-guide'>"
                "<p><strong>Adding to the current design:</strong> use "
                "<em>Exact-design additions</em>. Add a section, open its "
                "<em>Placement, spacing and responsive layout</em>, then choose "
                "After hero, article end, page end, or before/after an existing "
                "section anchor.</p>"
                "<p><strong>Replacing the page:</strong> choose Full visual page "
                "builder and edit the complete builder below. Preview before "
                "publishing; revisions allow rollback.</p>"
                "</div>"
            )
        ),
        MultiFieldPanel(
            [FieldPanel("layout_additions")],
            heading="Exact-design additions",
            help_text=(
                "This field is empty on existing pages, so nothing changes "
                "until you add a section. Drag sections to control their order "
                "within the same placement."
            ),
        ),
        MultiFieldPanel(
            [FieldPanel("body")],
            heading="Full page builder",
            help_text=(
                "Used only in Full visual page builder mode, or as a safe "
                "fallback when no exact layout exists."
            ),
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("categories"),
                FieldPanel("show_consultation_sidebar"),
                FieldPanel("show_clinic_choices"),
                FieldPanel("show_medical_disclaimer"),
            ],
            heading="Page relationships and shared sections",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("review_status"),
                FieldPanel("reviewed_by"),
                FieldRowPanel(
                    [
                        FieldPanel("medical_review_date"),
                        FieldPanel("next_review_date"),
                    ]
                ),
            ],
            heading="Medical review",
            classname="collapsible collapsed",
        ),
    ]

    promote_panels = Page.promote_panels + [
        FieldPanel("canonical_url_override"),
        FieldPanel("social_image"),
        FieldPanel("noindex"),
        FieldPanel("hide_from_internal_search"),
    ]

    search_fields = Page.search_fields + [
        index.SearchField("introduction"),
        index.SearchField("layout_additions"),
        index.SearchField("body"),
        index.FilterField("layout_mode"),
        index.FilterField("review_status"),
        index.FilterField("hide_from_internal_search"),
    ]

    class Meta:
        abstract = True

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        context["clinic_locations"] = ClinicLocation.objects.filter(
            is_active=True,
            live=True,
        )
        context["active_doctors"] = Doctor.objects.filter(
            is_active=True,
            live=True,
        )
        return context

    def get_sitemap_urls(self, request=None):
        if self.noindex:
            return []
        return super().get_sitemap_urls(request=request)


class HomePage(BaseFlexiblePage):
    template = "home/home_page.html"
    max_count = 1
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = [
        "home.ContentIndexPage",
        "home.StandardPage",
        "home.DoctorPage",
        "home.ClinicPage",
    ]


class ContentIndexPage(BaseFlexiblePage):
    template = "home/content_index_page.html"
    index_kind = models.CharField(
        max_length=20,
        choices=[
            ("conditions", "Conditions"),
            ("treatments", "Treatments"),
            ("blog", "Blog"),
            ("doctors", "Doctors"),
            ("clinics", "Clinics"),
            ("general", "General"),
        ],
        default="general",
    )
    cards_per_page = models.PositiveSmallIntegerField(default=12)
    listing_order = models.CharField(
        max_length=20,
        choices=[
            ("manual", "Manual drag-and-drop order"),
            ("newest", "Newest first"),
            ("alphabetical", "Alphabetical"),
        ],
        default="manual",
    )

    content_panels = BaseFlexiblePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("index_kind"),
                FieldPanel("cards_per_page"),
                FieldPanel("listing_order"),
            ],
            heading="Directory behaviour",
        )
    ]

    parent_page_types = ["home.HomePage", "home.StandardPage"]
    subpage_types = [
        "home.ConditionPage",
        "home.TreatmentPage",
        "home.BlogPage",
        "home.DoctorPage",
        "home.ClinicPage",
        "home.StandardPage",
    ]

    def get_context(self, request, *args, **kwargs):
        context = super().get_context(request, *args, **kwargs)
        entries = self.get_children().live().public()
        if self.listing_order == "newest":
            entries = entries.order_by("-first_published_at", "title")
        elif self.listing_order == "alphabetical":
            entries = entries.order_by("title")
        else:
            entries = entries.order_by("path")
        context["entries"] = Paginator(
            entries.specific(),
            self.cards_per_page,
        ).get_page(request.GET.get("page"))
        return context


class ConditionPage(BaseFlexiblePage):
    template = "home/flexible_page.html"
    parent_page_types = ["home.ContentIndexPage"]
    subpage_types: list[str] = []


class TreatmentPage(BaseFlexiblePage):
    template = "home/flexible_page.html"
    parent_page_types = ["home.ContentIndexPage"]
    subpage_types: list[str] = []


class StandardPage(BaseFlexiblePage):
    template = "home/flexible_page.html"
    parent_page_types = [
        "home.HomePage",
        "home.ContentIndexPage",
        "home.StandardPage",
    ]
    subpage_types = [
        "home.StandardPage",
        "home.ContentIndexPage",
    ]


class BlogPage(BaseFlexiblePage):
    template = "home/blog_page.html"
    published_date = models.DateField(default=timezone.localdate)
    author = models.ForeignKey(
        Doctor,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="blog_posts",
    )
    reading_time_minutes = models.PositiveSmallIntegerField(default=5)
    featured = models.BooleanField(default=False)

    content_panels = BaseFlexiblePage.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("published_date"),
                FieldPanel("author"),
                FieldPanel("reading_time_minutes"),
                FieldPanel("featured"),
            ],
            heading="Article details",
        )
    ]

    search_fields = BaseFlexiblePage.search_fields + [
        index.FilterField("published_date"),
        index.FilterField("featured"),
    ]

    parent_page_types = ["home.ContentIndexPage"]
    subpage_types: list[str] = []


class DoctorPage(BaseFlexiblePage):
    template = "home/doctor_page.html"
    doctor = models.ForeignKey(
        Doctor,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pages",
    )
    auto_sync_from_record = models.BooleanField(
        default=True,
        help_text=(
            "Keep page title, slug, introduction and hero image synchronised "
            "with the linked Doctor record. Disable before customising those fields."
        ),
    )

    content_panels = BaseFlexiblePage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("doctor"), FieldPanel("auto_sync_from_record")],
            heading="Doctor record connection",
        ),
    ]

    parent_page_types = ["home.HomePage", "home.ContentIndexPage"]
    subpage_types: list[str] = []


class ClinicPage(BaseFlexiblePage):
    template = "home/clinic_page.html"
    clinic = models.ForeignKey(
        ClinicLocation,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="pages",
    )
    auto_sync_from_record = models.BooleanField(
        default=True,
        help_text=(
            "Keep page title, slug, introduction and hero image synchronised "
            "with the linked Clinic record. Disable before customising those fields."
        ),
    )

    content_panels = BaseFlexiblePage.content_panels + [
        MultiFieldPanel(
            [FieldPanel("clinic"), FieldPanel("auto_sync_from_record")],
            heading="Clinic record connection",
        ),
    ]

    parent_page_types = ["home.HomePage", "home.ContentIndexPage"]
    subpage_types: list[str] = []
