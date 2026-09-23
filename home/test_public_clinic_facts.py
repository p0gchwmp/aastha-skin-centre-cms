from django.core.management import call_command
from django.test import TestCase

from home.models import ClinicLocation


class PublicClinicFactsSyncTests(TestCase):
    def test_known_legacy_hours_are_reconciled(self):
        karan = ClinicLocation.objects.create(
            name="Karan Nagar",
            slug="karan-nagar",
            address="Test address",
            reception_hours="Mon–Sat 10:00 AM–8:00 PM\nSun 10:00 AM–3:00 PM",
            doctor_hours="Mon–Sat 11:00 AM–4:00 PM\nSun 11:00 AM–3:00 PM",
            procedure_hours="Mon–Sat 11:00 AM–8:00 PM\nSun 11:00 AM–3:00 PM",
        )
        paloura = ClinicLocation.objects.create(
            name="Paloura Chowk",
            slug="paloura",
            address="Test address",
            reception_hours="Mon–Sat 10:00 AM–8:00 PM\nSun 10:00 AM–2:00 PM",
            doctor_hours="Mon–Sat 6:00 PM–8:00 PM\nSun 10:30 AM–12:00 PM",
            procedure_hours="Mon–Sat 10:00 AM–8:00 PM\nSun 10:30 AM–12:00 PM",
        )

        call_command("sync_public_clinic_facts")
        karan.refresh_from_db()
        paloura.refresh_from_db()

        self.assertEqual(karan.reception_hours, "10:00 AM–8:00 PM")
        self.assertEqual(karan.doctor_hours, "11:00 AM–3:00 PM")
        self.assertEqual(karan.procedure_hours, "Mon–Sat 11:00 AM–8:00 PM")
        self.assertEqual(paloura.reception_hours, "10:00 AM–8:00 PM")
        self.assertEqual(paloura.doctor_hours, "6:00 PM–8:00 PM")
        self.assertEqual(paloura.procedure_hours, "Mon–Sat 10:00 AM–8:00 PM")

    def test_editor_managed_hours_are_preserved(self):
        clinic = ClinicLocation.objects.create(
            name="Karan Nagar",
            slug="karan-nagar",
            address="Test address",
            reception_hours="Custom reception hours",
            doctor_hours="Custom doctor hours",
            procedure_hours="Custom procedure hours",
        )

        call_command("sync_public_clinic_facts")
        clinic.refresh_from_db()

        self.assertEqual(clinic.reception_hours, "Custom reception hours")
        self.assertEqual(clinic.doctor_hours, "Custom doctor hours")
        self.assertEqual(clinic.procedure_hours, "Custom procedure hours")
