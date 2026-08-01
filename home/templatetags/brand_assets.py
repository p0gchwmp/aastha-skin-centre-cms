"""Template helpers for globally configured brand images."""

from __future__ import annotations

from django import template

register = template.Library()


def _asset(image, rendition_spec: str) -> dict[str, object]:
    """Return a browser-ready rendition while tolerating legacy image files."""

    if not image:
        return {"url": "", "width": 0, "height": 0}

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
    """Resolve the current logo and favicon selected in Wagtail Settings."""

    if not site_settings:
        return {
            "logo": {"url": "", "width": 0, "height": 0},
            "favicon": {"url": "", "width": 0, "height": 0},
        }

    return {
        "logo": _asset(site_settings.logo, "max-480x160"),
        "favicon": _asset(site_settings.favicon, "fill-64x64"),
    }
