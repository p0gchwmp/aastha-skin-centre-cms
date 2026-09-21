"""Verified public-source record for Dr. Cheena Langer.

The records here are intentionally short summaries with outbound links. We do not
republish third-party articles or images. Each item is tied to a source that was
manually checked before inclusion.
"""

from __future__ import annotations

from html import escape


DOCTOR_MEDIA_RECORDS = (
    {
        "date": "2026–27",
        "kind": "Professional role",
        "publisher": "IADVL Academy",
        "title": "IADVL Academy — Scholarships",
        "summary": (
            "The IADVL Academy committee page lists Dr. Cheena Langer under the "
            "Academy's 2026–27 assigned responsibility for Scholarships."
        ),
        "url": "https://www.iadvl.org/academy/academy-committee",
    },
    {
        "date": "2025",
        "kind": "Congress abstract",
        "publisher": "European Academy of Dermatology & Venereology",
        "title": "Emerging role of apremilast in hand dermatoses",
        "summary": (
            "EADV Congress 2025 abstract 4878 lists Cheena Langer and Vivek Mahajan, "
            "with Aastha Skin and Dermato-Cosmetic Centre, Jammu as Dr. Langer's affiliation."
        ),
        "url": (
            "https://eadv.org/wp-content/uploads/scientific-abstracts/"
            "EADV-congress-2025/Atopic-dermatitis-eczema.pdf"
        ),
    },
    {
        "date": "23 Feb 2025",
        "kind": "Authored article",
        "publisher": "Daily Excelsior",
        "title": "Combating Winter Acne Woes",
        "summary": (
            "A patient-education article on winter acne, skincare changes and when "
            "dermatological support may be useful."
        ),
        "url": "https://www.dailyexcelsior.com/combating-winter-acne-woes/",
    },
    {
        "date": "25 Aug 2024",
        "kind": "Authored article",
        "publisher": "Daily Excelsior",
        "title": "Fungal Infection of Skin: An Epidemic on the Rise",
        "summary": (
            "An educational article covering common signs, prevention and the "
            "importance of diagnosis-led treatment for fungal skin infection."
        ),
        "url": (
            "https://www.dailyexcelsior.com/"
            "fungal-infection-of-skin-an-epidemic-on-the-rise/"
        ),
    },
    {
        "date": "16 Jun 2024",
        "kind": "Authored article",
        "publisher": "Daily Excelsior",
        "title": "Sunscreen | The Shield Against Sun's Wrath",
        "summary": (
            "A practical overview of sunscreen selection, application, reapplication "
            "and photoprotection."
        ),
        "url": (
            "https://www.dailyexcelsior.com/"
            "sunscreen-the-shield-against-suns-wrath/"
        ),
    },
    {
        "date": "25 May 2024",
        "kind": "International lecture",
        "publisher": "Daily Excelsior",
        "title": "Melasma: Behind and Beyond — lecture in Wroclaw, Poland",
        "summary": (
            "Coverage of Dr. Langer's lecture at the 8th Continental Congress of "
            "Dermatology and 12th Controversies in Dermatology Conference."
        ),
        "url": (
            "https://www.dailyexcelsior.com/"
            "dr-cheena-langer-delivers-lecture-at-intl-dermatology-conference-in-poland/"
        ),
        "secondary_url": "https://www.termedia.pl/Konferencje/print?program=1312",
        "secondary_label": "Official programme",
    },
    {
        "date": "16 Dec 2023",
        "kind": "Conference leadership",
        "publisher": "Daily Excelsior",
        "title": "CUTICON JK annual conference",
        "summary": (
            "Conference coverage names Dr. Cheena Langer as organising chairperson "
            "of the IADVL Jammu & Kashmir Branch annual conference."
        ),
        "url": (
            "https://www.dailyexcelsior.com/news/archive/"
            "two-day-annual-conference-of-iadvl-cuticon-jk-inaugurated"
        ),
    },
    {
        "date": "7 Jul 2019",
        "kind": "Professional training",
        "publisher": "Daily Excelsior",
        "title": "Fellowship in Surgical & Cosmetic Dermatology",
        "summary": (
            "Daily Excelsior reported Dr. Langer's fellowship training at Sapienza "
            "University of Rome in Surgical & Cosmetic Dermatology."
        ),
        "url": (
            "https://www.dailyexcelsior.com/news/archive/"
            "dr-cheena-awarded-fellowship-by-sapienza-university"
        ),
    },
    {
        "date": "2016",
        "kind": "Peer-reviewed publication",
        "publisher": "Indian Journal of Dermatology / PubMed",
        "title": "Bleomycin Containing Chemotherapeutic Regimen Induced Acquired Partial Lipodystrophy",
        "summary": (
            "PubMed lists Cheena Langer as a co-author on this Indian Journal of "
            "Dermatology case report (PMID 26955139)."
        ),
        "url": "https://pubmed.ncbi.nlm.nih.gov/26955139/",
    },
    {
        "date": "Current listing",
        "kind": "Professional organisation",
        "publisher": "IADVL",
        "title": "Artificial Intelligence Special Interest Group",
        "summary": (
            "IADVL's Special Interest Groups page lists Dr. Cheena Langer among "
            "the members of the Artificial Intelligence SIG."
        ),
        "url": "https://www.iadvl.org/academy/special-interest-groups",
    },
)


def doctor_media_records() -> list[dict[str, str]]:
    """Return copy-safe records for templates/admin views."""

    return [dict(item) for item in DOCTOR_MEDIA_RECORDS]


def doctor_media_markup() -> str:
    """Render a compact public profile section with outbound source links."""

    cards = []
    for item in DOCTOR_MEDIA_RECORDS:
        secondary = ""
        if item.get("secondary_url"):
            secondary = (
                f'<a href="{escape(item["secondary_url"], quote=True)}" '
                'target="_blank" rel="noopener noreferrer">'
                f'{escape(item.get("secondary_label", "Second source"))} ↗</a>'
            )
        cards.append(
            '<article class="doctor-media-card">'
            '<div class="doctor-media-meta">'
            f'<span>{escape(item["kind"])}</span>'
            f'<time>{escape(item["date"])}</time>'
            '</div>'
            f'<h3>{escape(item["title"])}</h3>'
            f'<p>{escape(item["summary"])}</p>'
            '<div class="doctor-media-source">'
            f'<span>{escape(item["publisher"])}</span>'
            f'<a href="{escape(item["url"], quote=True)}" '
            'target="_blank" rel="noopener noreferrer">View original source ↗</a>'
            f'{secondary}'
            '</div>'
            '</article>'
        )

    return (
        '<section class="doctor-media-section" id="professional-work-media" '
        'aria-labelledby="professional-work-media-title">'
        '<div class="doctor-media-heading">'
        '<div><span class="v37-kicker">Selected external record</span>'
        '<h2 id="professional-work-media-title">Professional work, publications &amp; media</h2></div>'
        '<p>A curated selection of independently published articles, conference records, '
        'research and professional listings connected to Dr. Cheena Langer. '
        'Links open the original source.</p>'
        '</div>'
        '<div class="doctor-media-grid">'
        + "".join(cards)
        + '</div>'
        '<p class="doctor-media-note">External publications and organisations remain '
        'responsible for their own content. Inclusion here is a source record, not an '
        'endorsement or a claim that every historic detail remains current.</p>'
        '</section>'
    )
