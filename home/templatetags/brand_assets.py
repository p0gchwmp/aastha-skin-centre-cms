"""Template helpers for globally configured brand images."""

from __future__ import annotations

from django import template

register = template.Library()


EMPTY_ASSET = {"url": "", "width": 0, "height": 0}


def _asset(image, rendition_spec: str) -> dict[str, object]:
    """Return a browser-ready rendition while tolerating legacy image files."""

    if not image:
        return EMPTY_ASSET.copy()

    try:
        rendition = image.get_rendition(rendition_spec)
        return {
            "url": rendition.url,
            "width": rendition.width,
            "height": rendition.height,
        }
    except (OSError, ValueError):
        # A previously uploaded SVG or unusual legacy file may not support the
        # requested raster operation. Showing the original is safer than
        # silently reverting to the placeholder brand mark.
        return {
            "url": image.file.url,
            "width": getattr(image, "width", 0) or 0,
            "height": getattr(image, "height", 0) or 0,
        }


@register.simple_tag
def global_brand_assets(site_settings):
    """Resolve responsive logo renditions and the selected favicon."""

    if not site_settings:
        return {
            "logo": EMPTY_ASSET.copy(),
            "logo_large": EMPTY_ASSET.copy(),
            "favicon": EMPTY_ASSET.copy(),
        }

    return {
        # The logo occupies at most ~150 CSS pixels. A 160px candidate serves
        # standard-density displays while 320px covers high-density screens.
        "logo": _asset(site_settings.logo, "max-160x54|format-webp"),
        "logo_large": _asset(
            site_settings.logo,
            "max-320x108|format-webp",
        ),
        "favicon": _asset(site_settings.favicon, "fill-64x64"),
    }
