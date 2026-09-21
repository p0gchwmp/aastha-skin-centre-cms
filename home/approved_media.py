"""Safe bootstrap for already-approved real clinic/doctor media.

This module never overwrites an editor-selected image.  It exists so a fresh
staging/production database can materialise the same real Dr. Cheena Langer
photograph that the verified renderer already uses as its public fallback.
"""

from __future__ import annotations

from io import BytesIO
from urllib.request import Request, urlopen

from django.core.files.base import ContentFile
from PIL import Image as PILImage
from wagtail.images import get_image_model
from wagtail.models import Site


APPROVED_DOCTOR_PORTRAIT_URL = (
    "https://www.aasthaskincentre.in/media/images/"
    "DSC_5241_1.max-900x900.format-webp.webp"
)
APPROVED_DOCTOR_PORTRAIT_TITLE = "Dr Cheena Langer — approved website portrait"
APPROVED_DOCTOR_PORTRAIT_FILENAME = "dr-cheena-langer-approved.webp"
MAX_APPROVED_MEDIA_BYTES = 8 * 1024 * 1024


def _download_approved_portrait(url: str) -> bytes:
    request = Request(
        url,
        headers={
            "User-Agent": "AasthaCMS/1.0 (+https://www.aasthaskincentre.in/)",
            "Accept": "image/avif,image/webp,image/png,image/jpeg,*/*;q=0.5",
        },
    )
    with urlopen(request, timeout=15) as response:
        payload = response.read(MAX_APPROVED_MEDIA_BYTES + 1)

    if not payload:
        raise ValueError("approved doctor image source returned an empty response")
    if len(payload) > MAX_APPROVED_MEDIA_BYTES:
        raise ValueError("approved doctor image source exceeded the 8 MB safety limit")

    # Reject HTML/error bodies and corrupt payloads before they can enter Wagtail.
    with PILImage.open(BytesIO(payload)) as candidate:
        candidate.verify()

    return payload


def _materialise_portrait(fetcher=None):
    image_model = get_image_model()
    existing = (
        image_model.objects.filter(title=APPROVED_DOCTOR_PORTRAIT_TITLE)
        .order_by("id")
        .first()
    )
    if existing is not None:
        return existing, False

    fetcher = fetcher or _download_approved_portrait
    payload = fetcher(APPROVED_DOCTOR_PORTRAIT_URL)
    if not payload:
        raise ValueError("approved media fetcher returned no image bytes")

    # Validate injected/test fetchers as well.
    with PILImage.open(BytesIO(payload)) as candidate:
        candidate.verify()

    image = image_model(
        title=APPROVED_DOCTOR_PORTRAIT_TITLE,
        file=ContentFile(payload, name=APPROVED_DOCTOR_PORTRAIT_FILENAME),
    )
    image.save()
    return image, True


def sync_approved_doctor_media(site=None, fetcher=None) -> dict[str, object]:
    """Fill blank doctor/social slots from existing or approved real media.

    Selection order:
    1. Existing editor-selected Doctor photo.
    2. Existing editor-selected homepage doctor image.
    3. Previously materialised approved portrait.
    4. Download the already-approved public fallback image.

    Existing values are never replaced.  Network/source failures are returned as
    a warning so deployment remains fail-safe and release sign-off stays blocked.
    """

    from .models import Doctor, HomePage, SiteSettings

    site = site or Site.objects.filter(is_default_site=True).first()
    doctor = Doctor.objects.filter(slug="dr-cheena-langer").first()
    home = HomePage.objects.first()
    site_settings = SiteSettings.for_site(site) if site is not None else None

    needs_media = bool(
        (doctor is not None and not doctor.photo_id)
        or (
            home is not None
            and hasattr(home, "doctor_section_image_id")
            and not home.doctor_section_image_id
        )
        or (site_settings is not None and not site_settings.default_social_image_id)
    )
    if not needs_media:
        return {
            "updates": [],
            "created_image": False,
            "warning": "",
            "source": "existing editor media",
        }

    candidate = None
    source = ""
    if doctor is not None and doctor.photo_id:
        candidate = doctor.photo
        source = "existing doctor photo"
    elif (
        home is not None
        and hasattr(home, "doctor_section_image_id")
        and home.doctor_section_image_id
    ):
        candidate = home.doctor_section_image
        source = "existing homepage doctor image"
    else:
        image_model = get_image_model()
        candidate = (
            image_model.objects.filter(title=APPROVED_DOCTOR_PORTRAIT_TITLE)
            .order_by("id")
            .first()
        )
        if candidate is not None:
            source = "materialised approved portrait"

    created_image = False
    if candidate is None:
        try:
            candidate, created_image = _materialise_portrait(fetcher=fetcher)
            source = "approved current-site portrait"
        except Exception as exc:
            return {
                "updates": [],
                "created_image": False,
                "warning": f"{exc.__class__.__name__}: {exc}",
                "source": APPROVED_DOCTOR_PORTRAIT_URL,
            }

    updates: list[str] = []

    if doctor is not None and not doctor.photo_id:
        doctor.photo = candidate
        doctor.save(update_fields=["photo"])
        doctor.save_revision().publish()
        updates.append("doctor profile image")

    if (
        home is not None
        and hasattr(home, "doctor_section_image_id")
        and not home.doctor_section_image_id
    ):
        home.doctor_section_image = candidate
        home.save(update_fields=["doctor_section_image"])
        home.save_revision().publish()
        updates.append("homepage doctor image")

    if site_settings is not None and not site_settings.default_social_image_id:
        site_settings.default_social_image = candidate
        site_settings.save(update_fields=["default_social_image"])
        updates.append("default social image")

    return {
        "updates": updates,
        "created_image": created_image,
        "warning": "",
        "source": source,
        "image_id": getattr(candidate, "pk", None),
        "image_title": getattr(candidate, "title", ""),
    }
