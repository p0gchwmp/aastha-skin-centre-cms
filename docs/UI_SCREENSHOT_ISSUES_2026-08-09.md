# Screenshot issue matrix — 2026-08-09

## Sitewide / both desktop and mobile

- Inconsistent panel radius and app-like boxes from overlapping legacy/V5/V6 CSS layers.
- Global heading scale leaking into component headings, especially footer headings.
- Small muted/gold text with insufficient contrast on light surfaces.
- Theme leakage in clinical-result galleries and selected CTA/panel states.
- Broken semantic list glyph rendered as mojibake.
- Excessively large whitespace inside some cards and fact panels.
- Repeated facts/counters creating unnecessary visual density.

## Mobile-specific / narrow viewport

- Clinical reading column can collapse to a few characters per line while a legacy left rail remains visible.
- Ordinary words can break at arbitrary character positions because of `overflow-wrap: anywhere`.
- Homepage fact cards are much taller than their content requires.
- Location illustration blocks consume excessive vertical space.
- Fixed Call / WhatsApp / Book bar can overlap footer and lower-page content.
- Logged-in Wagtail userbar can overlap the Book action.
- Mobile menu mixes large filled pink controls with plain text links and excessive rounded-container styling.
- Header can reserve too much vertical height and does not consistently present brand + menu as one compact bar.
- Directory/category headings are oversized for a 390px viewport.

## Confirmed automated QA failures from V6 main

- Mobile layout audit: 3/76 pages failed because content-index category headings reached 41px on `/about/`, `/conditions/`, and `/treatments/`.
- WCAG audit: 6 desktop-light representative pages failed minimum colour contrast.
- Desktop Lighthouse performance, best-practices and SEO remained excellent; the failed Lighthouse gate was accessibility-driven rather than a performance regression.
