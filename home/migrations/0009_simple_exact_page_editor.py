# Generated manually for the simple exact-page content editor.

import django.db.models.deletion
import home.exact_editor
import wagtail.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0008_complete_future_editor_blocks"),
        ("wagtailimages", "0026_delete_uploadedimage"),
    ]

    operations = [
        migrations.AddField(
            model_name="exactpagelayout",
            name="editable_text",
            field=wagtail.fields.StreamField(
                home.exact_editor.ExactTextStreamBlock(),
                blank=True,
                help_text="Visible text in page order. Open only the item to change.",
                use_json_field=True,
            ),
        ),
        migrations.AddField(
            model_name="exactpagelayout",
            name="editable_images",
            field=wagtail.fields.StreamField(
                home.exact_editor.ExactImageStreamBlock(),
                blank=True,
                help_text="Existing page images in page order.",
                use_json_field=True,
            ),
        ),
        migrations.AddField(
            model_name="exactpagelayout",
            name="editable_links",
            field=wagtail.fields.StreamField(
                home.exact_editor.ExactLinkStreamBlock(),
                blank=True,
                help_text="Existing buttons and links in page order.",
                use_json_field=True,
            ),
        ),
        migrations.AddField(
            model_name="homepage",
            name="doctor_section_image",
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    "Replaces the doctor illustration in the Meet your dermatologist "
                    "section on the homepage."
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="+",
                to="wagtailimages.image",
            ),
        ),
    ]
