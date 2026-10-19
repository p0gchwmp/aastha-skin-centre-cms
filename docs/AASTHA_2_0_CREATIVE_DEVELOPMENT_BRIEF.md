# PROJECT: AASTHA 2.0 — Complete Website Renovation

**Owner-supplied creative development brief — 19 October 2026.**

> **Status and authority:** This is the owner's creative brief. Read alongside `AGENTS.md`, `docs/OMNIRUSH_HANDOFF_2026-10-19.md`, and `EDITORIAL_V37_ROLLOUT.md`. The brief describes *what to create*; the other documents define the repository, verified architecture, existing progress, testing, data/clinical guardrails, and mandatory approval before deployment. Never interpret "work autonomously" as authorization to change production or push to Render-watched branches.

You are my **senior creative director, UI/UX designer, frontend engineer, and creative developer**.

I want to transform my existing Aastha Skin Centre website into an exceptional, highly interactive, editorial-style digital experience.

**Current visual website:** https://aastha-editorial-concept-preview.onrender.com/

**Brand:** Aastha Skin Centre  
**Industry:** Dermatology, skin and hair care  
**Location:** Jammu, India

## 1. FIRST — ACCESS MY GITHUB

I have connected my GitHub account to ChatGPT. OmniRush should use its own available GitHub/project access.

Before designing or writing code:

1. Check whether you can access my GitHub repositories.
2. Find the repository containing my existing Aastha Skin Centre website.
3. Inspect the complete project structure, source code, dependencies, existing animations, styling and page architecture.
4. Identify the technology stack and current deployment configuration.
5. Examine the existing Aastha website and understand its content, visual identity and user journeys.
6. Identify what is currently working, what needs improvement and what should be preserved.

If GitHub isn't accessible, tell me precisely what access or repository information you need.

**Important: Do not build a disconnected new website. Renovate my existing project.**

**Already-verified repository distinction for this handoff:** the visual reference is from `p0gchwmp/aastha-skin-centre` on `concept/editorial-interactive-v1`, while the deployable CMS is `p0gchwmp/aastha-skin-centre-cms`. Use `handoff/omnirush-2026-10-19` as the branch to start a new isolated work branch. Do not throw away the CMS architecture to ship the static reference directly.

## 2. CREATIVE VISION

I love the experimental web design of these references:

**NIRO:** https://www.allthingsniro.com/  
**WTFund / WTF:** https://www.allthingswtf.com/

Study their visual language and interaction concepts where accessible.

What inspires me:

- Bold, oversized, expressive typography.
- Unexpected and unconventional page layouts.
- Extremely smooth, cinematic scrolling.
- Unique scroll-triggered animation sequences.
- Playful microinteractions and hover effects.
- Interactive visual storytelling.
- Sophisticated page transitions.
- Premium editorial art direction.
- An immersive experience with memorable moments.

I do **NOT** want a soda website or a clone of NIRO.

I want to translate the same level of creativity into a **trustworthy, premium dermatology clinic website**.

Aastha should feel medically credible, contemporary, artistic, innovative and distinctive.

## 3. DESIGN DIRECTION

Create a cohesive design system specifically for Aastha.

Explore:

- Oversized editorial headlines mixed with refined supporting typography.
- Minimal, premium colours with warmth and intentional contrast.
- Exceptional layout composition and whitespace.
- High-quality skincare and dermatology photography.
- Creative but intuitive navigation.
- Magnetic buttons and subtle interactive elements.
- Smooth section transitions.
- Animated concern and treatment navigation.
- Thoughtful motion that supports the content.

Avoid generic AI-generated landing-page aesthetics, excessive gradients, repetitive cards, unnecessary glassmorphism and animations that make the content difficult to read.

The website must look exceptional on both desktop and mobile.

**Additional previously approved direction:** Pinterest-inspired, thoughtfully art-directed photography/moodboard composition, asymmetrical image-led layouts, warm ivory, burgundy/wine and rose accents, strong cropped portrait photography, understated labels, premium whitespace; use genuine approved clinician/clinic photographs when representing the doctor or clinics and original or properly licensed editorial imagery elsewhere. No hotlinked Pinterest images, generated doctor likenesses, fabricated patient photographs or clinical outcomes.

## 4. REIMAGINE THE EXISTING WEBSITE

Audit all existing pages before deciding what to redesign.

Pay particular attention to:

**Homepage:** Create an unforgettable opening experience with premium typography, engaging storytelling and strong appointment calls to action.

**Skin and hair concerns:** Turn the existing concern explorer into an intuitive, highly interactive experience.

**Treatments:** Present treatment information using visually engaging layouts and carefully controlled animations.

**Doctor profile:** Build an authoritative editorial presentation of the doctor's genuine credentials, experience and approach.

**Clinic locations:** Make finding the Jammu clinic branches and their contact details effortless.

**Appointments:** Improve the visual booking experience while preserving existing functionality and WhatsApp integrations.

Preserve important medical information, SEO metadata, existing URLs, treatment content and essential business details unless changes are explicitly justified.

Do not invent medical claims, credentials, patient reviews, treatment results or before-and-after imagery.

## 5. TECHNICAL IMPLEMENTATION

First determine the existing tech stack. Reuse it wherever sensible.

Consider tools such as GSAP, ScrollTrigger and Three.js only when they meaningfully improve the experience.

Requirements:

- Smooth, responsive interactions.
- Excellent mobile design and touch usability.
- Accessible navigation and controls.
- Reduced-motion support.
- Efficient animation performance.
- Optimized images and loading.
- SEO-friendly page structure.
- Clear appointment and enquiry flows.
- No broken links or regressions.

Prioritize quality, performance and maintainability over unnecessary complexity.

## 6. WORKFLOW

Work in the following order:

**Phase 1 — Existing website audit**

Inspect the GitHub project and published preview. Explain the architecture, design strengths, shortcomings and existing functionality.

**Phase 2 — Creative direction**

Develop a distinctive Aastha 2.0 visual concept, including typography, colours, layout principles, interaction ideas and a page-by-page renovation strategy.

**Phase 3 — Homepage prototype**

Implement an original, highly polished homepage redesign using the actual project. Use realistic content and working interactions rather than static mockups.

**Phase 4 — Full website renovation**

Extend the approved design system across the remaining pages while preserving their functionality.

**Phase 5 — Quality assurance**

Test responsiveness, accessibility, animation smoothness, navigation, forms, links, performance and build integrity.

Do not overwrite the live production website. Work on a separate development branch and provide a reviewable preview where possible.

## 7. HOW I WANT YOU TO COLLABORATE

Act like a serious creative agency and senior engineering team, not a basic website generator.

Take design decisions thoughtfully and explain important trade-offs. Make original creative suggestions rather than blindly copying reference sites.

Use your coding and project tools to do actual implementation work when access is available, not just generate instructions.

**START WITH PHASE 1: Identify my Aastha GitHub repository, inspect the existing codebase, and present the audit and creative direction before making major changes.**

Our goal is to make **Aastha 2.0 feel like an award-worthy creative website that people remember, while still functioning beautifully as a professional dermatology clinic website.**

## 8. ADDITIONAL INSTRUCTIONS — CREATIVE DEVELOPMENT TOOLKIT

I want Aastha 2.0 to achieve the level of creative development, animation quality, responsiveness and interaction polish found in exceptional experimental websites.

Before implementing anything, inspect my existing GitHub project and choose the most suitable tools.

**Prioritize the following technologies where appropriate:**

1. **GSAP** — For premium text animations, cinematic reveals, smooth transitions, and sophisticated microinteractions.
2. **GSAP ScrollTrigger** — For scroll-driven storytelling, pinned sections, horizontal treatment showcases and coordinated animation sequences.
3. **Lenis** — Consider for smooth scrolling, but only if it integrates reliably with the existing stack and ScrollTrigger.
4. **Three.js / React Three Fiber** — Only for specific interactive 3D elements that genuinely enhance the experience. Avoid unnecessary 3D effects.
5. **SplitText or equivalent** — For expressive animated typography while preserving readability and accessibility.
6. **Figma or equivalent design workflow** — For establishing the visual system before substantial implementation, where available.
7. **Playwright** — For testing navigation, responsive behaviour, booking flows and interactive features.
8. **Lighthouse** — For performance, accessibility, SEO and best-practice auditing.

**Development principles:**

- Reuse the existing framework and infrastructure wherever possible.
- Do not introduce overlapping animation libraries without a strong reason.
- Make interactions exceptionally fluid and polished.
- Aim for consistent animation performance, especially on mobile.
- Support reduced-motion preferences.
- Use original creative direction rather than copying reference websites.
- Prioritize readable medical content and easy appointment booking.
- Avoid excessive animations that hurt usability or loading times.
- Work in a separate GitHub branch and preserve the current functioning website.
- Verify all builds and test important user journeys before recommending deployment.

**Crucially:** Don't just produce a conventional landing page with fade-in animations. I want thoughtfully choreographed interactions, remarkable typography, distinctive layouts and memorable creative storytelling.

First, identify which technologies the existing Aastha project already uses. Then propose the **smallest effective toolkit** for achieving this vision, explaining why each dependency is necessary.

My priority is a truly distinctive, premium, production-quality experience — not adding technology for its own sake.

## 9. What OmniRush should deliver at each milestone

These are practical acceptance deliverables interpreting the owner's brief, not permission to deploy.

| Phase | Evidence required | Approval checkpoint |
|---|---|---|
| 1: audit | Both repository maps, Render branch/service mapping, current page inventory, dependencies, existing interactions, strengths/gaps, protected assets, QA failures, benchmark/screenshots | Share audit and creative opportunities before broad redesign |
| 2: art direction | Colour and typography system, motion principles, editorial moodboard, page-by-page interaction narrative, dependency justification, mobile and reduced-motion strategy | Owner approves direction before substantial build |
| 3: homepage | Working CMS-integrated homepage prototype, desktop/mobile interaction recording or screenshots, accessible fallback, measured performance/SEO | Owner reviews prototype |
| 4: full renovation | Reusable design components implemented across CMS pages, content and conversion parity, clear before/after review | Review by page family |
| 5: hardening | Test output, Playwright/axe/Lighthouse evidence, SEO audits, booking/WhatsApp/Maps tests, exact release SHA, staging signoff and rollback manifest | Owner explicitly authorizes any deployment |

**Design interaction acceptance:** motion must be deliberate and narrative-driven (not blanket fading). Use semantic HTML; support keyboard and pointer/touch, ensure reduced-motion alternatives and stop/resume for intrusive animation; avoid scroll-jacking, blocking transitions and inaccessible pinned content. Keep business CTAs findable without watching animations.

**Publishing boundary:** Work only in isolated `omnirush/*` branches off the handoff branch. Do **not** publish changes to either Render-watched branch, alter production infrastructure or expose secrets without the owner's clear approval.
