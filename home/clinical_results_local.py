"""Production renderer for locally materialised clinical-result photographs.

The approved source mapping remains in :mod:`home.clinical_results` for
provenance and for the explicit maintenance importer. Public pages use only
versioned static WebP files committed to this private repository; visitors do
not make Google Drive requests.
"""

from __future__ import annotations

from html import escape

from django.templatetags.static import static

from home.clinical_results import (
    CLINICAL_RESULT_GALLERIES,
    CLINICAL_RESULTS_STYLE,
    normalise_path,
)


RESPONSIVE_WIDTHS = (384, 640, 768)
ORIGINAL_MAX_WIDTH = 1200
HERO_IMAGE_SIZES = (
    "(max-width: 760px) calc(100vw - 48px), "
    "(max-width: 980px) calc(100vw - 72px), 382px"
)
SECTION_IMAGE_SIZES = (
    "(max-width: 760px) calc(100vw - 48px), "
    "(max-width: 1200px) calc(100vw - 72px), 1056px"
)


CLINICAL_RESULTS_LOCAL_STYLE = r"""
<style>
.clinical-results__load-error[hidden],
.clinical-results__controls[hidden] {
  display: none !important;
}

.page-hero-art:has(> .clinical-results--hero) > img {
  display: none !important;
}

.page-hero-art:has(> .clinical-results--hero) {
  padding: clamp(.65rem, 1.5vw, 1rem);
  align-items: stretch;
}

.page-hero-art > .clinical-results--hero {
  width: 100%;
  max-width: none;
  margin: 0;
  padding: 0;
}

.clinical-results--hero .clinical-results__inner {
  width: 100%;
  margin: 0;
  padding: 0;
  border: 0;
  border-radius: 0;
  background: transparent;
  box-shadow: none;
}

.clinical-results--hero .clinical-results__hero-label {
  margin: 0 0 .55rem;
  color: var(--plum, #7b1e3a);
  font-size: .76rem;
  font-weight: 800;
  letter-spacing: .08em;
  text-transform: uppercase;
}

.clinical-results--hero .clinical-results__viewport {
  width: 100%;
  aspect-ratio: 4 / 3;
  border-radius: clamp(.9rem, 2vw, 1.25rem);
}

.clinical-results--hero .clinical-results__slide {
  width: 100%;
  min-height: 0;
  height: 100%;
  aspect-ratio: 4 / 3;
}

.clinical-results--hero .clinical-results__slide img {
  width: 100%;
  height: 100%;
  max-height: none;
  object-fit: contain;
  background: #efe5e8;
}

.clinical-results--hero .clinical-results__controls {
  display: grid;
  grid-template-columns: 44px 1fr 44px;
  align-items: center;
  gap: .55rem;
  margin-top: .6rem;
}

.clinical-results--hero .clinical-results__button {
  width: 44px;
  min-width: 44px;
  min-height: 44px;
  padding: 0;
  border-radius: 999px;
}

.clinical-results--hero .clinical-results__counter {
  margin: 0;
  text-align: center;
  font-size: .86rem;
  font-weight: 750;
}

.clinical-results--hero .clinical-results__load-error {
  margin: .6rem 0 0;
  font-size: .82rem;
}

.clinical-results--hero .clinical-results__note {
  margin: .55rem 0 0;
  font-size: .76rem;
  line-height: 1.45;
}

@media (max-width: 760px) {
  .page-hero-art:has(> .clinical-results--hero) {
    padding: .65rem;
  }

  .clinical-results--hero .clinical-results__viewport,
  .clinical-results--hero .clinical-results__slide {
    aspect-ratio: 4 / 3;
  }
}
</style>
"""


CLINICAL_RESULTS_LOCAL_SCRIPT = r"""
<script>
(() => {
  const roots = document.querySelectorAll(
    '.clinical-results:not([data-clinical-ready])'
  );

  roots.forEach(root => {
    root.dataset.clinicalReady = 'true';

    const slides = [...root.querySelectorAll('[data-clinical-slide]')];
    const previous = root.querySelector('[data-clinical-previous]');
    const nextButton = root.querySelector('[data-clinical-next]');
    const current = root.querySelector('[data-clinical-current]');
    const controls = root.querySelector('[data-clinical-controls]');
    const errorMessage = root.querySelector('[data-clinical-error]');

    if (!slides.length) return;

    let active = 0;
    let startX = null;

    const activeImage = () => slides[active]?.querySelector('img');

    const syncError = () => {
      if (!errorMessage) return;
      const image = activeImage();
      errorMessage.hidden = !(
        image && image.dataset.clinicalLoadFailed === 'true'
      );
    };

    const bindImage = image => {
      if (!image || image.dataset.clinicalBound === 'true') return;
      image.dataset.clinicalBound = 'true';

      image.addEventListener('load', () => {
        delete image.dataset.clinicalLoadFailed;
        syncError();
      });

      image.addEventListener('error', () => {
        image.dataset.clinicalLoadFailed = 'true';
        syncError();
      });

      const source = image.getAttribute('src');
      if (
        source &&
        image.hasAttribute('src') &&
        image.complete &&
        image.naturalWidth === 0
      ) {
        image.dataset.clinicalLoadFailed = 'true';
      }
    };

    const loadSlide = slide => {
      const image = slide?.querySelector('img');
      if (!image) return;
      bindImage(image);
      if (image.dataset.sizes) {
        image.sizes = image.dataset.sizes;
        image.removeAttribute('data-sizes');
      }
      if (image.dataset.srcset) {
        image.srcset = image.dataset.srcset;
        image.removeAttribute('data-srcset');
      }
      if (image.dataset.src) {
        image.src = image.dataset.src;
        image.removeAttribute('data-src');
      }
    };

    const show = index => {
      active = (index + slides.length) % slides.length;
      slides.forEach((slide, slideIndex) => {
        const selected = slideIndex === active;
        slide.hidden = !selected;
        slide.setAttribute('aria-hidden', selected ? 'false' : 'true');
      });
      loadSlide(slides[active]);
      if (current) current.textContent = String(active + 1);
      syncError();
    };

    slides.forEach(slide => bindImage(slide.querySelector('img')));

    if (controls && slides.length > 1) {
      controls.hidden = false;
    }

    previous?.addEventListener('click', () => show(active - 1));
    nextButton?.addEventListener('click', () => show(active + 1));

    root.addEventListener('keydown', event => {
      if (slides.length < 2) return;
      if (event.key === 'ArrowLeft') {
        event.preventDefault();
        show(active - 1);
      } else if (event.key === 'ArrowRight') {
        event.preventDefault();
        show(active + 1);
      } else if (event.key === 'Home') {
        event.preventDefault();
        show(0);
      } else if (event.key === 'End') {
        event.preventDefault();
        show(slides.length - 1);
      }
    });

    root.addEventListener('touchstart', event => {
      startX = event.changedTouches[0]?.clientX ?? null;
    }, {passive: true});

    root.addEventListener('touchend', event => {
      if (startX === null || slides.length < 2) return;
      const endX = event.changedTouches[0]?.clientX ?? startX;
      const distance = endX - startX;
      startX = null;
      if (Math.abs(distance) < 45) return;
      show(distance < 0 ? active + 1 : active - 1);
    }, {passive: true});

    show(0);
  });
})();
</script>
"""


def local_asset_path(path: str, index: int) -> str:
    """Return the deterministic static path for one route/image placement."""
    slug = normalise_path(path).strip("/").split("/")[-1]
    return f"images/clinical-results/{slug}/{slug}-{index:02d}.webp"


def responsive_asset_path(path: str, index: int, width: int) -> str:
    """Return one build-generated responsive candidate path."""
    original = local_asset_path(path, index)
    if width == ORIGINAL_MAX_WIDTH:
        return original
    return original.removesuffix(".webp") + f"-{width}w.webp"


def _responsive_srcset(path: str, index: int) -> str:
    widths = (*RESPONSIVE_WIDTHS, ORIGINAL_MAX_WIDTH)
    return ", ".join(
        f"{static(responsive_asset_path(path, index, width))} {width}w"
        for width in widths
    )


def _local_dimensions(image: dict) -> tuple[int, int]:
    width = int(image["width"])
    height = int(image["height"])
    longest = max(width, height)
    if longest <= ORIGINAL_MAX_WIDTH:
        return width, height
    scale = ORIGINAL_MAX_WIDTH / longest
    return max(1, round(width * scale)), max(1, round(height * scale))


def _figure_markup(
    normalised: str,
    images: list[dict],
    *,
    hero: bool,
) -> str:
    figures: list[str] = []
    sizes = HERO_IMAGE_SIZES if hero else SECTION_IMAGE_SIZES
    escaped_sizes = escape(sizes, quote=True)

    for index, image in enumerate(images, start=1):
        image_url = escape(static(local_asset_path(normalised, index)), quote=True)
        srcset = escape(_responsive_srcset(normalised, index), quote=True)
        alt = escape(image["alt"], quote=True)
        width, height = _local_dimensions(image)
        source_attr = (
            f' src="{image_url}" srcset="{srcset}" sizes="{escaped_sizes}"'
            if index == 1
            else (
                f' data-src="{image_url}" data-srcset="{srcset}" '
                f'data-sizes="{escaped_sizes}"'
            )
        )
        hidden_attr = "" if index == 1 else " hidden"
        loading = (
            'loading="eager" decoding="async" fetchpriority="high"'
            if hero and index == 1
            else 'loading="lazy" decoding="async"'
        )
        figures.append(
            f'<figure class="clinical-results__slide" '
            f'data-clinical-slide data-slide-index="{index - 1}"{hidden_attr}>'
            f'<img{source_attr} alt="{alt}" '
            f'width="{width}" height="{height}" '
            f'{loading}>'
            "</figure>"
        )
    return "".join(figures)


def _carousel_attributes(title: str, count: int) -> str:
    if count <= 1:
        return ""
    return (
        ' data-clinical-carousel tabindex="0" '
        f'aria-roledescription="carousel" aria-label="{title} photographs"'
    )


def _controls(count: int, *, compact: bool) -> str:
    if count <= 1:
        return ""
    if compact:
        previous_content = '<span aria-hidden="true">←</span>'
        next_content = '<span aria-hidden="true">→</span>'
    else:
        previous_content = (
            '<span aria-hidden="true">←</span><span>Previous</span>'
        )
        next_content = '<span>Next</span><span aria-hidden="true">→</span>'

    return (
        '<div class="clinical-results__controls" data-clinical-controls hidden>'
        '<button type="button" class="clinical-results__button" '
        'data-clinical-previous aria-label="Show previous clinical photograph">'
        f"{previous_content}</button>"
        '<p class="clinical-results__counter" aria-live="polite">'
        f'<span data-clinical-current>1</span> of <span>{count}</span></p>'
        '<button type="button" class="clinical-results__button" '
        'data-clinical-next aria-label="Show next clinical photograph">'
        f"{next_content}</button>"
        "</div>"
    )


def _error_markup() -> str:
    return (
        '<p class="clinical-results__load-error" data-clinical-error hidden>'
        "A clinical photograph could not be loaded. Please try again later."
        "</p>"
    )


def gallery_markup(path: str) -> str:
    """Render the full in-content gallery used by Wagtail fallback pages."""
    normalised = normalise_path(path)
    gallery = CLINICAL_RESULT_GALLERIES.get(normalised)
    if not gallery:
        return ""

    images = gallery["images"]
    count = len(images)
    title = escape(gallery["title"])
    gallery_id = "clinical-results-" + normalised.strip("/").replace("/", "-")
    plural = "photograph" if count == 1 else "photographs"

    return (
        CLINICAL_RESULTS_STYLE
        + CLINICAL_RESULTS_LOCAL_STYLE
        + f'<section class="clinical-results clinical-results--section" '
        f'id="{gallery_id}" data-clinical-root'
        + _carousel_attributes(title, count)
        + ">"
        + '<div class="clinical-results__inner">'
        + "<header>"
        + '<h2 class="clinical-results__heading">Clinical photographs</h2>'
        + f'<p class="clinical-results__intro">{count} clinic-supplied {plural} '
          f"for {title.lower()}.</p>"
        + "</header>"
        + '<div class="clinical-results__viewport">'
        + _figure_markup(normalised, images, hero=False)
        + "</div>"
        + _controls(count, compact=False)
        + _error_markup()
        + '<p class="clinical-results__note">'
          "Individual response, treatment plans and timelines vary. "
          "These photographs are informational and do not guarantee a similar result."
          "</p>"
        + "</div></section>"
        + CLINICAL_RESULTS_LOCAL_SCRIPT
    )


def hero_gallery_markup(path: str) -> str:
    """Render clinical photographs inside the existing page-hero art card."""
    normalised = normalise_path(path)
    gallery = CLINICAL_RESULT_GALLERIES.get(normalised)
    if not gallery:
        return ""

    images = gallery["images"]
    count = len(images)
    title = escape(gallery["title"])
    gallery_id = (
        "clinical-results-hero-"
        + normalised.strip("/").replace("/", "-")
    )

    return (
        CLINICAL_RESULTS_STYLE
        + CLINICAL_RESULTS_LOCAL_STYLE
        + f'<section class="clinical-results clinical-results--hero" '
        f'id="{gallery_id}" data-clinical-root'
        + _carousel_attributes(title, count)
        + ">"
        + '<div class="clinical-results__inner">'
        + '<p class="clinical-results__hero-label">Clinical photographs</p>'
        + '<div class="clinical-results__viewport">'
        + _figure_markup(normalised, images, hero=True)
        + "</div>"
        + _controls(count, compact=True)
        + _error_markup()
        + '<p class="clinical-results__note">'
          "Clinic-supplied photographs. Individual results vary."
          "</p>"
        + "</div></section>"
        + CLINICAL_RESULTS_LOCAL_SCRIPT
    )
