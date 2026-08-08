# Aastha Luxury Design System

This document is the public-site design contract for the approved Aastha Skin Centre redesign.

## Brand direction

- Medical credibility first; luxury beauty art direction second.
- Dark theme: blackened espresso / charcoal, oxblood, antique champagne.
- Light theme: warm stone / ivory, oxblood, aged bronze.
- Editorial serif for display headings; restrained system sans-serif for UI and body copy.
- Sharp geometry, hairline borders, very small corner radii, minimal shadows.
- Photography and typography should carry the visual weight. Avoid decorative medical icons, bright hospital blues, generic gradients and excessive cards.

## Page architecture

### Home

- couture header and three-part hero;
- concern catalogue;
- Dr. Cheena editorial brand section;
- alternating/criss-cross selected treatments;
- clinical results / before-after;
- credibility, clinics, FAQ and closing consultation band.

### Treatment and condition pages

- editorial hero;
- five-point proof strip;
- sticky `On this page` rail on wide screens;
- readable central clinical article;
- sticky consultation concierge;
- clinical results and Wagtail comparisons;
- clinics, FAQs and closing CTA.

### Directories

- image-led editorial directory cards;
- sharp ruled grid;
- strong typography and restrained hover movement.

### Standard/blog/doctor/clinic pages

Use the same hero, typography, spacing, Wagtail blocks and interaction rules. New pages inherit the production layer automatically through `data-page-type` on the body.

## Wagtail editing contract

Existing exact-design content remains editable through **Editable page content**.

For new sections use **Pages → Exact-design additions**:

- `Split text and media`: premium image/text section. Choose media left or right. Reveal choreography is automatic.
- `Two-image comparison`: real draggable before/after component. Editors must supply two distinct approved images.
- `Gallery`: treatment/results photography.
- `Image / video carousel`: swipeable media storytelling.
- `FAQ` / `Expandable sections`: semantic animated disclosures.
- `Feature / service grid`: compact evidence/services presentation.
- `Clinics` and `Doctors`: use linked snippets so edits update automatically.

Hero photographs remain page fields. Doctor and clinic reusable photography remains controlled from their snippets. Missing photographs may use the existing fallback until editors upload a real image.

## Clinical image rule

Never fabricate a before/after result from a single composite image. The draggable comparison activates only when two distinct source images are provided. Result notes/disclaimers remain visible.

## Motion rules

Motion should explain hierarchy, not advertise itself.

- medium reveal motion;
- alternating criss-cross entrance on editorial split sections;
- masked image reveals;
- real draggable before/after;
- swipe for galleries/carousels;
- animated semantic accordions;
- sticky clinical navigation and reading progress where appropriate;
- no scroll hijacking, autoplay audio, custom-cursor gimmicks or heavy 3D.

Every motion feature must respect `prefers-reduced-motion` and preserve keyboard/touch access.

## Implementation files

- `home/static/css/premium-production.css` — site-wide final production overlay and Wagtail component styling.
- `home/static/js/premium-production.js` — site-wide clinical navigation, reveals and component enhancement.
- `home/static/css/premium-v5-content-interactions.css` / JS — approved comparison and content interaction behaviour retained during migration from the preview implementation.
- `aastha_cms/templates/base.html` — central loading point and `data-page-type` contract.

The older V3/V4/V5 visual modules remain temporarily underneath the production layer to preserve the approved exact-page appearance during rollout. They should only be removed after a full visual regression capture proves that the production layer reproduces the approved Home/Acne design across representative routes.

## Rollout safety

Do not merge solely because legacy pixel-parity tests fail: those tests compare against the pre-redesign visual baseline. Required rollout checks are structural route integrity, interaction errors, mobile layout, accessibility, Lighthouse and deliberate redesign screenshots.
