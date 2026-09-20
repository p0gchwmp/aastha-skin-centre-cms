from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("seo_support", "0002_seed_verified_profiles"),
    ]

    operations = [
        migrations.AddField(
            model_name="clinicseoprofile",
            name="verification_notes",
            field=models.TextField(
                blank=True,
                help_text="Record what was checked and against which clinic/source record.",
            ),
        ),
        migrations.AddField(
            model_name="clinicseoprofile",
            name="verification_reviewer",
            field=models.CharField(
                blank=True,
                help_text="Name or role of the person who checked these branch facts.",
                max_length=160,
            ),
        ),
        migrations.AddField(
            model_name="clinicseoprofile",
            name="verification_source_url",
            field=models.URLField(
                blank=True,
                help_text="Optional proof or source URL used during verification.",
            ),
        ),
        migrations.AddField(
            model_name="doctorseoprofile",
            name="verification_notes",
            field=models.TextField(
                blank=True,
                help_text="Record what was checked and against which professional/source record.",
            ),
        ),
        migrations.AddField(
            model_name="doctorseoprofile",
            name="verification_reviewer",
            field=models.CharField(
                blank=True,
                help_text="Name or role of the person who checked these professional facts.",
                max_length=160,
            ),
        ),
        migrations.AddField(
            model_name="doctorseoprofile",
            name="verification_source_url",
            field=models.URLField(
                blank=True,
                help_text="Optional proof or source URL used during verification.",
            ),
        ),
    ]
