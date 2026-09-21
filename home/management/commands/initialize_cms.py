import json
import os
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.core.management import call_command
from django.core.management.base import BaseCommand
from wagtail.models import Site

from home.approved_media import sync_approved_doctor_media
from home.exact_editor_sync import (
    sync_all_exact_layout_editor_fields,
    sync_uploaded_homepage_images,
)
from home.local_search import LOCAL_SEARCH_AREAS, area_description, area_intro, area_title
from home.seo_verification import ensure_candidate_seo_profiles
from home.models import (
    BlogPage,
    ClinicPage,
    ContentIndexPage,
    Doctor,
    DoctorPage,
    HomePage,
    SiteSettings,
    StandardPage,
    TreatmentPage,
)


APPROVED_FACEBOOK_URL = "https://www.facebook.com/aasthaskincentre/"
APPROVED_ANALYTICS_ID = "G-G5DQPDJ53P"
APPROVED_SEARCH_CONSOLE_VERIFICATION = (
    "LejmOPRWDnzDg6WWoVLxvPwjRBWkflLm_P81L0EbEkE"
)
APPROVED_HOMEPAGE_SEO_TITLE = "Dermatologist-led Skin, Hair & Laser Care in Jammu"
APPROVED_HOMEPAGE_META_DESCRIPTION = (
    "Dermatologist-led skin, hair, laser and cosmetic care in Jammu at Aastha "
    "Skin & Dermato-Cosmetic Centre. Book a consultation with Dr. Cheena Langer."
)
LEGACY_LOCATIONS_META_DESCRIPTION = (
    "Find Aastha Skin Centre at Karan Nagar and Paloura Chowk in Jammu."
)
APPROVED_LOCATIONS_META_DESCRIPTION = (
    "Find Aastha Skin Centre clinics in Jammu at Karan Nagar and Paloura Chowk, "
    "with branch details, contact information and directions."
)
APPROVED_DOCTOR_REGISTRATION_DETAILS = (
    "J&K Medical Council Registration No. 9538 (16 Jan 2007)"
)
LEGACY_FACEBOOK_URLS = {
    "",
    "https://facebook.com",
    "https://facebook.com/",
    "https://www.facebook.com",
    "https://www.facebook.com/",
}


def sync_approved_homepage_seo(home):
    """Fill approved homepage metadata only when editors have left it blank."""
    if home is None:
        return []

    updates = {}
    if not (home.seo_title or "").strip():
        updates["seo_title"] = APPROVED_HOMEPAGE_SEO_TITLE
    if not (home.search_description or "").strip():
        updates["search_description"] = APPROVED_HOMEPAGE_META_DESCRIPTION

    if not updates:
        return []

    for field_name, value in updates.items():
        setattr(home, field_name, value)
    home.save(update_fields=list(updates))
    return list(updates)


def sync_approved_locations_seo():
    """Upgrade only the known legacy locations description."""
    locations = (
        HomePage.objects.first()
        .get_children()
        .filter(slug="locations")
        .specific()
        .first()
        if HomePage.objects.first()
        else None
    )
    if locations is None:
        return False

    current = (locations.search_description or "").strip()
    if current not in {"", LEGACY_LOCATIONS_META_DESCRIPTION}:
        return False

    locations.search_description = APPROVED_LOCATIONS_META_DESCRIPTION
    locations.save(update_fields=["search_description"])
    return True


def sync_non_indexable_utility_pages():
    """Keep post-submission utility pages out of search indexes."""
    home = HomePage.objects.first()
    if home is None:
        return []

    updated = []
    page = (
        home.get_descendants()
        .filter(slug="appointment-request-received")
        .specific()
        .first()
    )
    if page is not None and not getattr(page, "noindex", False):
        page.noindex = True
        page.save(update_fields=["noindex"])
        updated.append("/appointment-request-received/")
    return updated


@lru_cache(maxsize=1)
def legacy_seed_seo_titles():
    """Return the original imported SEO titles used by the v28 starter site."""
    path = Path(settings.BASE_DIR) / "seed_data" / "v28-content.json"
    if not path.exists():
        return {}
    records = json.loads(path.read_text(encoding="utf-8"))
    return {
        (record.get("page_type", ""), record.get("slug", "")): (
            record.get("seo_title") or ""
        ).strip()
        for record in records
        if record.get("slug")
    }


def sync_local_search_pages():
    """Create the staged local-search graph without indexing unverified areas.

    Existing pages are left editor-owned. Newly created pages are live so the
    staging renderer/link audits can exercise them, but every route remains
    noindex until local facts are explicitly verified in the SEO profiles.
    """
    home = HomePage.objects.first()
    if home is None:
        return {"created": [], "existing": []}

    areas = (
        home.get_children()
        .filter(slug="areas")
        .specific()
        .first()
    )
    created = []
    existing = []

    if areas is None:
        areas = ContentIndexPage(
            title="Areas We Serve from Jammu",
            slug="areas",
            seo_title="Dermatology Care Areas | Jammu",
            search_description=(
                "Explore dermatologist-led skin, hair and laser care in Jammu "
                "for patients searching across Jammu neighbourhoods and nearby "
                "regional towns."
            ),
            eyebrow="Local care · Jammu",
            introduction=(
                "Use these area guides to compare Aastha Skin Centre's two "
                "Jammu clinics, explore treatment information and plan an "
                "appointment. Physical clinic locations are shown clearly on "
                "every page."
            ),
            index_kind="general",
            cards_per_page=24,
            listing_order="alphabetical",
            show_consultation_sidebar=False,
            show_clinic_choices=False,
            show_medical_disclaimer=False,
            noindex=True,
        )
        home.add_child(instance=areas)
        areas.save_revision().publish()
        created.append("/areas/")
    else:
        existing.append("/areas/")

    for area in LOCAL_SEARCH_AREAS:
        page = (
            areas.get_children()
            .filter(slug=area["slug"])
            .specific()
            .first()
        )
        if page is not None:
            existing.append(f"/areas/{area['slug']}/")
            continue

        page = StandardPage(
            title=area_title(area),
            slug=area["slug"],
            seo_title=area_title(area),
            search_description=area_description(area),
            eyebrow="Local care · Jammu",
            introduction=area_intro(area),
            layout_mode="hybrid",
            show_consultation_sidebar=False,
            show_clinic_choices=False,
            show_medical_disclaimer=False,
            noindex=True,
        )
        areas.add_child(instance=page)
        page.save_revision().publish()
        created.append(f"/areas/{area['slug']}/")

    return {"created": created, "existing": existing}


def sync_justdial_style_treatment_titles():
    """Add Jammu intent only where treatment SEO titles are blank/default.

    Editors keep full ownership of custom SEO titles.
    """
    updated = []
    legacy_titles = legacy_seed_seo_titles()
    for page in TreatmentPage.objects.live().public():
        current = (page.seo_title or "").strip()
        title = (page.title or "").strip()
        legacy = legacy_titles.get(("treatment", page.slug), "")
        if current not in {"", title, legacy}:
            continue
        candidate = title if "jammu" in title.casefold() else f"{title} in Jammu"
        if candidate == current or len(candidate) > 65:
            continue
        page.seo_title = candidate
        page.save(update_fields=["seo_title"])
        updated.append(page.get_url() or page.url_path)
    return updated


def sync_justdial_style_profile_titles():
    """Add local intent to default doctor/clinic SEO titles only."""
    updated = []
    legacy_titles = legacy_seed_seo_titles()

    for page in DoctorPage.objects.live().public().select_related("doctor"):
        current = (page.seo_title or "").strip()
        title = (page.title or "").strip()
        legacy = legacy_titles.get(("doctor", page.slug), "")
        if current not in {"", title, legacy}:
            continue
        doctor = page.doctor
        name = doctor.name if doctor else title
        candidate = (
            name if "jammu" in name.casefold()
            else f"{name}, Dermatologist in Jammu"
        )
        if candidate != current and len(candidate) <= 65:
            page.seo_title = candidate
            page.save(update_fields=["seo_title"])
            updated.append(page.get_url() or page.url_path)

    for page in ClinicPage.objects.live().public().select_related("clinic"):
        current = (page.seo_title or "").strip()
        title = (page.title or "").strip()
        legacy = legacy_titles.get(("clinic", page.slug), "")
        if current not in {"", title, legacy}:
            continue
        clinic = page.clinic
        locality = clinic.name if clinic else title
        candidate = f"Dermatologist & Skin Clinic in {locality}, Jammu"
        if "jammu" in locality.casefold():
            candidate = f"Dermatologist & Skin Clinic in {locality}"
        if candidate != current and len(candidate) <= 65:
            page.seo_title = candidate
            page.save(update_fields=["seo_title"])
            updated.append(page.get_url() or page.url_path)

    return updated


def sync_approved_doctor_registration():
    """Fill the council registration only when the doctor record is blank."""
    doctor = Doctor.objects.filter(slug="dr-cheena-langer").first()
    if doctor is None:
        return False
    if (doctor.registration_details or "").strip():
        return False

    doctor.registration_details = APPROVED_DOCTOR_REGISTRATION_DETAILS
    doctor.save(update_fields=["registration_details"])
    return True


def sync_approved_site_settings(site):
    """Fill approved blank/placeholder settings without overwriting later edits."""
    if site is None:
        return []

    site_settings, _ = SiteSettings.objects.get_or_create(site=site)
    updates = {}

    current_facebook_url = (site_settings.facebook_url or "").strip()
    if current_facebook_url in LEGACY_FACEBOOK_URLS:
        updates["facebook_url"] = APPROVED_FACEBOOK_URL

    if not (site_settings.analytics_id or "").strip():
        updates["analytics_id"] = APPROVED_ANALYTICS_ID

    if not (site_settings.search_console_verification or "").strip():
        updates[
            "search_console_verification"
        ] = APPROVED_SEARCH_CONSOLE_VERIFICATION

    if not updates:
        return []

    for field_name, value in updates.items():
        setattr(site_settings, field_name, value)
    site_settings.save(update_fields=list(updates))
    return list(updates)


class Command(BaseCommand):
    help = "Import the v28 starter site only when the CMS is genuinely empty."

    def sync_editor_state(self):
        exact_layouts = sync_all_exact_layout_editor_fields()
        if exact_layouts:
            self.stdout.write(
                f"Prepared simple text/image/link editing for {exact_layouts} pages."
            )

        image_updates = sync_uploaded_homepage_images()
        if image_updates:
            self.stdout.write(
                "Connected uploaded Dr. Cheena Langer photos to: "
                + ", ".join(image_updates)
                + "."
            )

        approved_media = sync_approved_doctor_media(
            Site.objects.filter(is_default_site=True).first()
        )
        if approved_media["updates"]:
            self.stdout.write(
                "Connected approved real Dr. Cheena Langer media to: "
                + ", ".join(approved_media["updates"])
                + "."
            )
        if approved_media["warning"]:
            self.stdout.write(
                self.style.WARNING(
                    "Approved doctor media bootstrap skipped safely: "
                    + approved_media["warning"]
                )
            )

    def handle(self, *args, **options):
        configured_host = (
            os.environ.get("SITE_HOSTNAME")
            or os.environ.get("RENDER_EXTERNAL_HOSTNAME")
        )
        site = Site.objects.filter(is_default_site=True).first()
        if configured_host and site and site.hostname != configured_host:
            site.hostname = configured_host
            site.port = 443
            site.save(update_fields=["hostname", "port"])
            self.stdout.write(
                f"Default site hostname updated to {configured_host}."
            )

        updated_fields = sync_approved_site_settings(site)
        if updated_fields:
            self.stdout.write(
                "Approved site settings applied: "
                + ", ".join(updated_fields)
                + "."
            )

        home = HomePage.objects.first()
        homepage_seo_updates = sync_approved_homepage_seo(home)
        if homepage_seo_updates:
            self.stdout.write(
                "Approved homepage SEO applied: "
                + ", ".join(homepage_seo_updates)
                + "."
            )
        if sync_approved_locations_seo():
            self.stdout.write("Approved locations SEO description applied.")
        utility_noindex_updates = sync_non_indexable_utility_pages()
        if utility_noindex_updates:
            self.stdout.write(
                "Protected utility pages from indexing: "
                + ", ".join(utility_noindex_updates)
                + "."
            )
        has_content = (
            TreatmentPage.objects.exists()
            or BlogPage.objects.exists()
            or (home is not None and home.get_children().exists())
        )
        if has_content:
            local_search = sync_local_search_pages()
            if local_search["created"]:
                self.stdout.write(
                    "Created staged noindex local-search pages: "
                    + ", ".join(local_search["created"])
                    + "."
                )
            local_title_updates = sync_justdial_style_treatment_titles()
            if local_title_updates:
                self.stdout.write(
                    f"Applied Jammu-intent SEO titles to {len(local_title_updates)} "
                    "treatment page(s) with blank/default titles."
                )
            profile_title_updates = sync_justdial_style_profile_titles()
            if profile_title_updates:
                self.stdout.write(
                    f"Applied local-intent SEO titles to {len(profile_title_updates)} "
                    "doctor/clinic page(s) with blank/default titles."
                )
            seo_profiles = ensure_candidate_seo_profiles()
            if seo_profiles["created"] or seo_profiles["updated"]:
                self.stdout.write(
                    "Prepared SEO verification profiles without marking them verified."
                )
            if sync_approved_doctor_registration():
                self.stdout.write(
                    "Applied verified J&K Medical Council registration to blank doctor record."
                )
            self.sync_editor_state()
            self.stdout.write(
                "CMS already contains pages; starter import skipped."
            )
            return
        call_command("import_v28_site")

        # A fresh import creates the site-specific settings record.
        site = Site.objects.filter(is_default_site=True).first()
        sync_approved_site_settings(site)
        sync_approved_homepage_seo(HomePage.objects.first())
        sync_approved_locations_seo()
        sync_non_indexable_utility_pages()
        sync_local_search_pages()
        sync_justdial_style_treatment_titles()
        sync_justdial_style_profile_titles()
        ensure_candidate_seo_profiles()
        sync_approved_doctor_registration()
        self.sync_editor_state()
