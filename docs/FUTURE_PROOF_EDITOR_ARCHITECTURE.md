# Future-proof editor architecture

## Objective

The CMS must support future structural editing without requiring source-code changes for normal clinic operations. Editors should be able to add, reorder, reuse and retire sections, doctors, clinics, cards and directories while the public website remains responsive, accessible and SEO-safe.

## Editing model

### 1. Page tree controls URLs and hierarchy

Wagtail Pages remain the source of truth for public routes. Moving a page changes its location deliberately and Wagtail-managed internal links remain valid. New doctor and clinic snippets do not silently create public URLs.

### 2. StreamField controls exact section order

Each flexible page has an ordered body. A section renders exactly where it appears in the editor. Editors drag sections to reorder them and use layout settings for width, theme, alignment, spacing, visibility and anchors.

### 3. Snippets control reusable entities

Doctors, clinic locations, reusable sections and future collections are edited once and referenced in multiple pages. Dynamic listing blocks may select all eligible records or a curated manual subset.

### 4. Responsive behavior is automatic by default

Templates own the responsive grid rules. Editors choose semantic intent such as two, three or four columns; the site automatically reduces columns on tablets and stacks content on small screens. Manual pixel positioning is not exposed.

### 5. Exact-layout compatibility is explicit

Legacy exact-layout snapshots preserve parity but can mask the visual page builder. The editor must clearly show when a snapshot is active and provide a controlled switch to the structured builder. New pages should use structured blocks by default.

## Required block library

- Hero and split hero
- Rich text and image/text split
- General columns
- Manual and reusable card grids
- Steps / timeline
- Statistics / trust indicators
- Testimonials / quotations
- Notice / alert / announcement
- FAQ and accordion
- Image and video galleries / carousels
- Pricing
- Related pages
- Dynamic doctors and clinics
- Reusable section insertion
- Spacer and administrator-only HTML escape hatch

## Dynamic entity behavior

### Doctors

A doctor listing block supports:

- all active, published doctors
- selected doctors in manual order
- optional role or interest filtering
- configurable columns and card detail level

A Doctor Page explicitly links to one Doctor snippet. Creating a snippet does not create a public page automatically. This prevents accidental duplicate URLs and incomplete profiles.

### Clinics

A clinic listing block supports:

- all active, published clinics
- primary clinics only
- selected clinics in manual order
- configurable card detail level

A Clinic Page explicitly links to one ClinicLocation snippet. Navigation and homepage placement use dynamic listing blocks or deliberate page links.

## Safety and governance

- Preview before publishing
- Draft, scheduled publishing, revisions and rollback
- Medical review status and review dates
- No raw patient data in analytics
- Internal page choosers instead of pasted internal URLs
- Alt text and heading guidance
- Block validation and maximum sensible item counts
- Automated desktop, mobile, dark-mode, accessibility and route QA

## Rollout order

1. Make dynamic doctor and clinic listings automatic or curated.
2. Add general columns, steps, statistics, testimonials and notices.
3. Add reusable card collections and section presets.
4. Add visible exact-layout status and safe builder conversion controls.
5. Add editor documentation and scenario-based tests.
6. Add optional guided creation flows for doctor and clinic profile pages.
