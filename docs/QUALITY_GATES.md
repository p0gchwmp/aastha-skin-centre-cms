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

The first release floor is deliberately a regression-prevention baseline:

| Category or metric | Blocking floor |
|---|---:|
| Performance category | 85 |
| Accessibility category | 95 |
| Best Practices category | 95 |
| SEO category | 95 |
| First Contentful Paint | <= 2.5 s |
| Largest Contentful Paint | <= 3.0 s |
| Cumulative Layout Shift | <= 0.10 |
| Total Blocking Time | <= 300 ms |

The product target remains:

- Performance 95+;
- Accessibility 100;
- Best Practices 100;
- SEO 100;
- LCP <= 2.5 seconds;
- CLS <= 0.10.

Do not lower a blocking threshold merely to make a pull request green. Fix the
regression or document why a metric is currently unstable. Raise thresholds as
reports establish a repeatable higher baseline.

## Evidence

Every workflow run uploads for 30 days:

- mobile Lighthouse reports;
- desktop Lighthouse reports;
- axe JSON results;
- axe Markdown summary;
- screenshots for pages with blocking accessibility violations;
- local server log.

## Local commands

Install the pinned tools used by CI:

```bash
npm install --no-save --no-package-lock \
  @lhci/cli@0.15.1 \
  playwright@1.62.0 \
  @axe-core/playwright@4.12.1
npx playwright install chromium
```

With the Django site running at `http://127.0.0.1:8000`:

```bash
node tools/audit_accessibility.mjs \
  --base-url http://127.0.0.1:8000 \
  --output audit-artifacts/accessibility

LHCI_FORM_FACTOR=mobile npx lhci autorun --config=lighthouserc.cjs
LHCI_FORM_FACTOR=desktop npx lhci autorun --config=lighthouserc.cjs
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
