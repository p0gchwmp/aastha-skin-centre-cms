# Aastha website editor guide

This guide covers structural edits that go beyond changing text or replacing one image. The editor is designed so normal future website changes do not require manual CSS, pixel positioning or source-code changes.

## The three editing modes

Every editable page has a **Rendering mode**.

### Exact design + editor additions — recommended for existing pages

The verified production design remains intact. Use **Exact-design additions** to insert new cards, columns, galleries, doctors, clinics, notices, testimonials, FAQs, CTAs and other sections.

Each added section contains **Placement, spacing and responsive layout** controls:

- **Immediately after the hero** — ideal for an announcement, trust strip or featured card.
- **Before/after an existing section anchor** — places content beside a specific existing topic.
- **Before the consultation sidebar / article end** — keeps the addition inside the main article flow.
- **Page end** — places a wide CTA, clinic list or related-content section near the footer.
- Width, theme, text alignment and top/bottom spacing are editor controlled.
- Mobile/desktop visibility can be controlled without custom CSS.

The page editor now displays an **Exact placement map**. It reads the active exact layout, lists the compatible existing sections by their human-readable heading and anchor ID, and fills the Target anchor field when an editor selects one. Editors no longer need to inspect source code or guess an anchor.

Sections dragged within the same placement render in that exact order. If an anchor is later removed, the section is not lost: it safely falls back to the article end and remains visible.

### Full visual page builder

Use this for a new page or when deliberately replacing an existing design. The public page follows the exact drag-and-drop order in **Full page builder**.

The builder supports complete page structures: hero, content, columns, cards, media, notices, processes, testimonials, automatic directories, doctors, clinics, pricing and conversion sections.

### Exact design only

This is a temporary safety mode. Exact HTML remains live and editor additions are hidden. Saved sections are not deleted, so returning to Hybrid mode restores them.

## Adding a card or a new section

1. Open **Pages** and edit the target page.
2. Keep **Exact design + editor additions** for an existing verified page.
3. Open **Exact-design additions** and choose the section type.
4. Complete the content fields.
5. Open **Placement, spacing and responsive layout**.
6. Choose a fixed location or select an existing section from the placement map.
7. Select width, theme, alignment and spacing.
8. Use **Preview** at desktop and mobile widths.
9. Save a draft, request medical review where needed, then publish.

### Designing a card grid

The designable Card grid includes:

- automatic, two-, three- or four-column maximum layouts
- elevated, outlined, soft-tinted and minimal card presets
- landscape, square, portrait or natural image ratios
- optional badges such as “New clinic” or “Popular”
- an optional featured-card emphasis
- equal-height cards
- an optional subtle hover/focus effect

The editor chooses intent rather than dimensions. The website automatically recalculates the final columns, card widths, image crop and stacking behavior.

### Building a flexible multi-column section

Use **Flexible columns** when a section needs two to six independent content areas. Each column can contain an image, eyebrow, heading, formatted text and up to two buttons. Columns can align their content to the top, centre or bottom and stack automatically on smaller screens.

### Adding a notice or alert

Use **Notice / alert** for clinic announcements, medical guidance, important warnings or operational updates. Choose the tone, add formatted content and optional buttons. The front end automatically applies the correct accessible semantic role and responsive presentation.

### Adding testimonials or quotations

Use **Testimonials / quotations** for approved patient experiences, professional quotations or general endorsements. A patient story cannot be saved as valid content unless written consent is explicitly confirmed. Keep the internal consent/source reference in the editor; it is never displayed publicly.

### Adding accreditation or partner logos

Use **Logo / accreditation strip** for memberships, technology partners, associations or accreditations. Add alt text for every logo, an optional label and an optional external link. The grid automatically reflows and can use a quiet monochrome treatment.

## Complete block library

- Hero
- Text section
- Split text and media
- Flexible columns
- Image, video, gallery or carousel
- Two-image comparison with results disclaimer
- Designable card grid
- Feature/service grid
- Statistics/trust indicators
- Process/timeline
- Notice/alert
- Testimonials/quotations with consent control
- Logo/accreditation strip
- FAQ or accordion
- CTA
- Related pages
- Automatic child-page directory
- Automatic or manually selected doctors
- Automatic, primary-only or manually selected clinics
- Pricing
- Reusable section
- Spacer
- Administrator-only advanced HTML escape hatch

## Adding a new clinic

1. Open **Snippets → Clinic locations → Add clinic location**.
2. Enter the address, locality, PIN code, contact details, map links, reception/doctor/procedure hours, directions and image.
3. Set **Primary clinic** according to how it should appear in primary-only lists.
4. Keep **Active** enabled when it should appear publicly.
5. Set the sort order.
6. Keep **Create public page** enabled when a dedicated location page is needed.
7. Leave **Publish automatically** disabled unless the generated page is already complete and approved.
8. Publish the clinic record.

What happens automatically:

- Every Clinic block set to **All active clinics** updates everywhere it is used.
- Primary-only blocks include it only when **Primary clinic** is enabled.
- A linked clinic page is created as a draft when no matching page exists.
- The system reuses a matching unlinked page instead of creating a duplicate.
- The draft appears under the Locations directory when that directory exists.
- The page can remain synchronised with the clinic record for title, introduction and image.
- Responsive clinic grids recalculate themselves; no pixel or column editing is needed.

Deactivating a clinic removes it from automatic lists. It does not silently delete its historical page or URL.

## Adding a new doctor

1. Open **Snippets → Doctors → Add doctor**.
2. Enter verified credentials, role, registration details, biography, interests, photograph and approved booking/contact details.
3. Set **Active** and the display order.
4. Keep **Create public page** enabled when a dedicated profile is needed.
5. Leave automatic page publishing disabled until the profile is medically and professionally reviewed.
6. Publish the doctor record.

What happens automatically:

- Doctor blocks set to **All active doctors** update wherever they are used.
- Manually selected Doctor blocks remain intentionally curated.
- A reviewable draft profile page is created when required.
- A matching unlinked profile page is reused rather than duplicated.
- Linked pages can remain synchronised with the doctor record.
- Published profile URLs remain stable even when the record slug changes.

## Adding a new page, directory or future content family

1. Open **Pages** and select the correct parent page.
2. Choose the appropriate page type.
3. Use **Full visual page builder** for a new design.
4. Add blocks in the exact public order required.
5. Use an **Automatic page directory** when child pages should appear without manual card maintenance.
6. Use internal page choosers for links so they survive future page moves.
7. Preview, review and publish.

A Content index page can list child pages in manual, newest-first or alphabetical order and handles pagination automatically.

## Reusing the same section on several pages

Create a **Reusable section** snippet, build it once, publish it, then add a **Reusable section** block to any page. Editing and publishing the snippet updates every page that references it.

Good uses include:

- standard appointment CTA
- consultation or financing information
- clinic-wide notice
- aftercare disclaimer
- shared doctor or clinic strip
- seasonal campaign
- accreditation strip
- standard trust or safety section

## How the website adjusts automatically

The editor deliberately does not expose manual pixel positioning. Templates handle:

- desktop, tablet and mobile column calculations
- one-column stacking on small screens
- equal card and column heights
- text wrapping and overflow prevention
- image cropping, focal points and lazy loading
- dark mode
- keyboard focus states
- touch-friendly carousel controls
- reduced-motion preferences
- semantic heading, list, notice and quotation structure
- safe fallback placement when an exact-layout anchor disappears

Editors choose semantic intent: width, maximum columns, theme, card preset, media side and placement. The website calculates the final responsive layout.

## Changes that remain intentionally controlled

The editor is broad, but several actions should not happen silently:

- Publishing a generated doctor or clinic page remains a deliberate decision by default.
- Deactivating a doctor or clinic removes it from automatic lists but does not delete pages.
- Replacing an entire exact layout requires switching to Full builder mode.
- Patient stories require consent confirmation.
- Medical claims, statistics, device names and before/after media require verification and approval.
- Advanced HTML is reserved for trusted administrators.

## Safe publishing workflow

1. Save draft.
2. Preview desktop and mobile.
3. Confirm links, alt text, section placement and card order.
4. Confirm consent/source notes for testimonials, statistics and clinical media.
5. Set medical review status and dates for clinical content.
6. Publish or schedule.
7. Use page revisions to compare or roll back.

Internal links should use the page chooser rather than pasted website URLs. They remain valid if a page is moved.
