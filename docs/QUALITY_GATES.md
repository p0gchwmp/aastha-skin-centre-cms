# Lighthouse and accessibility quality gates

This repository has two complementary frontend-quality systems:

1. The existing all-route audits protect structure, interactions, mobile layout,
   dark-mode readability, image delivery and practical performance budgets.
2. The Lighthouse and axe workflow audits representative page types against
   standardised browser scoring and WCAG rules.

Neither system replaces the other. Lighthouse samples representative pages;
the existing Playwright audits continue to cover all public routes.

## Representative pages

The gate covers:

- homepage;
- appointment page;
- doctor profile;
- clinic location;
- a photograph-heavy treatment page;
- blog index.

Axe runs each page in desktop light mode and mobile dark mode. Lighthouse runs
all representative pages once in mobile mode and once in desktop mode.

## Blocking accessibility standard

The axe gate fails on violations tagged as:

- WCAG 2.0 A or AA;
- WCAG 2.1 A or AA;
- WCAG 2.2 AA.

Best-practice findings that are not tied to those WCAG levels are retained in
the report as advisory findings. Rules are not silently disabled. Any future
exception must be documented with its affected route, reason, owner and removal
date.

## Lighthouse release floor

The measured production-like baseline supports the intended category target as
a blocking release floor:

| Category or metric | Blocking floor |
|---|---:|
| Performance category | 95 |
| Accessibility category | 100 |
| Best Practices category | 100 |
| SEO category | 100 |
| First Contentful Paint | <= 2.5 s |
| Largest Contentful Paint | <= 2.5 s |
| Cumulative Layout Shift | <= 0.10 |
| Total Blocking Time | <= 300 ms |
| Responsive image delivery | Required |

The photograph-heavy treatment route is intentionally part of this gate. Its
first clinical photograph must use width candidates and a truthful `sizes`
attribute so a mobile browser does not download the 1200-pixel source for a
roughly 360-pixel display slot.

Do not lower a blocking threshold merely to make a pull request green. Fix the
regression or document why a metric is currently unstable.

## Responsive clinical photographs

The 44 approved 1200-pixel WebP files remain the committed, durable source
assets. During every production and quality build,
`tools/generate_responsive_clinical_images.py` creates 384-pixel, 640-pixel and
768-pixel WebP candidates beside them before `collectstatic` runs.

Public markup then provides:

- `srcset` candidates at 384, 640, 768 and 1200 pixels;
- route-appropriate `sizes` values based on the measured hero slot;
- eager, high-priority loading only for the visible hero photograph;
- `data-src`, `data-srcset` and `data-sizes` for hidden carousel slides so they
  remain unfetched until selected.

`tools/audit_clinical_result_images.py` validates all 44 sources and 132
generated variants. It fails when a candidate is missing, has the wrong width,
is not a valid WebP or is not smaller than its source. Generated candidates are
build artifacts and are not edited manually.

## Responsive visual cues

The decorative dermatology cue system generates 64, 128, 256 and 512-pixel
transparent WebP candidates. The 64-pixel candidate serves the 42–54-pixel
slots on standard-density screens, while higher-density displays can select the
128-pixel or larger candidates. This keeps the global responsive-image audit
strict without reducing visual fidelity.

## Evidence

Every workflow run uploads for 30 days:

- mobile Lighthouse reports;
- desktop Lighthouse reports;
- a Markdown Lighthouse scorecard;
- axe JSON results;
- axe Markdown summary;
- responsive clinical-image generation and validation reports;
- screenshots for pages with blocking accessibility violations;
- local server log.

The GitHub Actions job summary shows the full route-by-route category and metric
table without requiring an artifact download.

## Local commands

Install the pinned tools used by CI:

```bash
npm install --no-save --no-package-lock \
  @lhci/cli@0.15.1 \
  playwright@1.62.0 \
  @axe-core/playwright@4.12.1
npx playwright install chromium
```

Run the same production-like asset build before auditing:

```bash
python tools/build_visual_cue_assets.py
python tools/generate_responsive_clinical_images.py
python tools/audit_clinical_result_images.py
python tools/verify_exact_page_snapshots.py
python manage.py collectstatic --no-input
```

With the Django site running at `http://127.0.0.1:8000`:

```bash
node tools/audit_accessibility.mjs \
  --base-url http://127.0.0.1:8000 \
  --output audit-artifacts/accessibility

LHCI_FORM_FACTOR=mobile npx lhci autorun --config=lighthouserc.cjs
LHCI_FORM_FACTOR=desktop npx lhci autorun --config=lighthouserc.cjs

python tools/summarize_lighthouse.py \
  --root audit-artifacts \
  --output audit-artifacts/lighthouse-summary.md
```

## Interpreting failures

- Fix accessibility failures before visual polish.
- Treat category-score drops as symptoms; inspect the individual failed audits.
- Confirm that a performance failure reproduces across more than one run before
  making a major architectural change.
- Never remove content, medical safety copy or accessible labels merely to
  improve a synthetic score.
- Field Core Web Vitals from Search Console remain the production source of
  truth once sufficient real-user data exists.
