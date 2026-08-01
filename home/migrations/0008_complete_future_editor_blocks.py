# Generated manually for the completed future-proof editor block library.

import home.blocks
import wagtail.fields
from django.db import migrations


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
        ("home", "0007_profile_page_auto_sync_flags"),
    ]

    operations = [
        *[
            migrations.AlterField(
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
