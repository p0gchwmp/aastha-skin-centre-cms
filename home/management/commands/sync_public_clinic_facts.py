from django.core.management.base import BaseCommand

from home.models import ClinicLocation


# Update only exact, known legacy values. This intentionally does not overwrite
# values that an editor has changed in Wagtail.
LEGACY_HOUR_REPLACEMENTS = {
    "karan-nagar": {
        "reception_hours": {
            "Mon–Sat 10:00 AM–8:00 PM · Sun 10:00 AM–3:00 PM": "Daily 10:00 AM–8:00 PM",
        },
        "doctor_hours": {
            "Mon–Sat 11:00 AM–4:00 PM · Sun 11:00 AM–3:00 PM": "Daily 11:00 AM–3:00 PM",
        },
        "procedure_hours": {
            "Mon–Sat 11:00 AM–8:00 PM · Sun 11:00 AM–3:00 PM": "Mon–Sat 11:00 AM–8:00 PM",
        },
    },
    "paloura": {
        "reception_hours": {
            "Mon–Sat 10:00 AM–8:00 PM · Sun 10:00 AM–2:00 PM": "Daily 10:00 AM–8:00 PM",
        },
        "doctor_hours": {
            "Mon–Sat 6:00 PM–8:00 PM · Sun 10:30 AM–12:00 PM": "Daily 6:00 PM–8:00 PM",
        },
        "procedure_hours": {
            "Mon–Sat 10:00 AM–8:00 PM · Sun 10:30 AM–12:00 PM": "Mon–Sat 10:00 AM–8:00 PM",
        },
    },
}


class Command(BaseCommand):
    help = (
        "Replace only known stale public clinic-hour values while preserving "
        "any values that editors have changed."
    )

    def handle(self, *args, **options):
        updated = 0

        for slug, fields in LEGACY_HOUR_REPLACEMENTS.items():
            for field_name, replacements in fields.items():
                for old_value, new_value in replacements.items():
                    count = ClinicLocation.objects.filter(
                        slug=slug,
                        **{field_name: old_value},
                    ).update(**{field_name: new_value})
                    if count:
                        updated += count
                        self.stdout.write(
                            f"Updated {slug}.{field_name}: {old_value!r} -> {new_value!r}"
                        )

        if updated:
            self.stdout.write(
                self.style.SUCCESS(f"Updated {updated} known stale clinic-hour value(s).")
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(
                    "No known stale clinic-hour values found; editor-managed values were left unchanged."
                )
            )
