"""Route-specific clinical image galleries sourced from the clinic Drive.

The route map is intentionally explicit. Images are included only when the
folder subject matches an existing public condition or treatment page.
"""

from __future__ import annotations

from html import escape
from urllib.parse import quote, urlsplit

CLINICAL_RESULT_GALLERIES = {'/treatments/acne-treatment/': {'title': 'Acne treatment', 'images': [{'id': '1B24EWwRQ4byTzcVsaZjtSJpi8DBZR3Hz', 'alt': 'Clinic-supplied before-and-after photograph for acne treatment (1 of 1).', 'width': 1200, 'height': 900}]}, '/treatments/acne-scar-treatment/': {'title': 'Acne-scar treatment', 'images': [{'id': '1AYptjdT9M1bYfSjPfujDR52J2tf-AMs8', 'alt': 'Clinic-supplied before-and-after photograph for acne-scar treatment (1 of 4).', 'width': 1200, 'height': 900}, {'id': '1imkT5uTnocWv8tD6XZj9Ynjg2d3807US', 'alt': 'Clinic-supplied before-and-after photograph for acne-scar treatment (2 of 4).', 'width': 1200, 'height': 900}, {'id': '1JXuYIr4CNw8vhuc7BTbMzmX92xrDMq-w', 'alt': 'Clinic-supplied before-and-after photograph for acne-scar treatment (3 of 4).', 'width': 1200, 'height': 900}, {'id': '10cF6qpYCvrAP1fAlQiAkIYPdUuQl79JH', 'alt': 'Clinic-supplied before-and-after photograph for acne-scar treatment (4 of 4).', 'width': 1200, 'height': 900}]}, '/treatments/alopecia-areata-treatment/': {'title': 'Alopecia areata treatment', 'images': [{'id': '1Aq6pl2EFNvrqpP8_9uudm95-1T0yYCyx', 'alt': 'Clinic-supplied before-and-after photograph for alopecia areata treatment (1 of 1).', 'width': 1200, 'height': 900}]}, '/treatments/contact-dermatitis-treatment/': {'title': 'Contact dermatitis treatment', 'images': [{'id': '1E2hhjp3vS3HGrTiJghDLH6NifqL3ZpzY', 'alt': 'Clinic-supplied before-and-after photograph for contact dermatitis treatment (1 of 1).', 'width': 1200, 'height': 900}]}, '/treatments/dark-circles-under-eye-treatment/': {'title': 'Dark-circle treatment', 'images': [{'id': '1JSTRUclVVaDvqqNUfFq6euTXVlhuPQOg', 'alt': 'Clinic-supplied before-and-after photograph for dark-circle treatment (1 of 1).', 'width': 1200, 'height': 900}]}, '/treatments/fungal-infection-treatment/': {'title': 'Fungal infection treatment', 'images': [{'id': '1kBe8mUSIHBc0ggb1AEDZMn4qjYrh9VMe', 'alt': 'Clinic-supplied before-and-after photograph for fungal infection treatment (1 of 1).', 'width': 1200, 'height': 900}]}, '/treatments/hair-fall-treatment/': {'title': 'Hair-fall treatment', 'images': [{'id': '1JHMHRJoylNi1Q9e6Ad8H5RV3--Q2ua0w', 'alt': 'Clinic-supplied before-and-after photograph for hair-fall treatment (1 of 6).', 'width': 1440, 'height': 1440}, {'id': '1p3FjFKbieTFnb-njA3eccUuW_2y_IYmf', 'alt': 'Clinic-supplied before-and-after photograph for hair-fall treatment (2 of 6).', 'width': 1200, 'height': 900}, {'id': '1J1kwH7mB8BVv_0WWqdDAWBipiogc3RrN', 'alt': 'Clinic-supplied before-and-after photograph for hair-fall treatment (3 of 6).', 'width': 1200, 'height': 900}, {'id': '1BDJecxtvjRcQYOSJB9qXkDM43ikXJebL', 'alt': 'Clinic-supplied before-and-after photograph for hair-fall treatment (4 of 6).', 'width': 1200, 'height': 900}, {'id': '1PkfCRBCi0oKNQhmn5J-NLcNKrqxiGvtN', 'alt': 'Clinic-supplied before-and-after photograph for hair-fall treatment (5 of 6).', 'width': 1200, 'height': 900}, {'id': '1JC73h8jjQ4zyvV3qEGY_GEUiB_xBfeKq', 'alt': 'Clinic-supplied before-and-after photograph for hair-fall treatment (6 of 6).', 'width': 1200, 'height': 900}]}, '/treatments/psoriasis-treatment/': {'title': 'Psoriasis treatment', 'images': [{'id': '1F8_n027yT5swg1gnMDOFnP9hN4mBGojg', 'alt': 'Clinic-supplied before-and-after photograph for psoriasis treatment (1 of 1).', 'width': 1440, 'height': 1440}]}, '/treatments/wart-mole-skin-tag-removal/': {'title': 'Wart treatment', 'images': [{'id': '1F_K8CtDmgUARJiTXz5GSyVgeXihnNI5W', 'alt': 'Clinic-supplied before-and-after photograph for wart treatment (1 of 1).', 'width': 1200, 'height': 900}]}, '/treatments/botulinum-toxin-dermal-fillers/': {'title': 'Botulinum toxin and dermal filler treatment', 'images': [{'id': '1LJa6J_5hImG_iTFMepzUzFWWcjY8lCf1', 'alt': 'Clinic-supplied before-and-after photograph for botulinum toxin and dermal filler treatment (1 of 9).', 'width': 1440, 'height': 1440}, {'id': '1QCNkyqWK9tW0qtotGxPA_SHOMKx5Cziv', 'alt': 'Clinic-supplied before-and-after photograph for botulinum toxin and dermal filler treatment (2 of 9).', 'width': 1200, 'height': 900}, {'id': '1_KFiP2ERDm0N11PPWHkfB2QCK56Cd7fS', 'alt': 'Clinic-supplied before-and-after photograph for botulinum toxin and dermal filler treatment (3 of 9).', 'width': 1200, 'height': 900}, {'id': '1WuRRioPlmgPkmjU3r2SgMPRvanDvaGpt', 'alt': 'Clinic-supplied before-and-after photograph for botulinum toxin and dermal filler treatment (4 of 9).', 'width': 1200, 'height': 900}, {'id': '1HhgpMpbz3dmboYSsXdyQfFhgPOzKie6d', 'alt': 'Clinic-supplied before-and-after photograph for botulinum toxin and dermal filler treatment (5 of 9).', 'width': 1200, 'height': 900}, {'id': '1XWKz40y4UniHthNXj3CtWQjwl78Zfi-v', 'alt': 'Clinic-supplied before-and-after photograph for botulinum toxin and dermal filler treatment (6 of 9).', 'width': 1200, 'height': 900}, {'id': '15qRIGJgAAdWkuS9D7pH-V-l_QKCUw9Rh', 'alt': 'Clinic-supplied before-and-after photograph for botulinum toxin and dermal filler treatment (7 of 9).', 'width': 1200, 'height': 900}, {'id': '1noAPVZmnzibqGf6on5gKeBq5h2DCQ2Lk', 'alt': 'Clinic-supplied before-and-after photograph for botulinum toxin and dermal filler treatment (8 of 9).', 'width': 1200, 'height': 900}, {'id': '17HT5Ch6CsmcH4cflImdj8nJ_jBcB1n_9', 'alt': 'Clinic-supplied before-and-after photograph for botulinum toxin and dermal filler treatment (9 of 9).', 'width': 1200, 'height': 900}]}, '/treatments/chemical-peels/': {'title': 'Chemical peel treatment', 'images': [{'id': '1wGwCqAyJ_A5899cc8mnMcwxWDRBhyNCo', 'alt': 'Clinic-supplied before-and-after photograph for chemical peel treatment (1 of 1).', 'width': 1200, 'height': 900}]}, '/treatments/hair-transplant/': {'title': 'Hair transplant', 'images': [{'id': '1NqpjjzEFQ72eLW6-JRtzhbh0_paSbH0K', 'alt': 'Clinic-supplied before-and-after photograph for hair transplant (1 of 2).', 'width': 1200, 'height': 900}, {'id': '15KQX4jJLTThiIDvEB-643tXFLD1jW7eo', 'alt': 'Clinic-supplied before-and-after photograph for hair transplant (2 of 2).', 'width': 1200, 'height': 900}]}, '/treatments/laser-hair-reduction/': {'title': 'Laser hair reduction', 'images': [{'id': '10zcynWjf1h8JmKszT7v8sVbd4DyuOHDl', 'alt': 'Clinic-supplied before-and-after photograph for laser hair reduction (1 of 7).', 'width': 1200, 'height': 900}, {'id': '1fw2gc4N0Ldl0kv7dMUjdxMB6gXSrssGY', 'alt': 'Clinic-supplied before-and-after photograph for laser hair reduction (2 of 7).', 'width': 1200, 'height': 900}, {'id': '1F2b2MlvtPq-AaM-xNJTZdTJk6xGm_p-h', 'alt': 'Clinic-supplied before-and-after photograph for laser hair reduction (3 of 7).', 'width': 1200, 'height': 900}, {'id': '1da-LKfhfJZF2f8PMf9xBdISMIxX3jyR8', 'alt': 'Clinic-supplied before-and-after photograph for laser hair reduction (4 of 7).', 'width': 1200, 'height': 900}, {'id': '1axfrEzKTVf9FnMAV4FIsl1q_uxI08tn1', 'alt': 'Clinic-supplied before-and-after photograph for laser hair reduction (5 of 7).', 'width': 1200, 'height': 900}, {'id': '1_1ppUPpCPL83k3GiWWe3IHqwAlAJRn67', 'alt': 'Clinic-supplied before-and-after photograph for laser hair reduction (6 of 7).', 'width': 1200, 'height': 900}, {'id': '1QVEMGvdUNLX5HWwIMfhg8-pLklkFS-3A', 'alt': 'Clinic-supplied before-and-after photograph for laser hair reduction (7 of 7).', 'width': 1200, 'height': 900}]}, '/treatments/laser-tattoo-removal/': {'title': 'Laser tattoo removal', 'images': [{'id': '1nKmZzH03EHOzg8CTI0oSFYxiOZBfwWcu', 'alt': 'Clinic-supplied before-and-after photograph for laser tattoo removal (1 of 1).', 'width': 1200, 'height': 900}]}, '/treatments/q-switched-laser-toning/': {'title': 'Q-switched laser and laser toning', 'images': [{'id': '16f-1ZiPyPJVAjlhu5aF3eBEjHvEaeker', 'alt': 'Clinic-supplied before-and-after photograph for q-switched laser and laser toning (1 of 4).', 'width': 1200, 'height': 900}, {'id': '1Zwo9Wb61_SZ5uHK59nG9stlX_GmRU0VM', 'alt': 'Clinic-supplied before-and-after photograph for q-switched laser and laser toning (2 of 4).', 'width': 1200, 'height': 900}, {'id': '1CKsbRIca00D-8awoSqvcsdgigZbTEszY', 'alt': 'Clinic-supplied before-and-after photograph for q-switched laser and laser toning (3 of 4).', 'width': 1200, 'height': 900}, {'id': '1LHVoHchx4nfHuqOEX-IZLMSSsPfl0rZs', 'alt': 'Clinic-supplied before-and-after photograph for q-switched laser and laser toning (4 of 4).', 'width': 1200, 'height': 900}]}, '/treatments/mnrf-treatment/': {'title': 'Microneedling radiofrequency treatment', 'images': [{'id': '1XGHuacAWmTKwV2N1a8A6qOzWYqZccF8U', 'alt': 'Clinic-supplied before-and-after photograph for microneedling radiofrequency treatment (1 of 3).', 'width': 1200, 'height': 900}, {'id': '1g8K5CqsYaZqSmkVWhRxlnBtxB8wsSkDH', 'alt': 'Clinic-supplied before-and-after photograph for microneedling radiofrequency treatment (2 of 3).', 'width': 1200, 'height': 900}, {'id': '1UAjp_rkPzElUXOupowe_QDqY9eTGEtxB', 'alt': 'Clinic-supplied before-and-after photograph for microneedling radiofrequency treatment (3 of 3).', 'width': 1200, 'height': 900}]}}
CLINICAL_RESULTS_STYLE = '\n<style>\n.clinical-results {\n  --results-border: color-mix(in srgb, var(--plum, #6e334b) 38%, transparent);\n  --results-panel: color-mix(in srgb, var(--surface, #fff9f7) 94%, #f1dfe6);\n  --results-muted: var(--muted, #64555d);\n  margin: clamp(3rem, 7vw, 5.5rem) auto;\n  padding-inline: max(1rem, env(safe-area-inset-left));\n}\n.clinical-results__inner {\n  width: min(1120px, 100%);\n  margin-inline: auto;\n  padding: clamp(1.1rem, 3vw, 2rem);\n  border: 1px solid var(--results-border);\n  border-radius: clamp(1.25rem, 3vw, 2rem);\n  background: var(--results-panel);\n  box-shadow: 0 18px 48px rgba(74, 35, 52, .08);\n}\n.clinical-results__heading {\n  margin: 0;\n  font-family: var(--font-display, Georgia, serif);\n  font-size: clamp(1.65rem, 4vw, 2.4rem);\n  line-height: 1.1;\n}\n.clinical-results__intro {\n  margin: .65rem 0 1.25rem;\n  color: var(--results-muted);\n  max-width: 68ch;\n}\n.clinical-results__viewport {\n  position: relative;\n  overflow: hidden;\n  border-radius: 1.15rem;\n  background: #efe5e8;\n  border: 1px solid var(--results-border);\n}\n.clinical-results__slide {\n  margin: 0;\n  min-height: min(68vw, 650px);\n  display: grid;\n  place-items: center;\n}\n.clinical-results__slide[hidden] { display: none; }\n.clinical-results__slide img {\n  display: block;\n  width: 100%;\n  height: auto;\n  max-height: 720px;\n  object-fit: contain;\n  background: #efe5e8;\n}\n.clinical-results:not([data-clinical-carousel]) .clinical-results__viewport {\n  max-width: 820px;\n  margin-inline: auto;\n}\n.clinical-results__controls {\n  display: grid;\n  grid-template-columns: minmax(0, 1fr) auto minmax(0, 1fr);\n  align-items: center;\n  gap: .75rem;\n  margin-top: 1rem;\n}\n.clinical-results__button {\n  min-height: 44px;\n  width: fit-content;\n  display: inline-flex;\n  align-items: center;\n  justify-content: center;\n  gap: .45rem;\n  border: 1px solid var(--results-border);\n  border-radius: 999px;\n  padding: .65rem 1rem;\n  background: transparent;\n  color: inherit;\n  font: inherit;\n  font-weight: 700;\n  cursor: pointer;\n}\n.clinical-results__button:last-child { justify-self: end; }\n.clinical-results__button:hover,\n.clinical-results__button:focus-visible {\n  background: var(--accent, #a31f52);\n  color: #fff;\n  outline: none;\n}\n.clinical-results__counter {\n  margin: 0;\n  color: var(--results-muted);\n  font-variant-numeric: tabular-nums;\n  white-space: nowrap;\n}\n.clinical-results__load-error {\n  margin: 1rem 0 0;\n  color: #a31f52;\n  font-weight: 700;\n}\n.clinical-results__note {\n  margin: 1rem 0 0;\n  color: var(--results-muted);\n  font-size: .92rem;\n  line-height: 1.55;\n}\nhtml[data-theme="dark"] .clinical-results {\n  --results-panel: #1b1217;\n  --results-muted: #d3c5cc;\n  --results-border: rgba(232, 157, 189, .28);\n}\nhtml[data-theme="dark"] .clinical-results__viewport,\nhtml[data-theme="dark"] .clinical-results__slide img {\n  background: #120c10;\n}\n@media (max-width: 620px) {\n  .clinical-results__inner { padding: 1rem; }\n  .clinical-results__slide { min-height: 66vw; }\n  .clinical-results__controls { grid-template-columns: 1fr auto 1fr; }\n  .clinical-results__button span:not([aria-hidden="true"]) { display: none; }\n  .clinical-results__button { width: 44px; height: 44px; padding: 0; }\n}\n@media (prefers-reduced-motion: reduce) {\n  .clinical-results *, .clinical-results *::before, .clinical-results *::after {\n    scroll-behavior: auto !important;\n    transition: none !important;\n    animation: none !important;\n  }\n}\n</style>\n'
CLINICAL_RESULTS_SCRIPT = '\n<script>\n(() => {\n  const roots = document.querySelectorAll(\n    \'.clinical-results:not([data-clinical-ready])\'\n  );\n  roots.forEach(root => {\n    root.dataset.clinicalReady = \'true\';\n    const slides = [...root.querySelectorAll(\'[data-clinical-slide]\')];\n    const previous = root.querySelector(\'[data-clinical-previous]\');\n    const next = root.querySelector(\'[data-clinical-next]\');\n    const current = root.querySelector(\'[data-clinical-current]\');\n    const controls = root.querySelector(\'[data-clinical-controls]\');\n    const errorMessage = root.querySelector(\'[data-clinical-error]\');\n    let active = 0;\n    let startX = null;\n\n    const installFallback = image => {\n      if (!image || image.dataset.fallbackReady) return;\n      image.dataset.fallbackReady = \'true\';\n      image.addEventListener(\'error\', () => {\n        if (image.dataset.fallbackSrc && !image.dataset.fallbackUsed) {\n          image.dataset.fallbackUsed = \'true\';\n          image.src = image.dataset.fallbackSrc;\n          return;\n        }\n        if (errorMessage) errorMessage.hidden = false;\n      });\n      if (image.complete && image.naturalWidth === 0) {\n        image.dispatchEvent(new Event(\'error\'));\n      }\n    };\n\n    const load = index => {\n      const image = slides[index]?.querySelector(\'img\');\n      if (!image) return;\n      installFallback(image);\n      if (image.dataset.src && !image.getAttribute(\'src\')) {\n        image.src = image.dataset.src;\n        image.removeAttribute(\'data-src\');\n      }\n    };\n\n    const show = index => {\n      active = (index + slides.length) % slides.length;\n      slides.forEach((slide, slideIndex) => {\n        slide.hidden = slideIndex !== active;\n        slide.setAttribute(\'aria-hidden\', slideIndex === active ? \'false\' : \'true\');\n      });\n      load(active);\n      if (current) current.textContent = String(active + 1);\n    };\n\n    slides.forEach(slide => installFallback(slide.querySelector(\'img\')));\n    if (controls && previous && next && current && slides.length > 1) {\n      controls.hidden = false;\n      previous.addEventListener(\'click\', () => show(active - 1));\n      next.addEventListener(\'click\', () => show(active + 1));\n      root.addEventListener(\'keydown\', event => {\n        if (event.key === \'ArrowLeft\') { event.preventDefault(); show(active - 1); }\n        if (event.key === \'ArrowRight\') { event.preventDefault(); show(active + 1); }\n        if (event.key === \'Home\') { event.preventDefault(); show(0); }\n        if (event.key === \'End\') { event.preventDefault(); show(slides.length - 1); }\n      });\n      root.addEventListener(\'touchstart\', event => {\n        startX = event.changedTouches[0]?.clientX ?? null;\n      }, { passive: true });\n      root.addEventListener(\'touchend\', event => {\n        if (startX === null) return;\n        const endX = event.changedTouches[0]?.clientX ?? startX;\n        const distance = endX - startX;\n        startX = null;\n        if (Math.abs(distance) < 45) return;\n        show(active + (distance < 0 ? 1 : -1));\n      }, { passive: true });\n    }\n    show(0);\n  });\n})();\n</script>\n'


def normalise_path(value: str) -> str:
    path = urlsplit(value or "/").path or "/"
    if not path.startswith("/"):
        path = "/" + path
    if path != "/" and not path.endswith("/"):
        path += "/"
    return path


def drive_thumbnail_url(file_id: str) -> str:
    return (
        "https://drive.google.com/thumbnail?"
        f"id={quote(file_id, safe='')}&sz=w1200"
    )


def drive_fallback_url(file_id: str) -> str:
    return (
        "https://drive.google.com/uc?"
        f"export=view&id={quote(file_id, safe='')}"
    )


def gallery_markup(path: str) -> str:
    gallery = CLINICAL_RESULT_GALLERIES.get(normalise_path(path))
    if not gallery:
        return ""

    images = gallery["images"]
    count = len(images)
    title = escape(gallery["title"])
    gallery_id = "clinical-results-" + normalise_path(path).strip("/").replace("/", "-")
    plural = "photograph" if count == 1 else "photographs"

    figures: list[str] = []
    for index, image in enumerate(images):
        image_url = escape(drive_thumbnail_url(image["id"]), quote=True)
        fallback_url = escape(drive_fallback_url(image["id"]), quote=True)
        alt = escape(image["alt"], quote=True)
        source_attr = (
            f' src="{image_url}"'
            if index == 0
            else f' data-src="{image_url}"'
        )
        hidden_attr = "" if index == 0 else " hidden"
        figures.append(
            f'<figure class="clinical-results__slide" '
            f'data-clinical-slide data-slide-index="{index}"{hidden_attr}>'
            f'<img{source_attr} data-fallback-src="{fallback_url}" alt="{alt}" '
            f'width="{image["width"]}" height="{image["height"]}" '
            f'loading="lazy" decoding="async" referrerpolicy="no-referrer">'
            f'</figure>'
        )

    carousel_attrs = (
        f' data-clinical-carousel tabindex="0" '
        f'aria-roledescription="carousel" aria-label="{title} photographs"'
        if count > 1
        else ""
    )
    controls = ""
    if count > 1:
        controls = (
            '<div class="clinical-results__controls" data-clinical-controls hidden>'
            '<button type="button" class="clinical-results__button" '
            'data-clinical-previous aria-label="Show previous clinical photograph">'
            '<span aria-hidden="true">←</span><span>Previous</span></button>'
            f'<p class="clinical-results__counter" aria-live="polite">'
            f'<span data-clinical-current>1</span> of <span>{count}</span></p>'
            '<button type="button" class="clinical-results__button" '
            'data-clinical-next aria-label="Show next clinical photograph">'
            '<span>Next</span><span aria-hidden="true">→</span></button>'
            '</div>'
        )

    return (
        CLINICAL_RESULTS_STYLE
        + f'<section class="clinical-results" id="{gallery_id}"{carousel_attrs}>'
        + '<div class="clinical-results__inner">'
        + '<header>'
        + '<h2 class="clinical-results__heading">Clinical photographs</h2>'
        + f'<p class="clinical-results__intro">{count} clinic-supplied {plural} '
          f'for {title.lower()}.</p>'
        + '</header>'
        + '<div class="clinical-results__viewport">'
        + "".join(figures)
        + '</div>'
        + controls
        + '<p class="clinical-results__load-error" data-clinical-error hidden>'
          'A clinical photograph could not be loaded. Please try again later.'
          '</p>'
        + '<p class="clinical-results__note">'
          'Individual response, treatment plans and timelines vary. '
          'These photographs are informational and do not guarantee a similar result.'
          '</p>'
        + '</div></section>'
        + CLINICAL_RESULTS_SCRIPT
    )
