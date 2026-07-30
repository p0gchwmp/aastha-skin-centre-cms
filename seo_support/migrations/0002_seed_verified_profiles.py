from datetime import date

from django.db import migrations


VERIFIED_ON = date(2026, 7, 31)


def seed_verified_profiles(apps, schema_editor):
    ClinicLocation = apps.get_model("home", "ClinicLocation")
    Doctor = apps.get_model("home", "Doctor")
    ClinicSEOProfile = apps.get_model("seo_support", "ClinicSEOProfile")
    DoctorSEOProfile = apps.get_model("seo_support", "DoctorSEOProfile")

    clinic_data = {
        "karan-nagar": {
            "google_business_url": "https://maps.app.goo.gl/pHCQ1r4crKuZBSi98",
            "justdial_url": (
                "https://www.justdial.com/Jammu/"
                "Aastha-Skin-Dermato-Cosmetic-Centre-Near-Amphalla-Chowk-"
                "Karan-Nagar/9999PX191-X191-110209095958-N1H9_BZDET"
            ),
            "service_area": "Jammu",
            "monday_hours": "10:00-20:00",
            "tuesday_hours": "10:00-20:00",
            "wednesday_hours": "10:00-20:00",
            "thursday_hours": "10:00-20:00",
            "friday_hours": "10:00-20:00",
            "saturday_hours": "10:00-20:00",
            "sunday_hours": "10:00-15:00",
            "facts_verified_on": VERIFIED_ON,
        },
        "paloura": {
            "google_business_url": "https://maps.app.goo.gl/kh4AqZoUkscpEgWc8",
            "justdial_url": (
                "https://www.justdial.com/Jammu/"
                "AASTHA-SKIN-AND-DERMATO-COSMETIC-CENTRE-Near-Govt-Higher-"
                "Secondary-School-Paloura/9999PX191-X191-250621103839-Q8M5_BZDET"
            ),
            "service_area": "Jammu",
            "monday_hours": "10:00-20:00",
            "tuesday_hours": "10:00-20:00",
            "wednesday_hours": "10:00-20:00",
            "thursday_hours": "10:00-20:00",
            "friday_hours": "10:00-20:00",
            "saturday_hours": "10:00-20:00",
            "sunday_hours": "10:00-14:00",
            "facts_verified_on": VERIFIED_ON,
        },
    }
    for slug, defaults in clinic_data.items():
        clinic = ClinicLocation.objects.filter(slug=slug).first()
        if clinic:
            ClinicSEOProfile.objects.get_or_create(
                clinic=clinic,
                defaults=defaults,
            )

    doctor = Doctor.objects.filter(slug="dr-cheena-langer").first()
    if doctor:
        DoctorSEOProfile.objects.get_or_create(
            doctor=doctor,
            defaults={
                "practo_url": (
                    "https://www.practo.com/jammu/doctor/"
                    "cheena-langer-dermatologist-1"
                ),
                "facts_verified_on": VERIFIED_ON,
            },
        )


def remove_seeded_profiles(apps, schema_editor):
    ClinicSEOProfile = apps.get_model("seo_support", "ClinicSEOProfile")
    DoctorSEOProfile = apps.get_model("seo_support", "DoctorSEOProfile")
    ClinicSEOProfile.objects.filter(
        facts_verified_on=VERIFIED_ON,
        clinic__slug__in=["karan-nagar", "paloura"],
    ).delete()
    DoctorSEOProfile.objects.filter(
        facts_verified_on=VERIFIED_ON,
        doctor__slug="dr-cheena-langer",
    ).delete()


class Migration(migrations.Migration):
    dependencies = [
        ("seo_support", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_verified_profiles, remove_seeded_profiles),
    ]
