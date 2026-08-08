# Sitewide UI stability pass — 2026-08-09

This branch addresses recurring presentation defects reported from the live site and confirmed by the post-V6 QA artifacts.

## Confirmed root causes

- `premium-system-v6.css` used `overflow-wrap: anywhere`, allowing pathological word fragmentation when legacy layouts collapsed a content column.
- Clinical treatment/condition layouts could retain legacy rails and multi-column rules below comfortable desktop widths.
- The V6 semantic check pseudo-element contains a mojibake string (`âœ“`) instead of a valid check glyph.
- Global V6 heading rules override footer heading scale, producing oversized footer headings.
- General V6 panel styling overrides the intended burgundy homepage accent card and creates light-mode contrast failures.
- The mobile menu inherits button/card styling from multiple older layers, producing inconsistent filled links and excessive rounding.
- Fixed mobile quick actions did not reserve page-bottom space, so content/footer could sit underneath the bar.
- The logged-in Wagtail userbar could overlap the public Book action on iPhone-sized screens.
- Homepage trust/fact cards were much taller than their content required on phones, and the V6 animated stats repeated facts already shown in the trust row.
- Inline clinical-result gallery styles retain rounded/light surfaces that can break the dark editorial theme.
- Directory category headings were measured at 41px in the 390px Chromium audit, exceeding the existing mobile QA limit.
- V6 gold text failed WCAG AA contrast on several light surfaces; the homepage accent card, article CTA copy and small booking CTA also had confirmed contrast failures.

## Corrective scope

The first pass is CSS-only and intentionally isolated on a branch. It:

- protects article width and disables desktop reading rails below 1181px;
- restores normal word wrapping;
- replaces broken boxed list glyphs with a clean semantic check;
- normalizes footer typography;
- tightens homepage facts and removes duplicated animated counters;
- makes the mobile navigation a consistent editorial drawer;
- reserves safe space for the mobile action bar and moves Wagtail controls above it;
- reduces oversized mobile location artwork;
- normalizes FAQ presentation;
- forces clinical result galleries to inherit the active theme;
- uses an AA-safe light-mode accent colour and restores intended accent-card colours;
- reduces directory heading scale on mobile;
- keeps card geometry architectural (2px) across the affected components.

## Deployment safety

No production merge or Render deployment should occur until the branch is visually reviewed. The heavy mobile and Lighthouse workflows are configured for `main`/manual execution, so branch iteration does not intentionally consume those workflows.
