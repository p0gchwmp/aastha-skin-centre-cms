# Aastha website editor guide

This guide covers structural edits that go beyond changing text or replacing one image.

## The three editing modes

Every editable page has a **Rendering mode**.

### Exact design + editor additions — recommended for existing pages

The verified production design remains intact. Use **Exact-design additions** to insert new cards, galleries, doctors, clinics, FAQs, CTAs and other sections.

Each added section contains **Placement, spacing and responsive layout** controls:

- **Immediately after the hero** — ideal for a notice, trust strip or featured card.
- **Before/after an existing section anchor** — places content beside a specific existing topic.
- **Before the consultation sidebar / article end** — keeps the addition inside the main article flow.
- **Page end** — places a wide CTA, clinic list or related-content section near the footer.
- Width, theme, alignment and spacing are automatic and responsive.
- Mobile/desktop visibility can be controlled without custom CSS.

Sections dragged within the same placement render in that exact order. If an anchor is later removed, the section is not lost: it safely falls back to the article end.

### Full visual page builder

Use this for a new page or when deliberately replacing an existing design. The public page follows the exact drag-and-drop order in **Full page builder**.

### Exact design only

This is a temporary safety mode. Exact HTML remains live and editor additions are hidden. Saved sections are not deleted.

## Adding a card or a new section

1. Open **Pages** and edit the target page.
2. Keep **Exact design + editor additions** for an existing verified page.
3. Open **Exact-design additions** and choose the section type.
4. Complete the content fields.
5. Open **Placement, spacing and responsive layout**.
6. Choose where the section belongs and select its width/theme.
7. Use **Preview** at desktop and mobile widths.
8. Save a draft, request medical review where needed, then publish.

Recommended blocks include:

- Text section
- Split text and media
- Image, video, gallery or carousel
- Card grid
- Feature/service grid
- Statistics/trust indicators
- Process/timeline
- Two-image comparison with results disclaimer
- FAQ or accordion
- CTA
- Related pages or an automatic child-page directory
- Automatic doctors or clinics
- Pricing
- Reusable section

## Adding a new clinic

1. Open **Snippets → Clinic locations → Add clinic location**.
2. Enter its address, contact details, map link, hours and image.
3. Keep **Create public page** enabled when a dedicated location page is needed.
4. Leave **Publish automatically** disabled unless the page is complete and approved.
5. Publish the clinic record.

What happens automatically:

- Any clinic block set to **All active clinics** updates everywhere it is used.
- Primary-only blocks include it only when **Primary clinic** is enabled.
- A linked clinic page is created as a draft when no page exists.
- The draft appears under the Locations directory when available.
- Responsive clinic grids recalculate themselves; no pixel or column editing is needed.

Deactivating a clinic removes it from automatic lists. It does not silently delete its historical page.

## Adding a new doctor

1. Open **Snippets → Doctors → Add doctor**.
2. Enter verified credentials, role, registration details, biography, interests and photograph.
3. Keep **Create public page** enabled when a dedicated profile is needed.
4. Publish the record.

Automatic doctor blocks update from active, published records. A reviewable draft profile page is created when required. The page is not automatically published unless that option is explicitly enabled.

## Reusing the same section on several pages

Create a **Reusable section** snippet, build it once, publish it, then add a **Reusable section** block to any page. Editing and publishing the snippet updates every page that references it.

Good uses include:

- standard appointment CTA
- financing or consultation information
- clinic-wide notice
- aftercare disclaimer
- shared doctor or clinic strip
- seasonal campaign

## How the website adjusts automatically

The editor does not expose manual pixel positioning. Templates handle:

- desktop, tablet and mobile columns
- equal card heights
- text wrapping and overflow prevention
- image cropping and lazy loading
- dark mode
- touch-friendly carousel controls
- reduced-motion preferences
- semantic heading and list structure

Editors choose intent: width, maximum columns, theme, media side and placement. The website calculates the final layout.

## Safe publishing workflow

1. Save draft.
2. Preview desktop and mobile.
3. Confirm links, image alt text and section placement.
4. Set medical review status and dates for clinical content.
5. Publish or schedule.
6. Use page revisions to compare or roll back.

Internal links should use the page chooser rather than pasted website URLs. They remain valid if a page is moved.
