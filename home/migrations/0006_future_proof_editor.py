# Generated manually for the future-proof Wagtail editor architecture.

import home.blocks
import wagtail.fields
from django.db import migrations, models


PAGE_MODELS = (
    "homepage",
    "contentindexpage",
    "conditionpage",
    "treatmentpage",
    "standardpage",
    "blogpage",
    "doctorpage",
    "clinicpage",
)


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0005_exactpagelayout"),
    ]

    operations = [
        migrations.AddField(
            model_name="doctor",
            name="create_public_page",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "When this published record has no linked Doctor page, "
                    "create one automatically as a draft."
                ),
            ),
        ),
        migrations.AddField(
            model_name="doctor",
            name="publish_public_page_automatically",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Publish the generated Doctor page immediately. Leave "
                    "disabled to review and publish the page manually."
                ),
            ),
        ),
        migrations.AddField(
            model_name="cliniclocation",
            name="create_public_page",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "When this published record has no linked Clinic page, "
                    "create one automatically as a draft."
                ),
            ),
        ),
        migrations.AddField(
            model_name="cliniclocation",
            name="publish_public_page_automatically",
            field=models.BooleanField(
                default=False,
                help_text=(
                    "Publish the generated Clinic page immediately. Leave "
                    "disabled to review and publish the page manually."
                ),
            ),
        ),
        *[
            migrations.AddField(
                model_name=model_name,
                name="layout_mode",
                field=models.CharField(
                    choices=[
                        (
                            "hybrid",
                            "Exact design + editor additions (recommended)",
                        ),
                        ("builder", "Full visual page builder"),
                        (
                            "exact",
                            "Exact design only — hide editor additions",
                        ),
                    ],
                    default="hybrid",
                    help_text=(
                        "Hybrid keeps the verified design and inserts sections "
                        "from the Exact-design additions field. Builder replaces "
                        "the exact design with the Full page builder."
                    ),
                    max_length=20,
                ),
            )
            for model_name in PAGE_MODELS
        ],
        *[
            migrations.AddField(
                model_name=model_name,
                name="layout_additions",
                field=wagtail.fields.StreamField(
                    home.blocks.PageAdditionStreamBlock(),
                    blank=True,
                    help_text=(
                        "Sections added here appear inside the current exact "
                        "design. Each section has its own Placement, spacing "
                        "and responsive layout."
                    ),
                    use_json_field=True,
                ),
            )
            for model_name in PAGE_MODELS
        ],
        *[
            migrations.AlterField(
                model_name=model_name,
                name="body",
                field=wagtail.fields.StreamField(
                    home.blocks.PageBodyStreamBlock(),
                    blank=True,
                    help_text=(
                        "Complete replacement layout used when Rendering mode "
                        "is Full visual page builder."
                    ),
                    use_json_field=True,
                ),
            )
            for model_name in PAGE_MODELS
        ],
        migrations.AlterField(
            model_name="reusablesection",
            name="body",
            field=wagtail.fields.StreamField(
                home.blocks.PageBodyStreamBlock(),
                blank=True,
                use_json_field=True,
            ),
        ),
    ]
