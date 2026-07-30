from decimal import Decimal

from django.core.exceptions import ValidationError
from django.test import RequestFactory, TestCase

from home.models import ClinicLocation, Doctor
from home.seo import _clinic_id, _doctor_id
from seo_support.models import ClinicSEOProfile, DoctorSEOProfile, validate_hours
from seo_support.schema import enrich_structured_data


class SEOProfileValidationTests(TestCase):
    def setUp(self):
        self.clinic = ClinicLocation.objects.create(
            name="SEO Test Clinic",
            slug="seo-test-clinic-profile",
            address="Jammu",
        )

    def test_hours_accept_single_split_and_closed_values(self):
        for value in (
            "10:00-20:00",
            "10:00-13:00,17:00-20:00",
            "closed",
            "",
        ):
            validate_hours(value)

    def test_hours_reject_ambiguous_text(self):
        with self.assertRaises(ValidationError):
            validate_hours("10 AM to 8 PM")

    def test_coordinates_must_be_complete_and_in_range(self):
        profile = ClinicSEOProfile(
            clinic=self.clinic,
            latitude=Decimal("32.726601"),
        )
        with self.assertRaises(ValidationError):
            profile.full_clean()

        profile.longitude = Decimal("181.000000")
        with self.assertRaises(ValidationError):
            profile.full_clean()

    def test_opening_hours_convert_to_schema_specifications(self):
        profile = ClinicSEOProfile(
            clinic=self.clinic,
            monday_hours="10:00-13:00,17:00-20:00",
            sunday_hours="closed",
        )
        specifications = profile.opening_hours_specifications()
        self.assertEqual(len(specifications), 2)
        self.assertTrue(
            all(item["dayOfWeek"].endswith("/Monday") for item in specifications)
        )


class SchemaEnrichmentTests(TestCase):
    def setUp(self):
        self.request = RequestFactory().get("/conditions/acne/")
        self.origin = "https://www.aasthaskincentre.in"
        self.clinic = ClinicLocation.objects.create(
            name="Karan Nagar SEO Test",
            slug="karan-nagar-seo-enrichment",
            address="Amphalla Chowk, Jammu",
        )
        self.doctor = Doctor.objects.create(
            name="Dr. SEO Test",
            slug="doctor-seo-enrichment",
        )
        ClinicSEOProfile.objects.create(
            clinic=self.clinic,
            latitude=Decimal("32.726601"),
            longitude=Decimal("74.857026"),
            google_business_url="https://maps.google.com/example",
            justdial_url="https://www.justdial.com/example",
            monday_hours="10:00-20:00",
            service_area="Jammu, Udhampur",
        )
        DoctorSEOProfile.objects.create(
            doctor=self.doctor,
            practo_url="https://www.practo.com/jammu/doctor/example",
        )

    def test_verified_profiles_enrich_existing_entities(self):
        clinic_id = _clinic_id(self.clinic, self.request, self.origin)
        doctor_id = _doctor_id(self.doctor, self.request, self.origin)
        payload = {
            "@context": "https://schema.org",
            "@graph": [
                {"@type": "MedicalClinic", "@id": clinic_id},
                {"@type": "Physician", "@id": doctor_id},
            ],
        }

        enriched = enrich_structured_data(
            payload,
            clinics=[self.clinic],
            doctors=[self.doctor],
            request=self.request,
            origin=self.origin,
        )
        clinic_entity, doctor_entity = enriched["@graph"]
        self.assertEqual(
            clinic_entity["geo"],
            {
                "@type": "GeoCoordinates",
                "latitude": 32.726601,
                "longitude": 74.857026,
            },
        )
        self.assertEqual(clinic_entity["hasMap"], "https://maps.google.com/example")
        self.assertEqual(len(clinic_entity["openingHoursSpecification"]), 1)
        self.assertEqual(
            [area["name"] for area in clinic_entity["areaServed"]],
            ["Jammu", "Udhampur"],
        )
        self.assertEqual(
            doctor_entity["sameAs"],
            ["https://www.practo.com/jammu/doctor/example"],
        )
