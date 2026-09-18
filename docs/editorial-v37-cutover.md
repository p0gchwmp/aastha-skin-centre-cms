# Editorial v37 production cutover

This runbook is the production replacement contract for Aastha Skin Centre.

## Safety principles

- Keep the current public frontend available until the final cutover.
- Preserve all existing public URLs.
- Do not point staging at the production database.
- Do not migrate or rewrite production content merely to change presentation.
- The v37 frontend is controlled by `AASTHA_EDITORIAL_V37`.
- The rollout flag defaults to **off**.
- Query parameters cannot enable the rollout.
- A rollback must not require a database restore.

## Current architecture

The existing Wagtail models, revisions, images, redirects, SEO fields, clinic
records, doctor records, page hierarchy and ExactPageLayout snapshots remain
the content system.

Editorial v37 is the rendering layer.

The v37 deployment gate requires:

- every live public Wagtail page to have a native v37 renderer;
- every audited route to return HTTP 200;
- no duplicate IDs;
- no dead `href="#"` anchors;
- no `/concept/` URLs;
- no legacy v3-v11 premium runtime under v37;
- staging to remain noindex;
- internal public links to resolve;
- the appointment form contract to exist;
- Wagtail admin routes to require authentication.

## Phase 1 — isolated CMS staging

Service: `aastha-editorial-cms-staging`

Required environment:

```
AASTHA_EDITORIAL_V37=1
PUBLIC_SITE_URL=
SITE_HOSTNAME=<render staging hostname>
```

The staging site must remain noindex and must not use the production database.

Before promotion:

1. Build must pass `audit_editorial_v37`.
2. Editorial rollout tests must pass.
3. Staging robots tests must pass.
4. Confirm homepage, conditions, treatments, common treatment pages, doctor,
   clinics, booking, contact, journal and long-tail medical pages.
5. Confirm mobile navigation and Explore.
6. Confirm all booking actions use the approved clinic contact details.
7. Confirm no unapproved medical outcome claims.
8. Confirm no placeholder or AI doctor imagery.
9. Confirm media fallbacks are from approved Aastha visual assets.
10. Confirm browser QA at desktop, tablet and mobile widths.

## Phase 2 — production code promotion with rollout OFF

Only after staging approval:

1. Create a production database snapshot / verified backup.
2. Record the current production deploy ID and git SHA.
3. Merge the reviewed v37 branch into `main`.
4. Keep `AASTHA_EDITORIAL_V37=0` on production.
5. Let Render deploy.
6. Verify the existing public frontend still renders normally.
7. Verify health check, Wagtail admin login, media delivery, sitemap, robots,
   canonical URLs and booking/contact paths.
8. Do not change DNS.

This phase proves the new code can coexist with the current public frontend.

## Phase 3 — visual cutover

After Phase 2 passes:

1. Set `AASTHA_EDITORIAL_V37=1` on the existing production CMS service.
2. Allow Render to restart/deploy with the new environment.
3. Verify on the Render alias first when possible.
4. Verify the custom domain:
   - homepage;
   - /conditions/;
   - /treatments/;
   - top clinical landing pages;
   - Dr. Cheena Langer;
   - both clinic pages;
   - booking;
   - contact;
   - journal;
   - sitemap.xml;
   - robots.txt.
5. Confirm canonical URLs still point to `https://www.aasthaskincentre.in`.
6. Confirm the custom domain is indexable and Render aliases remain noindex.
7. Confirm analytics and Search Console verification remain present.
8. Confirm 404 and redirect behaviour.
9. Confirm Core Web Vitals / Lighthouse from a real browser.

No public URL change or DNS cutover should be required.

## Immediate rollback

If the new frontend has a critical production problem:

1. Set `AASTHA_EDITORIAL_V37=0`.
2. Restart/redeploy the production service.
3. Verify the old frontend is restored.
4. Keep the CMS/database in place.
5. Investigate on staging.

If the release contains a code-level problem independent of the flag, redeploy
the recorded pre-v37 production deploy or revert the merge commit.

A database restore is a last resort, not the normal frontend rollback method.

## Post-cutover

After a stable observation period:

- keep ExactPageLayout snapshots until the new frontend has proven stable;
- keep Wagtail revision history;
- keep redirects;
- monitor 404s and Search Console coverage;
- monitor booking/contact errors;
- monitor Render error logs and latency;
- review top organic landing pages for traffic/ranking regressions;
- only then remove legacy frontend assets in a separate cleanup release.

## Persistent staging admin

The current visual staging service may use ephemeral SQLite. That is acceptable
for automated route/render QA, but not for long-lived editorial UAT.

Before staff/admin UAT, attach a dedicated persistent staging database or
another explicitly approved persistent store. Do not reuse CRM staging data and
do not connect staging with write access to the production website database.
