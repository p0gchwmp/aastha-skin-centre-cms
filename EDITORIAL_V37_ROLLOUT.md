# Editorial v37 production rollout

This runbook replaces the public frontend without throwing away the existing Wagtail CMS, URLs, SEO metadata, analytics, media library or rollback path.

## Safety contract

- Production service remains `aastha-skin-centre-cms` on `main` until staging is approved.
- Development happens on `concept/editorial-production-v37`.
- `AASTHA_EDITORIAL_V37` defaults to **off**.
- Do not connect editorial staging to the writable production database.
- Do not delete `ExactPageLayout` records during rollout.
- Do not change existing public slugs unless a permanent redirect is added and verified.
- Do not use the `/concept/` namespace in production templates or public links.
- Back up production Postgres and `/var/data/media` before the final merge/cutover.

## Stage 1 — CMS staging

Service: `aastha-editorial-cms-staging`

1. Deploy `concept/editorial-production-v37` with `AASTHA_EDITORIAL_V37=1`.
2. Keep the staging hostname on `*.onrender.com`; the existing middleware/base template must emit `noindex,nofollow` and an `X-Robots-Tag` header.
3. Run `./build.sh`.
4. Run:
   ```bash
   python manage.py test home.test_editorial_v37 home.test_staging_robots
   ```
5. Smoke-test the homepage and representative routes from every page family:
   - `/`
   - `/conditions/`
   - `/treatments/`
   - `/treatments/acne-treatment/`
   - `/treatments/acne-scar-treatment/`
   - `/treatments/pigmentation-treatment/`
   - `/treatments/hair-fall-treatment/`
   - `/treatments/laser-hair-reduction/`
   - `/treatments/fungal-infection-treatment/`
   - `/treatments/hair-transplant/`
   - `/treatments/botulinum-toxin-dermal-fillers/`
   - `/dr-cheena-langer/`
   - `/locations/karan-nagar/`
   - `/locations/paloura/`
   - `/blog/`
   - `/book-appointment/`
   - `/contact/`
6. Verify forms, call/WhatsApp links, maps, Wagtail images, clinical-result galleries, mobile navigation, keyboard navigation and reduced motion.
7. Verify staging is not indexable before sharing it broadly.

## Stage 2 — parity and SEO gate

Before production:

1. Crawl the current public site and the v37 staging site.
2. Compare status codes and canonical paths.
3. Require zero accidental `404`, `500`, mixed-content or `/concept/` links.
4. Preserve current URLs wherever possible.
5. For any intentionally retired URL, add and test one permanent redirect to the closest equivalent page. Avoid redirect chains.
6. Validate:
   - unique titles and meta descriptions;
   - canonical tags;
   - `MedicalClinic`, `Physician`, `BlogPosting` and relevant breadcrumb/page structured data;
   - sitemap output;
   - robots behavior;
   - Open Graph and Twitter metadata;
   - GA4/Search Console tags;
   - internal links to both Jammu clinics.
7. Run Lighthouse/mobile performance checks on representative pages. Resolve layout shift, oversized images and render-blocking regressions before cutover.

## Stage 3 — pre-production backup

Immediately before merging:

1. Create a production Postgres backup/snapshot in Render.
2. Create or verify a copy/snapshot of the persistent media disk mounted at `/var/data/media`.
3. Record the currently deployed production commit SHA and deploy ID.
4. Confirm production `AASTHA_EDITORIAL_V37` is absent or `0`.
5. Confirm no schema/data migration is required by the v37 frontend changes. If a later v37 change does require one, write and test a forward/rollback migration separately before continuing.

## Stage 4 — zero-downtime code rollout

1. Merge the approved v37 branch to `main`.
2. Allow Render production auto-deploy to finish with the flag **off**.
3. Smoke-test the production custom domain. It should still display the legacy frontend because the flag is off.
4. Verify `/healthz/`, admin login, public forms, canonical tags and sitemap.
5. Set `AASTHA_EDITORIAL_V37=1` on the production service.
6. Let Render perform the environment-triggered deploy/restart.
7. Smoke-test the custom domain immediately on desktop and mobile.

## Stage 5 — post-cutover verification

Check immediately, then again after caches settle:

- homepage and representative clinical pages return `200`;
- booking submission works end to end;
- phone, WhatsApp and map destinations are correct;
- Wagtail `/admin/` remains authenticated and usable;
- real uploaded imagery and consented clinical-result imagery load;
- no staging/noindex header leaks onto `www.aasthaskincentre.in`;
- canonical host is `https://www.aasthaskincentre.in`;
- sitemap/robots are correct;
- analytics requests fire once, not twice;
- no `/concept/` links exist;
- no severe browser-console or server errors appear;
- 404 and 5xx rates do not jump.

## Emergency rollback

The fastest rollback does **not** require a git revert or database restore.

1. Set production `AASTHA_EDITORIAL_V37=0`.
2. Let Render restart/redeploy.
3. Confirm the legacy frontend is rendering again.
4. Keep the production database and page revisions untouched.
5. Investigate the v37 issue on the branch/staging service.

Only restore a database/media backup if an independent data-changing incident occurred. The v37 frontend rollout itself is designed not to require a data rollback.

## Cleanup after stable launch

Do not perform this on launch day.

After v37 has been stable and approved:

1. Remove superseded legacy CSS/JS from the v37 path to improve Core Web Vitals.
2. Self-host/subset production fonts if that is the selected performance/privacy policy.
3. Consolidate duplicate historical frontend styles while retaining the feature-flag rollback until a later release.
4. Retain Wagtail revisions, redirects and structured content.
