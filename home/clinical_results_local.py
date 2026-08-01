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
    CLINICAL_RESULTS_SCRIPT,
    CLINICAL_RESULTS_STYLE,
    normalise_path,
)


HERO_GALLERY_STYLE = r"""
<style>
.clinical-results--hero {
  margin: 0 !important;
  padding: 0 !important;
  width: 100%;
}
.clinical-results--hero .clinical-results__inner {
  width: 100%;
  padding: 0;
  border: 0;
  border-radius: inherit;
  background: transparent;
  box-shadow: none;
}
.clinical-results--hero header,
.clinical-results--hero .clinical-results__note {
  display: none;
}
.clinical-results--hero .clinical-results__viewport {
  border-radius: inherit;
}
.clinical-results--hero .clinical-results__slide {
  min-height: 0;
  aspect-ratio: 4 / 3;
}
.clinical-results--hero .clinical-results__slide img {
  width: 100%;
  height: 100%;
  object-fit: contain;
}
.clinical-results--hero .clinical-results__controls {
  margin-top: .75rem;
}
.clinical-results__replaced-placeholder {
  display: none !important;
}
.clinical-results__load-error[hidden],
.clinical-results__load-error[data-suppressed="true"] {
  display: none !important;
}
</style>
"""


HERO_GALLERY_SCRIPT = r"""
<script>
(() => {
  const placeGalleryInHero = root => {
    if (root.dataset.heroPlaced === 'true') return;
    const main = root.closest('main') || document.querySelector('main');
    const heading = main?.querySelector('h1');
    const hero = heading?.closest('section');
    if (!hero) return;

    const visual = [...hero.querySelectorAll('div, figure')].find(node =>
      !node.contains(heading) && node.querySelector('img, svg, picture')
    );
    if (!visual || !visual.parentNode) return;

    visual.classList.add('clinical-results__replaced-placeholder');
    visual.parentNode.insertBefore(root, visual);
    root.classList.add('clinical-results--hero');
    root.dataset.heroPlaced = 'true';
  };

  const reconcileErrors = root => {
    const error = root.querySelector('[data-clinical-error]');
    if (!error) return;
    const loadedOrLoadingImages = [
      ...root.querySelectorAll('[data-clinical-slide] img[src]')
    ];
    const failed = loadedOrLoadingImages.some(
      image => image.complete && image.naturalWidth === 0
    );
    error.hidden = !failed;
    error.dataset.suppressed = failed ? 'false' : 'true';
    error.style.display = failed ? '' : 'none';
  };

  const initialise = () => {
    document.querySelectorAll('.clinical-results').forEach(root => {
      placeGalleryInHero(root);
      const images = [...root.querySelectorAll('[data-clinical-slide] img')];
      images.forEach(image => {
        image.addEventListener('load', () => reconcileErrors(root));
        image.addEventListener('error', () => reconcileErrors(root));
      });
      reconcileErrors(root);
      requestAnimationFrame(() => reconcileErrors(root));
      setTimeout(() => reconcileErrors(root), 500);
    });
  };

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initialise, {once: true});
  } else {
    initialise();
  }
})();
</script>
"""


def local_asset_path(path: str, index: int) -> str:
    """Return the deterministic static path for one route/image placement."""
    slug = normalise_path(path).strip("/").split("/")[-1]
    return f"images/clinical-results/{slug}/{slug}-{index:02d}.webp"


def gallery_markup(path: str) -> str:
    """Render one static image or a carousel using local WebP assets only."""
    normalised = normalise_path(path)
    gallery = CLINICAL_RESULT_GALLERIES.get(normalised)
    if not gallery:
        return ""

    images = gallery["images"]
    count = len(images)
    title = escape(gallery["title"])
    gallery_id = "clinical-results-" + normalised.strip("/").replace("/", "-")
    plural = "photograph" if count == 1 else "photographs"

    figures: list[str] = []
    for index, image in enumerate(images, start=1):
        image_url = escape(static(local_asset_path(normalised, index)), quote=True)
        alt = escape(image["alt"], quote=True)
        source_attr = (
            f' src="{image_url}"'
            if index == 1
            else f' data-src="{image_url}"'
        )
        hidden_attr = "" if index == 1 else " hidden"
        figures.append(
            f'<figure class="clinical-results__slide" '
            f'data-clinical-slide data-slide-index="{index - 1}"{hidden_attr}>'
            f'<img{source_attr} alt="{alt}" '
            f'width="{image["width"]}" height="{image["height"]}" '
            f'loading="lazy" decoding="async">'
            '</figure>'
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
            '<p class="clinical-results__counter" aria-live="polite">'
            f'<span data-clinical-current>1</span> of <span>{count}</span></p>'
            '<button type="button" class="clinical-results__button" '
            'data-clinical-next aria-label="Show next clinical photograph">'
            '<span>Next</span><span aria-hidden="true">→</span></button>'
            '</div>'
        )

    return (
        CLINICAL_RESULTS_STYLE
        + HERO_GALLERY_STYLE
        + f'<section class="clinical-results" id="{gallery_id}"{carousel_attrs}>'
        + '<div class="clinical-results__inner">'
        + '<header>'
        + '<h2 class="clinical-results__heading">Clinical photographs</h2>'
        + f'<p class="clinical-results__intro">{count} clinic-supplied {plural} '
          f'for {title.lower()}.</p>'
        + '</header>'
        + '<div class="clinical-results__viewport">'
        + ''.join(figures)
        + '</div>'
        + controls
        + '<p class="clinical-results__load-error" data-clinical-error '
          'data-suppressed="true" hidden style="display:none">'
          'A clinical photograph could not be loaded. Please try again later.'
          '</p>'
        + '<p class="clinical-results__note">'
          'Individual response, treatment plans and timelines vary. '
          'These photographs are informational and do not guarantee a similar result.'
          '</p>'
        + '</div></section>'
        + CLINICAL_RESULTS_SCRIPT
        + HERO_GALLERY_SCRIPT
    )
