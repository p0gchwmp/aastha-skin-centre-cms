# Post-PR #80 visual QA checklist

This pass changes layout and interaction only. It does not alter medical claims,
prices, timings, clinical captions or treatment guidance.

1. **Clinical photographs and contents rail**: removed forced gallery heights,
   image padding and dark letterboxing; galleries now use intrinsic image ratios.
   The active contents link is measured inside the rail scroll coordinates, and
   the rail title remains sticky while the complete list advances with the page.
2. **Accordion marker alignment**: summaries use a fixed 26 px marker track with
   the plus/minus centered vertically and horizontally on desktop and mobile.
3. **Section gaps**: consolidated section, article and heading spacing into V10
   rhythm tokens, including the hero-to-section transition.
4. **Rounded article callouts**: deep-dive CTAs, notices, care sidebars and article
   cards use the architectural 2 px geometry.
5. **Small text and inconsistent acne layout**: retired the acne-only V5 grid,
   tiny typography, sidebar and gallery transformations. Acne now uses the same
   shared V8/V10 article system and 16 px body text as other clinical pages.
6. **Clinic care-card alignment**: every service card uses the same 132 px minimum
   height, 24/26 px padding, left alignment, heading scale and body type scale.
7. **Appointment FAQ width**: open answers and their paragraphs/lists use the full
   useful accordion width with consistent inner padding.
8. **iPad layout**: treatment and condition articles collapse to one full reading
   track from 761–1100 px; article and care sidebar both span the track, and the
   tablet header uses one coherent menu pattern. Print remains single-column.
9. **Logo-to-Home gap**: desktop navigation begins immediately after the brand;
   unused flexible space now sits before the appointment CTA.
10. **Mobile theme control**: the theme button is centered in the menu, its label
    is visually hidden without occupying a grid cell, and horizontal menu overflow
    is suppressed at the component level.

## Local acceptance evidence

- 1024 px acne article: one 969 px track, no horizontal overflow.
- 1600 px long article: 39 contents links; deep-scroll active link remains visible
  and advances the rail to `scrollTop 980`.
- Appointment accordions: 70 px summaries, 26 px centered marker, full-width answer.
- Paloura care cards: all six measured at the same 132.9 px row height and 16 px
  description text.
- Mobile viewport: three-line menu control visible; menu overflow contained; theme
  control centered.
