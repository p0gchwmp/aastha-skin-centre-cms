# Editorial Milestone 3 — CMS Parity & Release Readiness

## Scope

Move the approved editorial concept into the existing Wagtail CMS without changing the public information architecture, SEO contracts, booking flow, analytics behavior, media ownership or rollback path.

This milestone applies to:

- CMS repo: `p0gchwmp/aastha-skin-centre-cms`
- Staging branch: `concept/editorial-production-v37`
- Staging service: `aastha-editorial-cms-staging`
- Staging URL: https://aastha-editorial-cms-staging.onrender.com/
- Production branch: `main` — untouched until explicit cutover approval

The editorial concept remains the visual source of truth.

---

## 3A — Interaction & design parity

Status: **GREEN on staging**

Validated on Render after the parity slice:

- 77/77 live CMS routes use native editorial renderers.
- 0 legacy fallback routes in v37 staging.
- Editorial v37 route/link/document-integrity audit passes.
- Responsive clinical image audit passes.
- Frontend Vite build passes.
- Staging/noindex tests pass.
- Editorial/staging test suite passes.

Parity refinements carried from the approved concept:

- keyboard-focusable treatment rail with Arrow / Home / End navigation;
- roving keyboard semantics for choice matrices, atlas selectors and clinic selectors;
- proper tab / tabpanel relationships;
- homepage current-section navigation state;
- balanced heading and paragraph wrapping;
- fixed-header anchor offsets;
- focus-visible treatments for interactive editorial controls;
- subtle Motion content-swap and FAQ transitions;
- reduced-motion behavior retained.

Regression contracts are asserted in `home/test_editorial_v37.py`.

---

## 3B — Content, SEO & release evidence

Status: **IN PROGRESS**

### Automated evidence required

1. Staging hostname stays `noindex,nofollow` and returns the staging robots contract.
2. All public routes return expected status codes.
3. No accidental `/concept/` links exist.
4. Canonicals and final route paths match production intent.
5. Titles and descriptions remain unique/valid.
6. Structured data stays valid for:
   - MedicalClinic
   - Physician
   - BlogPosting
   - BreadcrumbList
   - MedicalWebPage / MedicalCondition / MedicalProcedure where applicable
7. Sitemap and robots output remain valid.
8. Booking contract remains intact.
9. Phone, WhatsApp, map and clinic links are verified.
10. Mobile + desktop accessibility/performance QA is green on representative routes.
11. No severe browser-console/server errors.
12. Analytics fires only once when enabled.

### Human clinic sign-off required

Before production cutover, confirm:

1. Dr. Cheena Langer qualifications, registration details and approved experience wording.
2. Karan Nagar and Paloura:
   - full address and PIN;
   - map URL;
   - phone routing;
   - doctor/reception/procedure timings.
3. Consultation fee and follow-up policy.
4. Services offered per branch and approved device/machine names.
5. Consent status for patient photographs, clinical-result images and testimonials.
6. Final alt text for real clinic/patient media.
7. Privacy, medical disclaimer, booking/contact wording and analytics-consent requirements.
8. Final Search Console, sitemap, GBP and analytics settings.

No automated result overrides this sign-off.

---

## 3C — Production cutover

Status: **BLOCKED pending explicit approval**

Cutover sequence:

1. Back up production Postgres.
2. Back up/verify persistent production media.
3. Record current production commit and deploy ID.
4. Confirm production `AASTHA_EDITORIAL_V37` remains off.
5. Merge approved staging branch into `main` with the feature flag still off.
6. Deploy and verify that legacy production still renders.
7. Re-test health, admin, forms, canonical tags and sitemap.
8. Only after explicit approval, set `AASTHA_EDITORIAL_V37=1`.
9. Smoke-test the custom domain immediately on desktop/mobile.
10. Keep feature-flag rollback available.

Emergency rollback remains:

`AASTHA_EDITORIAL_V37=0`

No database rollback should be needed for frontend-only parity work.

---

## Current release boundary

The CMS staging implementation may continue to be audited and refined.

Do **not**:

- merge to `main`;
- toggle the production feature flag;
- point the production custom domain at staging;
- connect staging to the writable production database;
- publish unapproved medical/experience claims or patient media.
