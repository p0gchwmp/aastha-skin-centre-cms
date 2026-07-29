from __future__ import annotations

import json
import os
import re
from copy import deepcopy
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from wagtail.models import Page, Site

from home.models import (
    BlogPage,
    ClinicLocation,
    ClinicPage,
    ConditionPage,
    ContentCategory,
    ContentIndexPage,
    Doctor,
    DoctorPage,
    HomePage,
    SiteSettings,
    StandardPage,
    TreatmentPage,
)


PAGE_MODELS = {
    "index": ContentIndexPage,
    "condition": ConditionPage,
    "treatment": TreatmentPage,
    "blog": BlogPage,
    "doctor": DoctorPage,
    "clinic": ClinicPage,
    "standard": StandardPage,
}

INDEX_KIND = {
    "/conditions/": "conditions",
    "/treatments/": "treatments",
    "/blog/": "blog",
    "/locations/": "clinics",
}

GLOBAL_TEXT_REPLACEMENTS = [
    ("https://wa.me/917006613362", "{{ whatsapp_url }}"),
    ("tel:+917006613362", "tel:{{ primary_phone_digits }}"),
    ("tel:7006613362", "tel:{{ primary_phone_digits }}"),
    ("tel:+919796676541", "tel:{{ secondary_phone_digits }}"),
    ("tel:9796676541", "tel:{{ secondary_phone_digits }}"),
    ("mailto:aasthaskinsurgs@gmail.com", "mailto:{{ email }}"),
    ("aasthaskinsurgs@gmail.com", "{{ email }}"),
    ("7006613362", "{{ primary_phone }}"),
    ("9796676541", "{{ secondary_phone }}"),
    ("₹500", "{{ consultation_fee }}"),
    ("within 10 days", "within {{ follow_up_days }} days"),
]

GLOBAL_LINK_ACTIONS = {
    "https://wa.me/917006613362": "whatsapp",
    "tel:+917006613362": "primary_phone",
    "tel:7006613362": "primary_phone",
    "tel:+919796676541": "secondary_phone",
    "tel:9796676541": "secondary_phone",
    "mailto:aasthaskinsurgs@gmail.com": "email",
}


def normalise_path(path: str) -> str:
    if not path.startswith("/"):
        path = "/" + path
    if path != "/" and not path.endswith("/"):
        path += "/"
    return path


class Command(BaseCommand):
    help = (
        "Import the verified static v28 website into structured, editable "
        "Wagtail pages."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            "--data",
            type=Path,
            default=Path("seed_data/v28-content.json"),
        )
        parser.add_argument(
            "--reset",
            action="store_true",
            help="Delete existing descendants of the home page before importing.",
        )

    @transaction.atomic
    def handle(self, *args, **options):
        data_path = options["data"].resolve()
        if not data_path.exists():
            raise CommandError(f"Seed data not found: {data_path}")
        records = json.loads(data_path.read_text(encoding="utf-8"))
        records_by_path = {
            normalise_path(record["path"]): record for record in records
        }

        root = Page.get_first_root_node()
        home = HomePage.objects.first()
        if home is None:
            home = HomePage(title="Home", slug="home")
            root.add_child(instance=home)

        if options["reset"]:
            # Delete top-level children through Wagtail so Treebeard updates
            # the parent counters correctly. A bulk queryset delete can leave
            # the page tree inconsistent.
            for child in list(home.get_children()):
                child.delete()
            home.refresh_from_db()
        elif home.get_children().exists():
            raise CommandError(
                "The site already has pages. Re-run with --reset only if you "
                "intend to replace the existing page tree."
            )

        site, _ = Site.objects.update_or_create(
            is_default_site=True,
            defaults={
                "hostname": (
                    os.environ.get("SITE_HOSTNAME")
                    or os.environ.get("RENDER_EXTERNAL_HOSTNAME")
                    or "localhost"
                ),
                "port": (
                    443
                    if (
                        os.environ.get("SITE_HOSTNAME")
                        or os.environ.get("RENDER_EXTERNAL_HOSTNAME")
                    )
                    else 8000
                ),
                "site_name": "Aastha Skin Centre",
                "root_page": home,
            },
        )

        doctor = self.create_doctor()
        clinics = self.create_clinics()
        self.create_categories()
        self.create_settings(site)

        path_map: dict[str, Page] = {"/": home}
        page_record_map: dict[int, dict] = {}

        home_record = records_by_path.get("/")
        if home_record:
            self.apply_common_fields(home, home_record)
            home.body = []
            home.save()

        # The static source has clinic detail pages but no /locations/ index.
        if "/locations/" not in records_by_path:
            records.append(
                {
                    "path": "/locations/",
                    "parent_path": "/",
                    "page_type": "index",
                    "title": "Clinic Locations in Jammu",
                    "slug": "locations",
                    "seo_title": "Aastha Skin Centre Locations in Jammu",
                    "search_description": (
                        "Find Aastha Skin Centre at Karan Nagar and Paloura "
                        "Chowk in Jammu."
                    ),
                    "eyebrow": "Two Jammu clinics",
                    "introduction": (
                        "Choose the clinic that is most convenient for you."
                    ),
                    "body": [],
                    "show_consultation_sidebar": False,
                    "show_clinic_choices": False,
                    "show_medical_disclaimer": False,
                }
            )

        pending = [
            record
            for record in records
            if normalise_path(record["path"]) != "/"
        ]
        created = 0
        while pending:
            progress = False
            for record in pending[:]:
                path = normalise_path(record["path"])
                parent_path = normalise_path(record.get("parent_path") or "/")
                parent = path_map.get(parent_path)
                if parent is None:
                    continue
                page = self.create_page(record, parent, doctor, clinics)
                path_map[path] = page
                page_record_map[page.pk] = record
                pending.remove(record)
                created += 1
                progress = True
            if not progress:
                unresolved = ", ".join(
                    f"{record['path']} -> {record.get('parent_path')}"
                    for record in pending
                )
                raise CommandError(f"Could not resolve page parents: {unresolved}")

        self.configure_navigation(site, path_map)

        # Resolve every page chooser and rich-text internal link after the full
        # tree exists. This keeps links valid if an editor later moves a page.
        if home_record:
            home.body = self.resolve_blocks(
                home_record["body"],
                path_map,
                prepend_home_hero=home_record,
            )
            home.save_revision().publish()

        for page_id, record in page_record_map.items():
            page = Page.objects.get(pk=page_id).specific
            page.body = self.resolve_blocks(
                self.blocks_without_legacy_listing(record),
                path_map,
            )
            page.save_revision().publish()

        self.stdout.write(
            self.style.SUCCESS(
                f"Imported {created + 1} editable pages, "
                f"{len(clinics)} clinics and one doctor profile."
            )
        )
        self.stdout.write(
            "Open /admin/ and use Settings for global fees/contact details, "
            "Snippets for reusable doctors/clinics/sections, and Pages for "
            "drag-and-drop content."
        )

    def blocks_without_legacy_listing(self, record):
        """Use CMS child pages as the blog/treatment directory source."""
        path = normalise_path(record["path"])
        if path not in {"/blog/", "/treatments/"}:
            return record["body"]
        filtered = []
        for block in record["body"]:
            value = block.get("value")
            if not isinstance(value, str):
                filtered.append(block)
                continue
            if path == "/blog/" and 'class="journal-section"' in value:
                continue
            if path == "/treatments/" and 'class="hub-section' in value:
                continue
            filtered.append(block)
        return filtered

    def configure_navigation(self, site, path_map):
        settings = SiteSettings.for_site(site)

        def navigation_item(label, path):
            return (
                "link",
                {
                    "label": label,
                    "global_action": "",
                    "page": path_map[normalise_path(path)],
                    "external_url": "",
                    "new_tab": False,
                },
            )

        settings.header_navigation = [
            navigation_item("Conditions", "/conditions/"),
            navigation_item("Treatments", "/treatments/"),
            navigation_item("Blog", "/blog/"),
            navigation_item("Doctor", "/dr-cheena-langer/"),
            navigation_item("Locations", "/locations/"),
            navigation_item("Contact", "/contact/"),
        ]
        settings.footer_navigation = [
            navigation_item("Book an appointment", "/book-appointment/"),
            navigation_item("Privacy policy", "/privacy-policy/"),
            navigation_item("Terms and conditions", "/terms-and-conditions/"),
            navigation_item("Medical disclaimer", "/medical-disclaimer/"),
        ]
        settings.save()

    def create_doctor(self):
        doctor, _ = Doctor.objects.update_or_create(
            slug="dr-cheena-langer",
            defaults={
                "name": "Dr. Cheena Langer",
                "qualifications": "MBBS, MD Dermatology",
                "role": "Consultant Dermatologist",
                "short_bio": (
                    "Dermatologist providing diagnosis-led medical, laser, "
                    "hair and dermato-cosmetic care in Jammu."
                ),
                "is_active": True,
            },
        )
        doctor.save_revision().publish()
        return doctor

    def create_clinics(self):
        data = [
            {
                "slug": "karan-nagar",
                "name": "Karan Nagar",
                "address": (
                    "Lane 2, Karan Nagar, near Amphalla Chowk, Jammu, "
                    "Jammu & Kashmir – 180005"
                ),
                "locality": "Karan Nagar",
                "postal_code": "180005",
                "landline": "0191-3509230",
                "mobile": "7006613362",
                "email": "aasthaskinsurgs@gmail.com",
                "google_maps_url": "https://maps.app.goo.gl/pHCQ1r4crKuZBSi98",
                "reception_hours": (
                    "Mon–Sat 10:00 AM–8:00 PM\nSun 10:00 AM–3:00 PM"
                ),
                "doctor_hours": (
                    "Mon–Sat 11:00 AM–4:00 PM\nSun 11:00 AM–3:00 PM"
                ),
                "procedure_hours": (
                    "Mon–Sat 11:00 AM–8:00 PM\nSun 11:00 AM–3:00 PM"
                ),
                "sort_order": 1,
            },
            {
                "slug": "paloura",
                "name": "Paloura Chowk",
                "address": (
                    "Paloura Chowk, Top Paloura, opposite Government Senior "
                    "Secondary School, Jammu, Jammu & Kashmir – 181121"
                ),
                "locality": "Top Paloura",
                "postal_code": "181121",
                "landline": "0191-3135864",
                "mobile": "9796676541",
                "email": "aasthaskinsurgs@gmail.com",
                "google_maps_url": "https://maps.app.goo.gl/kh4AqZoUkscpEgWc8",
                "reception_hours": (
                    "Mon–Sat 10:00 AM–8:00 PM\nSun 10:00 AM–2:00 PM"
                ),
                "doctor_hours": (
                    "Mon–Sat 6:00 PM–8:00 PM\nSun 10:30 AM–12:00 PM"
                ),
                "procedure_hours": (
                    "Mon–Sat 10:00 AM–8:00 PM\nSun 10:30 AM–12:00 PM"
                ),
                "sort_order": 2,
            },
        ]
        clinics = {}
        for item in data:
            clinic, _ = ClinicLocation.objects.update_or_create(
                slug=item["slug"],
                defaults=item,
            )
            clinic.save_revision().publish()
            clinics[item["slug"]] = clinic
        return clinics

    def create_categories(self):
        categories = [
            ("Acne and scars", "acne-and-scars"),
            ("Pigmentation", "pigmentation"),
            ("Hair and scalp", "hair-and-scalp"),
            ("Medical dermatology", "medical-dermatology"),
            ("Laser and procedures", "laser-and-procedures"),
            ("Patient guides", "patient-guides"),
        ]
        for name, slug in categories:
            ContentCategory.objects.get_or_create(
                slug=slug,
                defaults={"name": name},
            )

    def create_settings(self, site):
        SiteSettings.objects.update_or_create(
            site=site,
            defaults={
                "clinic_name": "Aastha Skin & Dermato-Cosmetic Centre",
                "short_name": "Aastha Skin Centre",
                "tagline": (
                    "Dermatologist-led skin, hair and laser care in Jammu"
                ),
                "consultation_fee": 500,
                "currency_symbol": "₹",
                "follow_up_days": 10,
                "primary_mobile": "7006613362",
                "secondary_mobile": "9796676541",
                "whatsapp_mobile": "7006613362",
                "email": "aasthaskinsurgs@gmail.com",
                "instagram_url": (
                    "https://www.instagram.com/aastha_skin_centre/"
                ),
                "youtube_url": "https://www.youtube.com/@aasthaskincentre",
            },
        )

    def apply_common_fields(self, page, record):
        page.title = record["title"][:255]
        page.draft_title = page.title
        page.slug = record["slug"]
        page.seo_title = record.get("seo_title", "")[:255]
        page.search_description = record.get("search_description", "")[:255]
        page.eyebrow = record.get("eyebrow", "")[:120]
        page.introduction = record.get("introduction", "")
        page.show_consultation_sidebar = record.get(
            "show_consultation_sidebar",
            True,
        )
        page.show_clinic_choices = record.get("show_clinic_choices", True)
        page.show_medical_disclaimer = record.get(
            "show_medical_disclaimer",
            True,
        )
        page.review_status = "medical"

    def create_page(self, record, parent, doctor, clinics):
        model = PAGE_MODELS.get(record["page_type"])
        if model is None:
            raise CommandError(f"Unsupported page type: {record['page_type']}")
        page = model(title=record["title"][:255], slug=record["slug"])
        self.apply_common_fields(page, record)
        page.body = []

        path = normalise_path(record["path"])
        if isinstance(page, ContentIndexPage):
            page.index_kind = INDEX_KIND.get(path, "general")
            page.listing_order = "newest" if path == "/blog/" else "manual"
        elif isinstance(page, BlogPage):
            page.author = doctor
        elif isinstance(page, DoctorPage):
            page.doctor = doctor
        elif isinstance(page, ClinicPage):
            page.clinic = clinics.get(record["slug"])

        parent.add_child(instance=page)
        page.save_revision().publish()
        return page

    def resolve_blocks(
        self,
        blocks,
        path_map,
        prepend_home_hero=None,
    ):
        output = []
        if prepend_home_hero:
            output.append(
                (
                    "hero",
                    {
                        "eyebrow": prepend_home_hero.get("eyebrow", ""),
                        "heading": prepend_home_hero["title"],
                        "introduction": prepend_home_hero.get(
                            "introduction",
                            "",
                        ),
                        "image": None,
                        "video_url": "",
                        "media_position": "right",
                        "buttons": [
                            {
                                "link": {
                                    "label": "Book an appointment",
                                    "page": path_map.get("/book-appointment/"),
                                    "external_url": "",
                                    "new_tab": False,
                                },
                                "style": "primary",
                            },
                            {
                                "link": {
                                    "label": "Explore treatments",
                                    "page": path_map.get("/treatments/"),
                                    "external_url": "",
                                    "new_tab": False,
                                },
                                "style": "secondary",
                            },
                        ],
                        "layout": {
                            "width": "full",
                            "theme": "soft",
                            "text_alignment": "left",
                            "top_spacing": "none",
                            "bottom_spacing": "lg",
                            "anchor_id": "",
                            "hide_on_mobile": False,
                            "hide_on_desktop": False,
                        },
                    },
                )
            )

        for block in blocks:
            block_type = block["type"]
            raw_value = deepcopy(block["value"])
            if block_type == "advanced_html" and isinstance(raw_value, str):
                raw_value = {
                    "html": raw_value,
                    "layout": {
                        "width": "content",
                        "theme": "default",
                        "text_alignment": "left",
                        "top_spacing": "md",
                        "bottom_spacing": "md",
                        "anchor_id": "",
                        "hide_on_mobile": False,
                        "hide_on_desktop": False,
                    },
                }
            value = self.resolve_value(
                raw_value,
                path_map,
                convert_rich_text=block_type in {
                    "text",
                    "faq",
                    "accordion",
                },
            )
            output.append((block["type"], value))
        return output

    def resolve_value(self, value, path_map, convert_rich_text=False):
        if isinstance(value, list):
            return [
                self.resolve_value(
                    item,
                    path_map,
                    convert_rich_text=convert_rich_text,
                )
                for item in value
            ]
        if not isinstance(value, dict):
            if isinstance(value, str):
                value = self.insert_global_tokens(value)
                if convert_rich_text and "<a " in value:
                    return self.convert_rich_text_links(value, path_map)
            return value

        if "page_path" in value:
            page_path = value.pop("page_path", "")
            value["page"] = path_map.get(normalise_path(page_path)) if page_path else None
            if value["page"] is None and page_path:
                # Preserve unresolved paths as ordinary links.
                value["external_url"] = ""
                value["page"] = None

        external_url = value.get("external_url")
        if external_url in GLOBAL_LINK_ACTIONS:
            value["global_action"] = GLOBAL_LINK_ACTIONS[external_url]
            value["external_url"] = ""

        for key, item in list(value.items()):
            value[key] = self.resolve_value(
                item,
                path_map,
                convert_rich_text=convert_rich_text,
            )
        return value

    def insert_global_tokens(self, value):
        for current, token in GLOBAL_TEXT_REPLACEMENTS:
            value = value.replace(current, token)
        return value

    def convert_rich_text_links(self, markup, path_map):
        def replace(match):
            quote = match.group(1)
            href = match.group(2)
            target = path_map.get(normalise_path(href.split("#", 1)[0]))
            if target is None:
                return match.group(0)
            return f'<a linktype="page" id="{target.pk}"'

        return re.sub(
            r'<a\s+href=(["\'])(/[^"\']*)\1',
            replace,
            markup,
            flags=re.I,
        )
