# OmniRush takeover handoff — Aastha website renovation
**Prepared:** 19 October 2026  
**Status:** safe work branch prepared; **production not changed**  
**Read with (the user's creative brief is required, not optional):** `AGENTS.md`, `docs/AASTHA_2_0_CREATIVE_DEVELOPMENT_BRIEF.md`, `EDITORIAL_V37_ROLLOUT.md`, `docs/editorial-v37-cutover.md`, `docs/BACKUP_AND_RECOVERY.md`

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

## 1A. The exact visual preview the owner wants updated

**Confirmed by inspecting Render's live service configuration on 19 Oct 2026:**

| URL | Render service | Source repository | Source branch | Role |
|---|---|---|---|---|
| https://aastha-editorial-concept-preview.onrender.com/ | `aastha-editorial-concept-preview` | `p0gchwmp/aastha-skin-centre` | `concept/editorial-interactive-v1` | **Owner's desired visual design**; separate static Render service |
| https://aastha-editorial-cms-staging.onrender.com/ | `aastha-editorial-cms-staging` | `p0gchwmp/aastha-skin-centre-cms` | `concept/editorial-production-v37` | CMS-integrated staging; noindex |
| https://www.aasthaskincentre.in/ | `aastha-skin-centre-cms` | `p0gchwmp/aastha-skin-centre-cms` | `main` | Real public production website; do not touch until approved |

**Clarification from website owner:** The first URL is the look and experience they have been renovating and want continued, aesthetically enhanced, and kept updated as they review work. Do **not** treat it as the final production application. Its static source is not the Wagtail CMS. The CMS-staging URL is the actual launch candidate.

**Design acceptance and update workflow:**
1. Inspect the owner's exact editorial concept preview as a visual reference and compare its real desktop/mobile layout against the current v37 CMS output: homepage, doctor profile, booking, treatment, blog, both locations and navigation.
2. Carry forward the best components into the CMS **in one maintainable implementation**, including asymmetrical Pinterest-inspired editorial photo boards, elegant crops, thoughtful typography, whitespace, mobile visual rhythm, tasteful transitions, accessible contrast and rich visual browsing paths.
3. Improve with genuinely licensed/original design assets and approved real clinic/Dr Cheena images, never hotlink random Pinterest images, fake clinician images, fake before-and-after outcomes or invented patients.
4. When owner needs a fresh shareable visual preview, produce local/CI screenshot evidence or an isolated preview artifact first. Once Render build capacity is confirmed, update the **actual CMS staging** with a reviewed batch so the owner can review the future live site. If the owner explicitly wants the original static preview URL refreshed too, synchronize the static concept source **as a secondary demo**, not as an independent production codebase.
5. Never confuse a change on the static concept branch with a change on the CMS. These are two repositories and two independently deploying services. Never claim one URL has updated until its Render deployment has succeeded and browser validation confirms the served SHA.
6. Avoid repeated Render pushes: a previous incident exhausted workspace build minutes and sent many failure emails. Neither staging nor production should auto-deploy during exploratory agent work.

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

## 4. First OmniRush mission — Aastha 2.0 five-phase agency workflow

**Creative brief:** `docs/AASTHA_2_0_CREATIVE_DEVELOPMENT_BRIEF.md` is the owner-supplied primary creative direction. Follow its full five-phase sequence. Technical due diligence belongs inside Phase 1; hardening belongs in Phase 5. Preserve the existing QA debt and test it throughout, but do **not** start wholesale visual rewrites or deploy anything before understanding the project.

Work in a *new* `omnirush/<task-name>` branch derived from `handoff/omnirush-2026-10-19`.

### Phase 1 — audit everything before designing

1. Fetch/inspect both `p0gchwmp/aastha-skin-centre` (`concept/editorial-interactive-v1`) and `p0gchwmp/aastha-skin-centre-cms` (production `main`, staging `concept/editorial-production-v37`, and the handoff branch). Inspect actual Git history, assets, dependencies, route/render architecture, stylesheet cascade, image delivery, JavaScript/React islands, and current animations.
2. Inspect `https://aastha-editorial-concept-preview.onrender.com/` visually on desktop and mobile, and the CMS staging and actual production website where accessible. The linked *concept preview* is the owner's reference; the CMS branch is what launches.
3. Study `https://www.allthingsniro.com/` and `https://www.allthingswtf.com/` as inspiration for pacing, expressive typography, choreography and distinctiveness **without copying their style or implementing a soda aesthetic**. If blocked, say exactly which aspects could not be inspected.
4. Map actual homepage, concerns, treatments, doctor profile, location, booking and blog user journeys. Inventory real approved photography versus decorative/stock assets and existing CMS editor functionality.
5. Inspect `.github/workflows/quality-gates.yml`, `tools/audit_accessibility.mjs`, `lighthouserc.cjs`, `tools/summarize_lighthouse.py`, and actual management commands. Review the latest isolated QA runs; separate workflow/config failure from a real site defect.
6. Establish clean **local** CI-parity build with dummy credentials, disposable database, and no Render deployment. Summarize strengths, exact shortcomings and what must be preserved.
7. **Deliver an audit and prioritized creative/engineering opportunity report before broad visual changes.**

### Phase 2 — distinctive creative direction for approval

1. Propose bespoke typography hierarchy, refined warm medical colour system, asymmetrical editorial layouts, Pinterest-style imagery composition using owned/licensed images, whitespace, responsive grid, and doctor/clinic photo treatment.
2. Propose specific interaction beats, not repetitive fade-ins: choreographed homepage opening, intuitive concern explorer, interactive treatment stories, transitions and meaningful feedback. Ensure medical info and booking remain clear and accessible.
3. Choose the **smallest effective animation toolkit**, based on inspected code: consider GSAP and ScrollTrigger for measured, maintainable choreography; Lenis only where integration improves UX; SplitText or an accessible equivalent for expressive headlines; Three.js/R3F only with a justified, lightweight need. Do not install overlapping libraries speculatively.
4. Provide desktop/mobile storyboard, reduced-motion behavior, contrast and performance design constraints, page-by-page renovation sequence and dependency tradeoffs.
5. **Show the owner the direction and seek feedback before substantial homepage implementation.**

### Phase 3 — real CMS-integrated homepage prototype

1. Implement a working homepage prototype in the Wagtail CMS app (not just Figma images or disconnected static HTML) on an isolated `omnirush/*` branch.
2. Include live navigation, real content, working call/WhatsApp/booking, expressive typography, intentional visual storytelling and refined yet usable interactive concern/treatment entry points.
3. Produce desktop/mobile screenshot or recording evidence, accessible reduced-motion and keyboard alternatives, and measurable build/page audit results.
4. Send a reviewable local/CI preview or screenshots; **do not push directly to Render-watched branches** to generate screenshots.

### Phase 4 — renovate all page families

After owner approves homepage direction, extend it across conditions, treatments, doctor, branches, booking/contact, blog/long-tail pages without damaging URLs, SEO/schema, existing CMS editing, actual clinic details or medically reviewed content. Use approved real clinic/doctor photos and licensed/original supplementary visuals. Test route/appointment behavior throughout; no fictional treatment outcomes or case imagery.

### Phase 5 — final full-site engineering and release QA

1. Fix actual WCAG contrast, ARIA, accessible-name and light/dark theme issues, including Karan Nagar address card. Do **not** suppress failing axe rules.
2. Verify homepage/doctor image loading, `srcset`/`sizes`/`width`/`height`, WebP, LCP discoverability, and no duplicated preloads. Optimize real mobile bottlenecks, not just the audit thresholds.
3. Preserve protected rollback suite (`AASTHA_EDITORIAL_V37=0`) and enabled editorial contracts (`AASTHA_EDITORIAL_V37=1`). Historical green runs showed 256 rollback tests and 42 v37 tests, but freshly verify test counts and pass status on the exact final SHA.
4. Require 12/12 WCAG representative desktop/mobile scenarios with **zero blocking AA violations**, full mobile and desktop Lighthouse budgets, SEO audit with zero errors, ~96 native routes and internal-link parity, working appointment/Maps/WhatsApp/call flows, and Wagtail admin access.
5. Record exact commit SHA, commands, audit artifacts, page screenshots, tested URLs and a rollback-ready deployment manifest. Do not claim a green gate unless **that same SHA** passed.
6. Prepare a reviewable PR; **no merge to staging or production until the owner specifically authorizes it**.

### Deployment — separate owner-authorized step (not part of automatic Phase 5)

- Confirm Render build-minute capacity before triggering **one** planned staging deployment.
- Recheck current production deploy/rollback anchor before making assumptions.
- Back up production PostgreSQL and persistent media independently.
- Follow `EDITORIAL_V37_ROLLOUT.md` and `docs/editorial-v37-cutover.md`: promote approved code with `AASTHA_EDITORIAL_V37=0` on production, verify, and enable v37 only after explicit approval.
- Do not change domain/DNS. Audit canonicals, robots, sitemap, schema, redirects, Wagtail admin, branch/location links, analytics, booking and 404/5xx.
- Roll back through the feature flag for presentation incidents; DB restore only for an independent data incident.

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

> Read AGENTS.md, docs/AASTHA_2_0_CREATIVE_DEVELOPMENT_BRIEF.md and docs/OMNIRUSH_HANDOFF_2026-10-19.md completely. Take ownership of Aastha 2.0 as both creative director and senior engineer. Begin with **Phase 1 audit only**: inspect both actual GitHub repos, code, dependencies, existing visual/motion language, current concept preview, CMS staging, production safety, user journeys and QA history. Study NIRO and WTF as creative quality references where accessible. Present the existing architecture, strengths, flaws, preservation rules and a distinctive Aastha 2.0 creative direction, specifying the smallest useful GSAP/ScrollTrigger/Lenis/Three toolkit and explaining tradeoffs. Get the owner's feedback on the creative direction before major implementation. Then prototype a working CMS-integrated homepage; renovate all page families; finally complete the strict CI/Playwright/axe/Lighthouse and SEO gates. Work only in isolated omnirush/* branches. Do not push to Render-watched branches, deploy, alter production, or expose secrets/patient data without express approval.
