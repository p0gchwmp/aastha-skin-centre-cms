# Aastha CMS custom-domain cutover

This runbook changes infrastructure and indexability, not website copy or SEO
strategy. Do not begin until clinic facts, service claims, conversion tests and
pre-launch backups are approved.

## 1. Approve one canonical origin

Choose exactly one:

- `https://www.aasthaskincentre.in`
- `https://aasthaskincentre.in`

The other hostname becomes a permanent redirect. Do not configure both as
indexable copies. Record the approved choice in GitHub issue #9 before changing
Render or DNS.

## 2. Capture recovery points

Before touching DNS:

1. Create and download a Render PostgreSQL export.
2. Create a portable media archive and move it off Render.
3. Record the current CMS release from `/healthz/`.
4. Confirm the static Render service is still healthy.
5. Record the current DNS values and TTLs with screenshots.

Follow `docs/BACKUP_AND_RECOVERY.md` for the database and media procedure.

## 3. Attach custom domains to the CMS service

In the Render dashboard for `aastha-skin-centre-cms`:

1. Add the approved canonical hostname.
2. Add the alternate hostname so Render can issue TLS for it and serve the
   application-level permanent redirect.
3. Use the exact DNS records Render displays. Do not guess record targets from
   this document.
4. Wait until Render reports successful verification and certificate issuance
   for both hostnames.

Do not remove the `*.onrender.com` hostname. It remains the noindex health and
rollback endpoint.

## 4. Set production environment variables

Use the approved values, with no trailing slash:

```text
PUBLIC_SITE_URL=https://<canonical-host>
SITE_HOSTNAME=<canonical-host>
WAGTAILADMIN_BASE_URL=https://<canonical-host>
CANONICAL_REDIRECT_HOSTS=<alternate-host>
ALLOWED_HOSTS=.onrender.com,aasthaskincentre.in,www.aasthaskincentre.in
CSRF_TRUSTED_ORIGINS=https://*.onrender.com,https://aasthaskincentre.in,https://www.aasthaskincentre.in
```

`CANONICAL_REDIRECT_HOSTS` is deliberately blank during staging. Never include
an `*.onrender.com` hostname or the canonical hostname itself.

Redeploy after saving the variables. `initialize_cms` synchronises the default
Wagtail Site hostname to `SITE_HOSTNAME` without reimporting existing content.

## 5. Validate configuration inside Render

Open a Render shell and run:

```bash
python manage.py check_launch_config --require-public
```

It must confirm:

- HTTPS canonical origin;
- Wagtail Site hostname matches the canonical host;
- Wagtail admin base URL matches the canonical origin;
- allowed-host and CSRF origin coverage;
- alternate-host redirect configuration;
- secure cookies and HTTPS redirect settings.

Do not continue if this command fails.

## 6. Run the external cutover audit

Example when `www` is canonical:

```bash
python tools/audit_domain_cutover.py \
  --canonical https://www.aasthaskincentre.in \
  --alternate https://aasthaskincentre.in \
  --render https://aastha-skin-centre-cms.onrender.com \
  --expected-release <release-from-healthz>
```

For an apex canonical origin, swap the canonical and alternate arguments.

The audit verifies:

- canonical homepage is indexable;
- canonical, Open Graph and clinic JSON-LD URLs use the final origin;
- canonical robots file allows crawling and declares the final sitemap;
- sitemap URLs use the canonical origin;
- alternate hostname permanently redirects with its path and query preserved;
- Render alias remains available, noindex and blocked in robots;
- health endpoint reports the expected release.

The report is written to `audit-artifacts/domain-cutover/`.

## 7. Manual conversion check on the final domain

On a real iPhone and Android phone:

- open the homepage and one long clinical page in light and dark mode;
- call both numbers;
- open WhatsApp;
- submit the appointment request for both clinics;
- open both Maps destinations;
- open Facebook, Instagram and YouTube;
- log into Wagtail through the final domain;
- upload one harmless test image and then remove it;
- perform the deferred publish/revert banner test.

## 8. Search and analytics handoff

Only after every cutover check passes:

- provide the agreed SEO reference websites;
- review metadata, schema and internal-link strategy;
- configure approved analytics;
- verify Search Console properties;
- submit the final sitemap;
- monitor coverage, Core Web Vitals and conversions.

Do not submit the sitemap while the custom domain is still noindex or while
canonical-host redirects are unresolved.

## Rollback

Keep the static service available for at least 7–14 days.

If a serious launch issue occurs:

1. Record the failing CMS release and symptoms.
2. Set `PUBLIC_SITE_URL` and `CANONICAL_REDIRECT_HOSTS` blank to return the CMS
   to noindex staging behaviour, then redeploy if the CMS must remain online.
3. Restore the previously recorded DNS routing or attach the custom domain to
   the retained static service according to the pre-recorded rollback plan.
4. Verify calls, WhatsApp and appointment paths on the rollback target.
5. Do not delete the CMS database or media disk while investigating.

A rollback is complete only after the custom domain, both mobile conversion
paths and search-indexing headers have been rechecked.
