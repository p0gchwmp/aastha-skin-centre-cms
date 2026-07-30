# Generated for verified local and professional SEO facts.

import django.db.models.deletion
from django.db import migrations, models

import seo_support.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("home", "0005_exactpagelayout"),
    ]

    operations = [
        migrations.CreateModel(
            name="ClinicSEOProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "latitude",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Verified map latitude, for example 32.726601.",
                        max_digits=9,
                        null=True,
                    ),
                ),
                (
                    "longitude",
                    models.DecimalField(
                        blank=True,
                        decimal_places=6,
                        help_text="Verified map longitude, for example 74.857026.",
                        max_digits=9,
                        null=True,
                    ),
                ),
                (
                    "google_business_url",
                    models.URLField(
                        blank=True,
                        help_text="The verified Google Business Profile or Maps place URL.",
                    ),
                ),
                ("justdial_url", models.URLField(blank=True)),
                ("practo_clinic_url", models.URLField(blank=True)),
                (
                    "service_area",
                    models.CharField(
                        blank=True,
                        help_text=(
                            "Comma-separated real service areas, used only for entity "
                            "context; do not add places the clinic does not genuinely serve."
                        ),
                        max_length=400,
                    ),
                ),
                (
                    "monday_hours",
                    models.CharField(
                        blank=True,
                        max_length=80,
                        validators=[seo_support.models.validate_hours],
                    ),
                ),
                (
                    "tuesday_hours",
                    models.CharField(
                        blank=True,
                        max_length=80,
                        validators=[seo_support.models.validate_hours],
                    ),
                ),
                (
                    "wednesday_hours",
                    models.CharField(
                        blank=True,
                        max_length=80,
                        validators=[seo_support.models.validate_hours],
                    ),
                ),
                (
                    "thursday_hours",
                    models.CharField(
                        blank=True,
                        max_length=80,
                        validators=[seo_support.models.validate_hours],
                    ),
                ),
                (
                    "friday_hours",
                    models.CharField(
                        blank=True,
                        max_length=80,
                        validators=[seo_support.models.validate_hours],
                    ),
                ),
                (
                    "saturday_hours",
                    models.CharField(
                        blank=True,
                        max_length=80,
                        validators=[seo_support.models.validate_hours],
                    ),
                ),
                (
                    "sunday_hours",
                    models.CharField(
                        blank=True,
                        max_length=80,
                        validators=[seo_support.models.validate_hours],
                    ),
                ),
                (
                    "facts_verified_on",
                    models.DateField(
                        blank=True,
                        help_text=(
                            "Date these branch facts were last checked against clinic records."
                        ),
                        null=True,
                    ),
                ),
                (
                    "clinic",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="seo_profile",
                        to="home.cliniclocation",
                    ),
                ),
            ],
            options={
                "verbose_name": "Clinic local SEO profile",
                "verbose_name_plural": "Clinic local SEO profiles",
                "ordering": ["clinic__sort_order", "clinic__name"],
            },
        ),
        migrations.CreateModel(
            name="DoctorSEOProfile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("practo_url", models.URLField(blank=True)),
                ("google_scholar_url", models.URLField(blank=True)),
                ("orcid_url", models.URLField(blank=True)),
                ("linkedin_url", models.URLField(blank=True)),
                ("facts_verified_on", models.DateField(blank=True, null=True)),
                (
                    "doctor",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="seo_profile",
                        to="home.doctor",
                    ),
                ),
            ],
            options={
                "verbose_name": "Doctor SEO profile",
                "verbose_name_plural": "Doctor SEO profiles",
                "ordering": ["doctor__sort_order", "doctor__name"],
            },
        ),
    ]
