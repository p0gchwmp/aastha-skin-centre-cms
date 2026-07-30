"""Structured local-search facts kept separate from public page copy."""

from __future__ import annotations

import re

from django.core.exceptions import ValidationError
from django.db import models
from wagtail.admin.panels import FieldPanel, FieldRowPanel, MultiFieldPanel
from wagtail.snippets.models import register_snippet


TIME_24H = r"(?:[01]\d|2[0-3]):[0-5]\d"
TIME_INTERVAL = rf"{TIME_24H}-{TIME_24H}"
HOURS_PATTERN = re.compile(
    rf"^(?:closed|{TIME_INTERVAL}(?:,{TIME_INTERVAL})*)$",
    re.IGNORECASE,
)
DAY_FIELDS = (
    ("monday_hours", "Monday"),
    ("tuesday_hours", "Tuesday"),
    ("wednesday_hours", "Wednesday"),
    ("thursday_hours", "Thursday"),
    ("friday_hours", "Friday"),
    ("saturday_hours", "Saturday"),
    ("sunday_hours", "Sunday"),
)


def validate_hours(value: str) -> None:
    value = (value or "").strip()
    if value and not HOURS_PATTERN.fullmatch(value):
        raise ValidationError(
            "Use 24-hour ranges such as 10:00-20:00, split hours such as "
            "10:00-13:00,17:00-20:00, or 'closed'."
        )


@register_snippet
class ClinicSEOProfile(models.Model):
    """Verified local-search data for one physical clinic branch."""

    clinic = models.OneToOneField(
        "home.ClinicLocation",
        on_delete=models.CASCADE,
        related_name="seo_profile",
    )
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Verified map latitude, for example 32.726601.",
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        help_text="Verified map longitude, for example 74.857026.",
    )
    google_business_url = models.URLField(
        blank=True,
        help_text="The verified Google Business Profile or Maps place URL.",
    )
    justdial_url = models.URLField(blank=True)
    practo_clinic_url = models.URLField(blank=True)
    service_area = models.CharField(
        max_length=400,
        blank=True,
        help_text=(
            "Comma-separated real service areas, used only for entity context; "
            "do not add places the clinic does not genuinely serve."
        ),
    )
    monday_hours = models.CharField(
        max_length=80, blank=True, validators=[validate_hours]
    )
    tuesday_hours = models.CharField(
        max_length=80, blank=True, validators=[validate_hours]
    )
    wednesday_hours = models.CharField(
        max_length=80, blank=True, validators=[validate_hours]
    )
    thursday_hours = models.CharField(
        max_length=80, blank=True, validators=[validate_hours]
    )
    friday_hours = models.CharField(
        max_length=80, blank=True, validators=[validate_hours]
    )
    saturday_hours = models.CharField(
        max_length=80, blank=True, validators=[validate_hours]
    )
    sunday_hours = models.CharField(
        max_length=80, blank=True, validators=[validate_hours]
    )
    facts_verified_on = models.DateField(
        null=True,
        blank=True,
        help_text="Date these branch facts were last checked against clinic records.",
    )

    panels = [
        FieldPanel("clinic"),
        MultiFieldPanel(
            [
                FieldRowPanel([FieldPanel("latitude"), FieldPanel("longitude")]),
                FieldPanel("google_business_url"),
                FieldPanel("justdial_url"),
                FieldPanel("practo_clinic_url"),
                FieldPanel("service_area"),
            ],
            heading="Local identity and profiles",
        ),
        MultiFieldPanel(
            [FieldPanel(field_name) for field_name, _ in DAY_FIELDS],
            heading="Public opening hours",
            help_text=(
                "Use 24-hour ranges such as 10:00-20:00. For split hours use "
                "10:00-13:00,17:00-20:00. Leave blank when not verified."
            ),
        ),
        FieldPanel("facts_verified_on"),
    ]

    class Meta:
        ordering = ["clinic__sort_order", "clinic__name"]
        verbose_name = "Clinic local SEO profile"
        verbose_name_plural = "Clinic local SEO profiles"

    def clean(self):
        super().clean()
        if (self.latitude is None) != (self.longitude is None):
            raise ValidationError(
                "Latitude and longitude must either both be filled or both be blank."
            )
        if self.latitude is not None and not -90 <= self.latitude <= 90:
            raise ValidationError({"latitude": "Latitude must be between -90 and 90."})
        if self.longitude is not None and not -180 <= self.longitude <= 180:
            raise ValidationError(
                {"longitude": "Longitude must be between -180 and 180."}
            )

    @property
    def same_as_urls(self) -> list[str]:
        return [
            value
            for value in (
                self.google_business_url,
                self.justdial_url,
                self.practo_clinic_url,
            )
            if value
        ]

    @property
    def service_areas(self) -> list[str]:
        return [item.strip() for item in self.service_area.split(",") if item.strip()]

    def opening_hours_specifications(self) -> list[dict[str, object]]:
        output: list[dict[str, object]] = []
        for field_name, day_name in DAY_FIELDS:
            value = (getattr(self, field_name) or "").strip().lower()
            if not value or value == "closed":
                continue
            for interval in value.split(","):
                opens, closes = interval.split("-", 1)
                output.append(
                    {
                        "@type": "OpeningHoursSpecification",
                        "dayOfWeek": f"https://schema.org/{day_name}",
                        "opens": opens,
                        "closes": closes,
                    }
                )
        return output

    def __str__(self):
        return f"Local SEO — {self.clinic}"


@register_snippet
class DoctorSEOProfile(models.Model):
    """Verified third-party professional identities for a doctor."""

    doctor = models.OneToOneField(
        "home.Doctor",
        on_delete=models.CASCADE,
        related_name="seo_profile",
    )
    practo_url = models.URLField(blank=True)
    google_scholar_url = models.URLField(blank=True)
    orcid_url = models.URLField(blank=True)
    linkedin_url = models.URLField(blank=True)
    facts_verified_on = models.DateField(null=True, blank=True)

    panels = [
        FieldPanel("doctor"),
        MultiFieldPanel(
            [
                FieldPanel("practo_url"),
                FieldPanel("google_scholar_url"),
                FieldPanel("orcid_url"),
                FieldPanel("linkedin_url"),
            ],
            heading="Verified professional profiles",
        ),
        FieldPanel("facts_verified_on"),
    ]

    class Meta:
        ordering = ["doctor__sort_order", "doctor__name"]
        verbose_name = "Doctor SEO profile"
        verbose_name_plural = "Doctor SEO profiles"

    @property
    def same_as_urls(self) -> list[str]:
        return [
            value
            for value in (
                self.practo_url,
                self.google_scholar_url,
                self.orcid_url,
                self.linkedin_url,
            )
            if value
        ]

    def __str__(self):
        return f"SEO — {self.doctor}"
