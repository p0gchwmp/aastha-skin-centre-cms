# Generated manually to capture the profile-page synchronisation controls.

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("home", "0006_future_proof_editor"),
    ]

    operations = [
        migrations.AddField(
            model_name="doctorpage",
            name="auto_sync_from_record",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Keep page title, slug, introduction and hero image "
                    "synchronised with the linked Doctor record. Disable before "
                    "customising those fields."
                ),
            ),
        ),
        migrations.AddField(
            model_name="clinicpage",
            name="auto_sync_from_record",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Keep page title, slug, introduction and hero image "
                    "synchronised with the linked Clinic record. Disable before "
                    "customising those fields."
                ),
            ),
        ),
    ]
