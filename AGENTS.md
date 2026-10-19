# Aastha Skin Centre — instructions for OmniRush agents

Read `docs/OMNIRUSH_HANDOFF_2026-10-19.md` and `EDITORIAL_V37_ROLLOUT.md` before doing any work.

## Project and goal
- This repository (`p0gchwmp/aastha-skin-centre-cms`) is the **production Wagtail/Django CMS**, not the old static-only concept.
- Renovate the **existing** Aastha Skin & Dermato-Cosmetic Centre website into a premium, fast, accessible, medically trustworthy, SEO/AEO/GEO-ready experience, while preserving its CMS, public routes, editor control, redirects, and verified content.
- Site: https://www.aasthaskincentre.in/
- Site owner wants an elegant, restrained, high-quality *luxury medical* design, meaningful mobile interaction, excellent conversion paths, real approved clinical/doctor imagery, and excellent technical SEO. Do not use AI-generated doctor photographs or invent patient results/testimonials.

## Branch safety — mandatory
- Treat `main` as production and **read-only** until the owner explicitly approves a cutover.
- Treat `concept/editorial-production-v37` as an auto-deploying Render staging branch; do **not push** to it casually.
- Begin on `handoff/omnirush-2026-10-19` (branched from `work/editorial-v37-final-qa`). Create a new `omnirush/<task>` branch from this handoff branch for implementation.
- Do **not** change DNS, Render service settings, database connections, public indexing, deploy hooks, or domain ownership without explicit approval.
- Do not trigger production deploys or merge to `main` automatically.
- Preserve `AASTHA_EDITORIAL_V37` default OFF on production; feature flag is the primary rollback switch.
- Never use a writable production database for QA. Keep staging and local test databases isolated.
- Do not rewrite existing Wagtail revisions, `ExactPageLayout` records, media or SEO metadata as a side effect of redesign.
- Do not expose `.env`, secrets, database dumps, patient records, exported CRM data, cloud provider tokens, unpublished consultation data, or private attachments to coding agent/model context. Use dummy/sanitized local fixtures.

## Code architecture
- Django 6 / Python 3.13 CI, Wagtail 7.4, PostgreSQL in hosted environments.
- Frontend: editorial-v37 Django templates, CSS, browser JavaScript; small React/Vite islands under `frontend/`.
- Runtime/public rendering controlled by `AASTHA_EDITORIAL_V37`.
- Existing QA: `.github/workflows/quality-gates.yml`, `tools/audit_accessibility.mjs`, `lighthouserc.cjs`, `tools/summarize_lighthouse.py`, `home/test_editorial_v37.py`.
- Always inspect actual code and docs before changing; project README describes an older v28 milestone and is **not** the latest release specification.

## Clinic truth constraints
- Brand: Aastha Skin & Dermato-Cosmetic Centre; two Jammu branches: Karan Nagar/Amphalla and Paloura.
- Dr. Cheena Langer — dermatologist, MD Dermatology, Venereology & Leprology; laser and hair-transplant specialist.
- Public clinic hours: `10:00 AM–8:00 PM`; doctor consultation slots: Karan Nagar `11:00 AM–3:00 PM`, Paloura `6:00 PM–8:00 PM`. Do not assert that slots are available every day; request same-day confirmation.
- Call: `97966 76541`, `70066 13362`; appointment WhatsApp `+917006613362`.
- Do not create an appointment automatically from a WhatsApp request: appointment workflow submits a prefilled **request** and reception confirms it.
- Do not invent efficacy rates, case counts, superiority claims, pricing, reviews, medical affiliations, awards, branch availability or doctor credentials. Any new treatment copy requires clinic medical review before public publishing.

## Engineering and quality
1. First establish reproducible local builds and **fix the QA pipeline itself**; separate infra/test errors from product defects. Preserve helpful audit artifacts.
2. Fix known contrast/ARIA/accessible-name issues based on actual rendered DOM; do not lower WCAG thresholds to hide failures.
3. Optimize mobile LCP, image discoverability, modern WebP/srcset/sizes, caching and CSS without sacrificing core layout or responsiveness.
4. Preserve the current public permalink structure, metadata, canonical URLs, breadcrumbs, MedicalClinic/Physician schema as applicable, sitemap and robots. Staging remains noindex.
5. Verify appointment, call, WhatsApp, Google Maps, mobile nav, keyboard flows, reduced-motion and admin behavior.
6. Run two separate modes: legacy rollback suite with `AASTHA_EDITORIAL_V37=0`; v37 contract tests with flag `1`.
7. Release criteria: production-like build and SEO audits 0 errors; all regression tests green; WCAG on 12 representative desktop/mobile scenarios with 0 blocking AA violations; full mobile and desktop Lighthouse representative route gates; responsive images; no broken routes.
8. Before any production promotion: independent staging preview, diff review, DB+media backup, rollback rehearsal and explicit approval from site owner.
9. Commit coherent, small diffs; give exact file paths, command output, links and measurable results. Do not claim a green test unless that exact SHA passed.

## First task
Follow `docs/OMNIRUSH_HANDOFF_2026-10-19.md` section "First OmniRush mission". Audit current branch & GitHub Actions, diagnose latest isolated QA failure, fix the workflow and remaining real frontend issues on a **non-Render** feature branch. Do not deploy.
