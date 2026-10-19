# Aastha Skin Centre — instructions for OmniRush agents

**Required reading in order:** `AGENTS.md` → `docs/AASTHA_2_0_CREATIVE_DEVELOPMENT_BRIEF.md` (the owner's complete creative vision) → `docs/OMNIRUSH_HANDOFF_2026-10-19.md` (technical handoff) → `EDITORIAL_V37_ROLLOUT.md` (deployment safeguards). The creative brief directs the design; the technical handoff controls the existing architecture, protected clinic facts, and production safety.

## Project and goal
- This repository (`p0gchwmp/aastha-skin-centre-cms`) is the **production Wagtail/Django CMS**, not the old static-only concept.
- Renovate the **existing** Aastha Skin & Dermato-Cosmetic Centre website into a premium, fast, accessible, medically trustworthy, SEO/AEO/GEO-ready experience, while preserving its CMS, public routes, editor control, redirects, and verified content.
- Site: https://www.aasthaskincentre.in/
- **Owner-confirmed visual inspiration / review preview:** https://aastha-editorial-concept-preview.onrender.com/ . Render confirms this is a separate static concept site: repository `p0gchwmp/aastha-skin-centre`, branch `concept/editorial-interactive-v1`, built using `scripts/build_concept_preview.py`. The editable CMS on this repository remains the implementation to ship. Preserve and improve the concept's visual direction on CMS v37, not on an unrelated new site.
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
- **Design synchronization requirement:** compare CMS v37 desktop/mobile pages directly against the static concept preview. Keep the premium look, add well-curated, appropriately licensed Pinterest-inspired imagery and asymmetrical editorial cards while retaining approved real clinician/clinical imagery, SEO, semantic markup and speed. When preview updates are needed, batch them and coordinate with the site owner; the separate static preview does not auto-update when CMS source changes.
- Do not push frequently to either Render-watched branch simply to refresh screenshots: previously the Render workspace exhausted build minutes and sent repeated failure notifications. Use local/CI browser screenshots and an isolated review branch first; only deliberately deploy a reviewed snapshot once capacity is confirmed.

## Clinic truth constraints
- Brand: Aastha Skin & Dermato-Cosmetic Centre; two Jammu branches: Karan Nagar/Amphalla and Paloura.
- Dr. Cheena Langer — dermatologist, MD Dermatology, Venereology & Leprology; laser and hair-transplant specialist.
- Public clinic hours: `10:00 AM–8:00 PM`; doctor consultation slots: Karan Nagar `11:00 AM–3:00 PM`, Paloura `6:00 PM–8:00 PM`. Do not assert that slots are available every day; request same-day confirmation.
- Call: `97966 76541`, `70066 13362`; appointment WhatsApp `+917006613362`.
- Do not create an appointment automatically from a WhatsApp request: appointment workflow submits a prefilled **request** and reception confirms it.
- Do not invent efficacy rates, case counts, superiority claims, pricing, reviews, medical affiliations, awards, branch availability or doctor credentials. Any new treatment copy requires clinic medical review before public publishing.

## Aastha 2.0 creative direction and execution order
- The owner wants **award-worthy, memorable editorial medical design**, inspired by the *creative quality and interaction concepts* of `https://www.allthingsniro.com/` and `https://www.allthingswtf.com/`, not a soda-site clone. Read the complete specifications in `docs/AASTHA_2_0_CREATIVE_DEVELOPMENT_BRIEF.md` before recommending a visual language.
- Preserve/advance the current concept preview at `https://aastha-editorial-concept-preview.onrender.com/`. Build toward **CMS-integrated, maintained** visual parity, never an unrelated static redesign.
- Use oversized expressive typography, refined medical copy, dynamic but readable composition, Pinterest-inspired licensed/owned images, intelligent concern exploration, distinctive treatment narratives, engaging but straightforward booking and rich real doctor/clinic imagery.
- Avoid generic AI landing pages, repetitive cards, gradients/glassmorphism, excessive animation and fabricated clinical media.
- **Work order**: Phase 1 inspect BOTH GitHub repos, preview/live/staging, deployments, visual strengths, stack, dependencies, flows, outstanding QA; Phase 2 present a cohesive Aastha 2.0 concept with typography, colour, page-by-page choreography, meaningful technology trade-offs, and get owner direction; Phase 3 implement an interactive, accessible **CMS-based** homepage prototype; Phase 4 renovate page families; Phase 5 harden with all quality gates. Diagnose material blockers during audit, but do not make broad visual changes before Phases 1–2.
- Consider GSAP/ScrollTrigger for justified choreographed motion; Lenis only if smooth scrolling adds value without scroll hijacking; SplitText or equivalent only with accessible natural text and reduced-motion fallback; Three.js/React Three Fiber only for a proven meaningful 3D interaction. Prefer the **smallest effective toolkit** and do not install technologies speculatively.
- Meet WCAG AA, keyboard and touch interaction needs, `prefers-reduced-motion`, LCP/CLS targets, semantic SEO, real medical credibility and fast mobile interactions. Use Playwright and Lighthouse as evidence. Explain design decisions and provide working previews/screenshots for approval.

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
**Start with Phase 1, not an immediate code rewrite:** inspect `docs/AASTHA_2_0_CREATIVE_DEVELOPMENT_BRIEF.md` and `docs/OMNIRUSH_HANDOFF_2026-10-19.md` in full, audit the two existing repositories, review the live concept and CMS staging, verify app dependencies and GitHub Actions, map the current design and user journeys, and report all confirmed QA gaps. Then deliver a bold, medically credible design system and page-by-page interaction concept, plus a reasoned minimal animation toolkit (Phase 2). Seek owner feedback on creative direction before substantial visual implementation. Subsequently implement/test on a **non-Render** feature branch; do not deploy.
