# Aastha Premium Design System V4

> Status: **approved art direction / preview only**. Do not merge or deploy until the clinic owner approves the rendered light and dark previews.

## Brand direction

Aastha should feel like a high-end dermatology house rather than a generic clinic template: editorial, exact, calm and medically credible. Luxury comes from proportion, typography, photography, restraint and service—not from decorative gold effects.

### Final palette

#### Dark — primary luxury expression
- Background: `#100f0e` blackened espresso
- Paper: `#141311`
- Surface: `#1b1917`
- Primary text: `#f4ede3`
- Muted text: `#a99d92`
- Oxblood: `#7b203c`
- Deep oxblood: `#941f49`
- Antique champagne: `#c3a16b`
- Soft champagne: `#ddc796`

#### Light — clinical luxury expression
- Background: `#eee8dd` warm stone
- Paper: `#f8f4ec`
- Surface: `#fffaf3`
- Primary text: `#151311`
- Muted text: `#746a62`
- Oxblood: `#702433`
- Deep oxblood: `#531827`
- Aged bronze: `#9d7658`
- Soft bronze: `#c8ad91`

## Typography

- Display / editorial: Iowan Old Style → Baskerville → Palatino → Georgia fallback chain.
- UI / body: Inter → system UI stack.
- Headings are large, close-set and low-weight.
- UI labels are small, uppercase and letter-spaced.
- Do not add more font families without a measured performance and licensing review.

## Geometry

- Default corner radius: `0–2px`.
- Circular controls are reserved for arrows, comparison handles and theme controls.
- Hairline rules replace most cards and shadows.
- Photography may use a 0px radius to reinforce editorial art direction.

## Motion

Level: **Medium**.

Use:
- 300–750ms reveal choreography;
- 1–2% image crop shifts on hover;
- treatment carousel snap motion;
- header compression after initial scroll;
- disclosure content fade on native `<details>`;
- progress rail on long clinical pages;
- clinical gallery touch swiping;
- before/after comparison only when two distinct media assets are supplied.

Never use:
- scroll-jacking;
- autoplay audio/video;
- custom cursors;
- constant parallax;
- fake counters;
- animated gradients as decoration;
- motion that ignores `prefers-reduced-motion`.

## Photography rules

1. Real clinic/doctor photography is preferred over illustrations.
2. Dr. Cheena Langer must always use an actual uploaded photograph, never an AI recreation.
3. Missing media must fall back gracefully and remain editable in Wagtail.
4. Hero photography: portrait crop, eyes/face kept clear of overlay UI.
5. Treatment photography: editorial crop, no generic stock-doctor imagery.
6. Clinical result images retain factual captions and outcome disclaimers.

## Required Wagtail editability before production

Every media-bearing final component must expose a Wagtail chooser and alt text where applicable.

### Homepage
- Hero photograph
- Doctor spotlight photograph
- Concern icons/optional photography
- Selected treatment image per item
- Clinic image per branch
- Optional closing CTA image

### Treatment / condition pages
- Hero image
- Inline clinical/treatment image blocks
- Treatment technology image
- Clinic images
- Related-treatment images

### Before/after results
Production component must store **two distinct image fields**:
- `before_image`
- `after_image`

Plus:
- treatment/condition relation or route assignment
- accessible alt text for each image
- optional result caption
- sort order
- consent/approval status if the clinic later chooses to record it
- patient-facing disclaimer remains mandatory

Do not generate a comparison slider from one combined image. Existing combined clinical photographs remain gallery media until explicitly split/approved by the clinic.

## Interaction components

### Before/after comparator
- pointer, touch and keyboard range input
- visible handle
- clear Before / After labels
- no automatic movement
- `aria-valuetext`
- reduced-motion compatible

### Selected treatments carousel
- horizontal snap on mobile
- previous/next controls
- progress indicator
- drag/swipe support from native scrolling
- no infinite loop

### Long-page reading rail
- generated from H2 headings
- highlights active section
- desktop only
- hidden when page has fewer than four sections

### Consultation concierge
Production version should use existing Wagtail/global contact settings and avoid duplicated hard-coded phone numbers. Desktop may use a sticky sidebar. Mobile should reuse/replace the existing mobile action bar rather than adding a second competing bar.

## Accessibility / performance gates

Before merge:
- WCAG 2.2 A/AA automated audit: zero blocking violations
- Lighthouse Accessibility / Best Practices / SEO: 100 target on representative pages
- Performance: >=95 mobile and desktop representative routes
- CLS: <=0.05 target
- LCP: <=2.5s target on mobile lab profile
- dark and light mobile audits in Chromium and WebKit
- keyboard navigation for comparison slider, carousel controls, accordions and header menus

## Production sequence

1. Approve final V4 rendered previews in both themes.
2. Convert preview-only CSS/JS into production files and remove obsolete preview layers.
3. Add missing Wagtail media/result fields and migrations.
4. Connect real production media without overwriting editor choices.
5. QA preview deployment/staging.
6. Merge only after clinic owner approval.
7. Render production deployment and post-deploy smoke/accessibility/performance checks.
