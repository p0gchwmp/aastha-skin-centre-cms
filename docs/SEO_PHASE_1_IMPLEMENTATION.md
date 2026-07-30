# SEO Phase 1 implementation slice

The first code change should be limited to low-risk backend improvements that do not rewrite medical content:

1. Add `noindex,follow` to internal search-result pages.
2. Generate page-specific structured-data graphs while preserving the existing homepage graph:
   - Organization / WebSite
   - two separate MedicalClinic branches
   - Physician/ProfilePage
   - BreadcrumbList
   - BlogPosting for BlogPage
3. Add clinic latitude, longitude and opening-hours fields to ClinicLocation with safe blank defaults.
4. Add social `sameAs` URLs to organization/physician entities.
5. Add automated tests for schema identity, canonical origins, visible-data parity and invalid/missing values.
6. Add a crawler audit for titles, descriptions, H1, canonical, robots and schema across all indexable routes.

Content rewrites, locality landing pages, Search Console submission and review-platform changes are separate workstreams and should not be bundled into this code change.
