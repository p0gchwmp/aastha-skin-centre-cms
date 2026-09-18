"""Local-search architecture for patient-useful Jammu area hubs.

These pages mirror the useful part of large directory SEO: clear locality intent,
strong internal linking and branch/service context. They deliberately avoid
"best" claims, fake branch locations and service×location doorway-page spam.
"""

from __future__ import annotations


LOCAL_SEARCH_AREAS = (
    {"slug": "gandhi-nagar", "name": "Gandhi Nagar", "kind": "jammu"},
    {"slug": "janipur", "name": "Janipur", "kind": "jammu"},
    {"slug": "talab-tillo", "name": "Talab Tillo", "kind": "jammu"},
    {"slug": "bakshi-nagar", "name": "Bakshi Nagar", "kind": "jammu"},
    {"slug": "rehari", "name": "Rehari", "kind": "jammu"},
    {"slug": "trikuta-nagar", "name": "Trikuta Nagar", "kind": "jammu"},
    {"slug": "roop-nagar", "name": "Roop Nagar", "kind": "jammu"},
    {"slug": "bantalab", "name": "Bantalab", "kind": "jammu"},
    {"slug": "nagrota", "name": "Nagrota", "kind": "jammu"},
    {"slug": "satwari", "name": "Satwari", "kind": "jammu"},
    {"slug": "sidhra", "name": "Sidhra", "kind": "jammu"},
    {"slug": "kathua", "name": "Kathua", "kind": "regional"},
    {"slug": "udhampur", "name": "Udhampur", "kind": "regional"},
    {"slug": "rajouri", "name": "Rajouri", "kind": "regional"},
    {"slug": "poonch", "name": "Poonch", "kind": "regional"},
    {"slug": "reasi", "name": "Reasi", "kind": "regional"},
    {"slug": "katra", "name": "Katra", "kind": "regional"},
    {"slug": "pathankot", "name": "Pathankot", "kind": "regional"},
)

AREA_BY_SLUG = {item["slug"]: item for item in LOCAL_SEARCH_AREAS}
LOCAL_SEARCH_AREA_SLUGS = frozenset(AREA_BY_SLUG)

PRIORITY_TREATMENT_SLUGS = (
    "acne-treatment",
    "acne-scar-treatment",
    "pigmentation-treatment",
    "melasma-treatment",
    "hair-fall-treatment",
    "seborrheic-dermatitis-dandruff",
    "prp-gfc-hair-treatment",
    "hair-transplant",
    "laser-hair-reduction",
    "chemical-peels",
    "fractional-co2-laser",
    "botulinum-toxin-dermal-fillers",
)


def area_title(area: dict[str, str]) -> str:
    if area["kind"] == "jammu":
        return f"Dermatologist near {area['name']}, Jammu"
    return f"Dermatology care in Jammu for patients from {area['name']}"


def area_description(area: dict[str, str]) -> str:
    if area["kind"] == "jammu":
        return (
            f"Looking for dermatologist-led skin, hair and laser care near "
            f"{area['name']}, Jammu? Explore Aastha Skin Centre services, "
            "clinic locations and appointment options."
        )
    return (
        f"Planning dermatologist-led skin, hair or laser care in Jammu from "
        f"{area['name']}? Explore Aastha Skin Centre services, Jammu clinic "
        "locations and appointment options before travelling."
    )


def area_intro(area: dict[str, str]) -> str:
    if area["kind"] == "jammu":
        return (
            f"Aastha Skin Centre provides dermatologist-led care in Jammu for "
            f"patients searching from {area['name']}. Choose between the Karan "
            "Nagar and Paloura Chowk clinics, then explore the concern or "
            "treatment page that matches what you want assessed."
        )
    return (
        f"Aastha Skin Centre's physical clinics are in Jammu. This page helps "
        f"patients travelling from {area['name']} review services, branch details "
        "and appointment options before planning a visit."
    )


def related_area_slugs(slug: str, limit: int = 8) -> tuple[str, ...]:
    current = AREA_BY_SLUG.get(slug)
    if current is None:
        return ()
    same_kind = [
        item["slug"]
        for item in LOCAL_SEARCH_AREAS
        if item["slug"] != slug and item["kind"] == current["kind"]
    ]
    other_kind = [
        item["slug"]
        for item in LOCAL_SEARCH_AREAS
        if item["slug"] != slug and item["kind"] != current["kind"]
    ]
    return tuple((same_kind + other_kind)[:limit])
