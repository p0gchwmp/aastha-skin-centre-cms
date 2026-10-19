# OmniRush takeover handoff — Aastha website renovation
**Prepared:** 19 October 2026  
**Status:** safe work branch prepared; **production not changed**  
**Read with:** `AGENTS.md`, `EDITORIAL_V37_ROLLOUT.md`, `docs/editorial-v37-cutover.md`, `docs/BACKUP_AND_RECOVERY.md`

## 1. Identity and source of truth

| Role | Value |
|---|---|
| Public site | `https://www.aasthaskincentre.in/` |
| Production CMS repository | `p0gchwmp/aastha-skin-centre-cms` |
| Production branch | `main` |
| Last explicitly verified pre-v37 production rollback anchor | `a62c76343c26c7b10de4d26a20f65d83daf3a270` |
| Render CMS staging branch (auto-deploy) | `concept/editorial-production-v37` |
| Current isolated QA working branch | `work/editorial-v37-final-qa` |
| **OmniRush handoff branch** | `handoff/omnirush-2026-10-19` |
| Static/visual concept reference repo | `p0gchwmp/aastha-skin-centre` |
| Static concept branch | `concept/editorial-interactive-v1` |
| Current architecture | Django/Wagtail CMS rendering an editorial-v37 site behind a feature flag |
| Primary production rollback | Set `AASTHA_EDITORIAL_V37=0` (subject to runbook) |

**Important:** The static concept repo is a design/reference source, **not** the deployable production CMS. Do not swap the domain to the static concept. The work should be integrated into the CMS repo.

On 19 Oct 2026 GitHub comparison confirmed:
- `concept/editorial-production-v37` was **270 commits ahead of `main`**, no commits behind.
- `work/editorial-v37-final-qa` was **6 commits ahead of staging**, no commits behind.
- The isolated QA branch changed: `.github/workflows/quality-gates.yml`, `home/static/css/editorial-v37-release-gate.css`, `home/static/js/editorial-v37-release-gate.js`, `home/templates/home/home_page.html`, and `home/templates/home/doctor_page.html`.

Use these relative positions as the verified handoff snapshot; **recheck Git refs and deployed releases** before making decisions because they can move.

## 2. What has been built

The current editorial-v37 stage is well beyond a mock-up:
- 96 public routes in a production-like CMS release audit, including 52 clinical pages and 10 dedicated blog pages.
- 96/96 native editorial renderers, zero legacy fallback; 85 tested internal link targets.
- CMS editor, page/revision history, clinic and doctor models, doctor-approved media, SEO metadata and a booking-request interface are retained.
- A reconciler changes only exact stale known branch-hour strings and preserves values an editor already customized.
- Staging respects `noindex`; production public canonical is expected to be `https://www.aasthaskincentre.in`.
- Analytics/GA4 event hooks exist for appointment/call/WhatsApp/branch/maps interactions.
- Static concept previously received strong mobile/desktop design and page audit results; CMS integration is the current unit of work.
- At one verified staging candidate (the historical `f2b97540...` stage), 256 rollback-mode tests and 42 v37-specific contracts passed; separate SEO audit reported 0 errors. These are **historical proofs, not proof that the current handoff HEAD is green**.
- A later isolated QA evaluation reported 12/12 WCAG representative cases clear and mobile Lighthouse ~94–96, desktop ~99–100, but some Lighthouse thresholds and a specific Karan card contrast inheritance remained; these numbers must be freshly confirmed.

## 3. Current unresolved work / why release is not frozen

The isolated QA branch was created specifically to avoid burning Render build minutes and repeated deployment notifications.

Latest meaningful isolated fixes staged on the work branch include:
- Remove logo link accessible-name/visible-label mismatch.
- Prevent light address text rules from recoloring a dark Karan Nagar clinic card.
- Improve hero asset loading via early discovery/preloads and smaller responsive doctor image candidates.
- Adjust CI workflow to run on `work/editorial-v37-final-qa` while **not** touching Render staging or production.

The old QA run on code commit `b06e584885fcf9c7bf165900799bcc38801afa88` failed due to a **stale workflow definition**, not proven app regression: it invoked nonexistent `audit_release`, never started the local site, then Lighthouse hit `CHROME_INTERSTITIAL_ERROR`, and called `summarize_lighthouse.py` with outdated `--mobile/--desktop` flags.

That workflow was subsequently corrected on the work branch and latest chat-reported isolated revision was `943d5e2e...`, but **no completed green run of that exact revision is proven here**. Check GitHub Actions afresh and do not assume the quality gate passed.

The workflow in the handoff branch currently triggers for `concept/editorial-production-v37` and `work/editorial-v37-final-qa` only. The handoff branch is intentionally **not a Render branch** and does not yet automatically run that QA workflow on commits.

## 4. First OmniRush mission

Work in a *new* `omnirush/<task-name>` branch derived from `handoff/omnirush-2026-10-19`.

### Mission A — recreate the ground truth
1. `git fetch --all --prune`; inspect `git status`, `git log`, branch comparisons, workflow history and repository docs.
2. Verify code in `AGENTS.md` and the four deployment/rollback runbooks above.
3. Inspect the current `.github/workflows/quality-gates.yml`, `tools/audit_accessibility.mjs`, `lighthouserc.cjs`, `tools/summarize_lighthouse.py` and the release/SEO management commands. **Do not run an old audit command by memory.**
4. Establish a clean local Python virtualenv and Node installation. Use dummy credentials, a local disposable SQLite test database, and the existing `aastha_cms.settings.quality` settings for CI-parity builds.
5. Review latest failed/passing Actions evidence on the isolated work branch before editing; distinguish infrastructure failures from a real accessibility/performance regression.

### Mission B — complete the release gate
1. Fix actual WCAG contrast/ARIA/visible-label findings, without suppressing or ignoring axe rules. Recheck mobile dark/light and Karan Nagar address card.
2. Verify homepage/doctor hero preload behavior, proper responsive images (`srcset`/`sizes`/`width`/`height`), LCP discoverability and no duplicate preload downloads. Confirm images remain real approved photos.
3. Meet the existing mobile and desktop Lighthouse budgets; optimize real bottlenecks, do not simply lower scores or remove failed assertions.
4. Verify all 12 representative WCAG desktop/mobile cases with **0 blocking violations**, 256 legacy tests and 42 v37 contract tests or their then-current exact counts, SEO release audit, 96 route parity, appointment functions, and editor access.
5. Record exact revision SHA, commands, failing/passing tests, representative scorecard and artifact links. Only claim the exact SHA green when it is.
6. Prepare a code review / pull request; **do not merge to Render staging or production without approval**.

### Mission C — finish comprehensive renovation, not just a benchmark
After the release gate is stable, complete page-by-page quality assurance: hero and navigation, doctor profile credibility, both location pages, all high-intent treatment pages, real approved images, clinical editorial hierarchy, appointment conversion and admin editability. Preserve premium aesthetic, excellent mobile layout and accessibility. Remove placeholders/duplicate legacy scripts only after verifiable parity. Medical efficacy claims require review.

### Mission D — launch only after owner authorizes
- Recheck live CMS deploy and rollback SHA first.
- Back up production PostgreSQL and persistent media, independently.
- Promote the reviewed commit into staging once; test with noindex.
- Use existing two-step feature-flag cutover in `EDITORIAL_V37_ROLLOUT.md` and `docs/editorial-v37-cutover.md`. Do not change domain/DNS.
- Keep flag off when initially promoting code to production, then enable after green smoke tests and specific approval.
- Post-launch audit canonical, robots, sitemap, schema, both branch pages, forms, calls, WhatsApp, redirects, admin, analytics, 404/5xx and real mobile devices.
- Roll back via the flag if anything critical fails. Restore DB only if a separate data-changing incident requires it.

## 5. Quality commands (verify against current repo)

```bash
# Run in an isolated checkout of the handoff/feature branch.
python -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
npm --prefix frontend install --no-audit --no-fund
npm --prefix frontend run build

export DJANGO_SETTINGS_MODULE=aastha_cms.settings.quality
export AASTHA_EDITORIAL_V37=1
export PUBLIC_SITE_URL=""
export SECRET_KEY="quality-gate-only-not-for-production"
python manage.py check
python manage.py migrate --noinput
python manage.py initialize_cms
python manage.py sync_public_clinic_facts
python manage.py audit_editorial_v37
python manage.py check_launch_config
python manage.py audit_seo_content --json /tmp/aastha-seo-content.json --fail-on-errors
python manage.py qa_cms_release

AASTHA_EDITORIAL_V37=0 python manage.py test
AASTHA_EDITORIAL_V37=1 python manage.py test \
  home.test_editorial_v37 \
  home.test_staging_robots \
  home.test_domain_cutover \
  home.test_google_measurement_readiness
```

For full asset regeneration and Lighthouse/axe, use the exact steps in `.github/workflows/quality-gates.yml`. A clean checkout needs `tools/build_visual_cue_assets.py`, `tools/install_curated_visual_cue_assets.py`, `tools/generate_responsive_clinical_images.py` and collected static files **before** the served-page visual suite, matching the workflow.

## 6. User-facing website facts to preserve

**Aastha Skin & Dermato-Cosmetic Centre**, Jammu. Dr. Cheena Langer, MD Dermatology, Venereology & Leprology; laser and hair transplant specialist. **Karan Nagar/Amphalla** and **Paloura** branches. Clinic hours: **10:00 AM–8:00 PM**; Karan Nagar doctor slot **11:00 AM–3:00 PM**; Paloura **6:00 PM–8:00 PM**; consultation availability needs confirmation. Clinic phones: **97966 76541**, **70066 13362**; WhatsApp bookings to **+917006613362**. The website generates a WhatsApp **request**, *not* a confirmed booking. Do not change these without authoritative clinic approval.

## 7. Non-negotiable acceptance

- Content editor and Wagtail revisions remain intact.
- No patient or confidential clinic data enters OmniRush context or a GitHub commit.
- 0 accidental 404s, no `/concept/` public links, valid canonical/schema/sitemap/robots.
- Staging and Render preview aliases remain noindex.
- Appointments/WhatsApp/calls/Maps behave correctly on real phones.
- No invented medical content, fake images or fake clinical before/after results.
- Verified mobile performance and responsive UX; WCAG AA blockers zero.
- Production not modified until the user clearly authorizes launch.

## 8. Suggested very first prompt to OmniRush

> Read AGENTS.md and docs/OMNIRUSH_HANDOFF_2026-10-19.md completely. Take ownership of the Aastha editorial-v37 website renovation, starting from this isolated handoff branch. Inspect the actual code, recent commits, workflows and release runbooks. First audit the current state; identify precise blockers to the 12-case WCAG and mobile/desktop Lighthouse gate. Fix those in a new omnirush/* branch, validate the exact commit locally and in CI, then produce a diff-based, test-backed release recommendation. Continue the full premium-medical site renovation page by page without replacing the existing Wagtail CMS or disturbing production. Never deploy, push to Render-watched branches, change DNS, read private patient data or expose secrets without my express approval.
