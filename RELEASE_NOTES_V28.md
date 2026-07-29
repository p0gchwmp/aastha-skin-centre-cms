# Editable CMS v28

This is the no-code Wagtail successor to the static website. It preserves the
reviewed v28 URLs and content while adding a complete editorial control centre.
Deploy it as a separate Render web service and test it before switching the
production domain.

## Imported and structured content

- 77 public pages
- 52 clinical pages
- 10 dedicated blog articles
- 345 complete FAQs
- 586 imported page-builder sections
- 250 legacy internal links converted into resilient Wagtail page references
- 2 clinic records and 1 doctor record

Sixty-five content pages were decomposed into ordinary text, FAQ, accordion and
CTA blocks. Advanced HTML remains available for the smaller set of bespoke
legacy layouts, but editors can replace those sections with visual blocks.

## No-code editing

- Drag-and-drop page sections
- Per-section width, theme, alignment, spacing, anchor and device visibility
- Text, images, video embeds, galleries, cards, FAQs, accordions, CTAs,
  related pages, doctor/clinic lists, pricing, reusable content and carousels
- Internal page choosers, external links and global Call/WhatsApp/Email actions
- Add and organise blogs, treatments, conditions, static pages, doctors and
  clinics without code
- Drafts, previews, scheduled publishing, moderation, locking, revisions and
  rollback
- Per-page SEO, social image, canonical URL, search visibility and medical
  review status

## Global controls

One Settings screen controls fee, follow-up policy, phones, WhatsApp, email,
logo, favicon, social image, header/footer navigation, announcement, legal
disclaimer, analytics and social links. Global tokens and action links update
everywhere at render time.

## Deployment and verification

- Fresh database import tested
- All 77 public pages rendered
- 72 internal destinations checked
- Search, sitemap, robots and database health routes tested
- Public admin dashboard, largest clinical editor, global settings and snippet
  screens tested
- Global fee, follow-up, phone and WhatsApp propagation tested
- All 17 page-builder block types loaded
- Django migrations, project checks and automated tests passed
- SQLite verification database integrity: `ok`

Read `ADMIN_GUIDE.md`, then run `30_Verify_CMS_v28.bat`.
