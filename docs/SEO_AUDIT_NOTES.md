# Current SEO backend audit notes

## Existing strengths

- canonical custom domain and permanent apex-to-www redirect;
- public/indexable canonical host with Render alias retained as noindex rollback host;
- per-page Wagtail SEO title and search description support;
- canonical override, social image and per-page noindex controls;
- XML sitemap generation with noindex pages excluded;
- MedicalClinic and Physician JSON-LD foundation;
- medical review status, reviewer and review-date fields;
- redirects application and middleware enabled;
- Search Console verification and analytics settings already available;
- strong automated route, visual, interaction, dark-mode and performance QA.

## Highest-priority gaps

1. Structured data is global rather than page-specific and models both branches as one clinic with an address array.
2. Clinic entities lack geo coordinates, opening-hours markup, map identifiers and branch-specific schema identity.
3. Nested pages do not receive an automatic BreadcrumbList graph.
4. Blog pages do not receive automatic BlogPosting schema.
5. Condition and treatment pages do not yet expose structured MedicalCondition / MedicalProcedure relationships.
6. Internal search-result pages are currently indexable unless separately blocked.
7. Page-two and later directory URLs need a canonical/discoverability review.
8. SEO fields are available but lack publication-time quality checks for missing, duplicate or overlong metadata.
9. Exact-page HTML preserves the legacy design but makes structured content relationships harder to scale; SEO-critical fields should remain CMS-managed.
10. Search Console and analytics settings exist, but measurement configuration must be completed and validated after launch.
