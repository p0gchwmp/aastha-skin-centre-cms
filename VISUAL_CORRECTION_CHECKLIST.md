# Complete visual and interactivity correction checklist

Baseline: production `main` at `5dc7c8f27470f666e0af84b53cb8abb6dc17ebbe` after PR #78.

The 19 supplied screenshots and the full 30-page MNRF PDF are the visual acceptance references. This pass intentionally excludes performance Pass 3 work.

| # | Acceptance item | Implementation | Verification |
|---|---|---|---|
| 1 | Header and navigation | Final header authority gives Home equal breathing room, removes filled styling from About, Conditions, Treatments and Locations, preserves a restrained current state, and normalises the brand, navigation, theme control and appointment action. | Passed desktop alignment and both mobile engines |
| 2 | Icon size | Homepage trust, concern and hub cue slots are larger and responsive. | Passed desktop and 390 px mobile visual checks |
| 3 | Icon quality | Eight recovered vector originals are used directly. Remaining raster originals are served at their native source resolution without generated upscale selection. | Passed asset contract and real-browser image checks |
| 4 | Checkmarks and counters | Checkmark artwork is replaced by editorial diamond or numbered feature treatments. Existing scroll-triggered clinic statistics are restored and remain reduced-motion safe. | Passed scroll and reduced-motion interaction checks |
| 5 | Clinic cards | Address typography, reception-panel padding, grid rows, artwork columns, card heights and action rows are normalised for both branches. | Passed both branches on desktop, Chromium mobile and WebKit mobile |
| 6 | FAQ | Heading gap, full-width rows, marker inset, answer padding and every accordion boundary are standardised. | Passed open, close, animation, border and reduced-motion checks |
| 7 | No em dashes | Visible exact-page text is normalised server-side without touching attributes or structured blocks. Hydrated header/footer text receives the same safe text-node treatment. | Passed 76-page rendered text-node scan |
| 8 | Patient-care principles | Principle type and padding are larger, hover elevation is restrained, and adjacent section rhythm is compacted. | Passed desktop, hover and mobile checks |
| 9 | Global section spacing | Shared spacing tokens now control section padding, heading gaps and article-section rhythm. | Passed representative visual QA and full route sweeps |
| 10 | Explore main areas | The two major areas and child grids use equal tracks, equal rows, common padding, larger headings and consistent icon slots. | Passed equal-track and responsive checks |
| 11 | Gradient CTA | The gradient is preserved; its upper gap and button layout are normalised, and both actions use the same border/background system. | Passed matched button and light/dark theme checks |
| 12 | On this page | Legacy pill and truncated rails are removed. Doctor, treatment, condition, blog and clinic articles receive one complete sticky left rail with active-section tracking plus a compact mobile disclosure. | Passed complete-link and active-scroll checks on all article routes |
| 13 | Doctor features and geometry | Doctor checks are replaced by numbered interactive features. Focus and value cards use the architectural system, larger headings and shared hover interaction. | Passed doctor desktop/mobile and geometry checks |
| 14 | Accordion border and clinic boxes | Every deep-dive and FAQ accordion closes with a full border. Doctor clinic cards use equal architectural geometry and heights. | Passed all-route detail-border and card-radius checks |
| 15 | Accordion inner padding | Summary and expanded content padding are shared across FAQ and deep-dive components. | Passed desktop/mobile accordion checks |
| 16 | CTA and disclaimer alignment | CTA and medical disclaimer widths are locked to the same article track. Where the final CTA is redundant, the aligned disclaimer remains as the deliberate legal note. | Passed shared-track width checks |
| 17 | Repetitive CTA blocks | Redundant final article CTAs are removed from treatment, condition, doctor and clinic pages because those templates already provide hero and sidebar actions. Blog CTAs remain where they add a real next step. | Passed 76-page template sweep |
| 18 | Conditions directory | Group and child-card grids use equal columns, auto rows, common padding, larger headings and shared hover states. | Passed directory desktop/mobile and equal-height checks |
| 19 | Shared articles and MNRF | One shared article grid covers treatment, condition, blog, doctor and clinic content. All tracks use `min-width: 0`; list, deep-dive, sidebar, photograph and caption widths are bounded; responsive and print layouts collapse deliberately; complete TOCs are generated; generic clinical proof strips are removed. | Passed 76-page desktop, Chromium and WebKit sweeps; MNRF print is 29 pages with zero blank pages |
| 20 | Location pages | Notices span the article track, middle cards use architectural geometry, and first-visit checks become numbered interactive cards. | Passed both clinic pages on desktop and both mobile engines |

## Final local verification

- 168 Django tests passed.
- 40 targeted visual, exact-page and asset contract tests passed after the final interaction fix.
- 75 exact-page snapshots verified with all landmarks, routes and assets intact.
- 76 of 76 desktop routes passed the visual-system sweep.
- 76 of 76 routes passed at 390 px in Chromium.
- 76 of 76 routes passed at 390 px in iPhone WebKit.
- The regenerated MNRF print has 29 content-bearing pages and zero blank pages.

## Recovered original vector cues

- Acne care
- Pigmentation care
- Hair and scalp care
- Dermatologist-led diagnosis
- Medical experience
- Two clinic locations
- Complete care
- Personalised plan

## Full-size clay originals not recovered

These are kept at or below the native source dimensions. They are not enlarged into false high-resolution assets and remain candidates for later generation.

- Advanced laser care: 256 x 256 raster source
- Clinical skin care: 128 x 128 sprite source
- Allergy and inflammatory rashes: 128 x 128 raster source
- Moles, growths and nails: 128 x 128 raster source
- Scars, texture and skin quality: 128 x 128 raster source
- Children's dermatology: 128 x 128 raster source
- Minor dermatosurgery: 128 x 128 raster source
- Skin quality and ageing: 128 x 128 raster source
- Fungal infection care: 192 x 192 raster source
