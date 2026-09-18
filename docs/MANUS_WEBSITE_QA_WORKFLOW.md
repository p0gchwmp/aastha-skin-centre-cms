# Manus website QA workflow

Manus is a development/QA agent in this project, not a public-site runtime dependency.

## When to run it

Run this brief against the CMS staging service before any production cutover and after large batches of page/template changes.

Staging target:

- https://aastha-editorial-cms-staging.onrender.com
- production domain is never the test target until the final approved cutover.

## Required audit

1. Crawl the public navigation from the homepage through Concerns, Treatments, Doctor, Clinics, Journal, Contact and Booking.
2. Test representative clinical pages from each family:
   - acne / acne scars
   - pigmentation / melasma
   - hair fall / hair transplant
   - fungal / inflammatory medical dermatology
   - laser hair reduction
   - injectables / selected aesthetic pages
3. Check desktop, tablet and mobile layouts for:
   - hidden or overlapping content
   - blank reserved sections
   - horizontal overflow
   - text below readable size
   - broken image crops
   - duplicate navigation or CTAs
   - interactions that cannot be used by touch or keyboard
4. Follow every primary CTA and report:
   - broken URLs
   - legacy/static-preview exits
   - wrong anchors
   - booking paths that lose context
5. Review imagery for relevance:
   - use real Aastha/approved clinical media before generic stock
   - never invent doctor, patient, result or equipment photography
6. Review copy for clarity and restraint:
   - remove prototype/design-process language
   - flag generic sophistication filler
   - flag repeated copy that adds no patient value
   - do not rewrite medical claims autonomously
7. Check performance symptoms:
   - long main-thread stalls
   - janky scroll/drag interactions
   - layout shift
   - oversized media
   - motion that ignores reduced-motion preference
8. Return issues grouped as:
   - P0: blocks launch or risks patient/SEO/admin integrity
   - P1: important utility/layout issue
   - P2: visual polish
   - P3: optional enhancement

## Medical-content guardrail

Manus may flag unclear, duplicated or unsupported medical wording but must not create or strengthen clinical efficacy claims. Changes to diagnoses, treatment indications, risks, contraindications, expected results, or comparative claims require review against the verified CMS source material.

## Output

Return a concise report with:
- route
- viewport/device
- screenshot or clear reproduction steps
- severity
- observed issue
- suggested fix
- whether it is visual, functional, SEO, content or performance

The implementation agent should fix P0/P1 items first and rerun the same routes before production cutover.
