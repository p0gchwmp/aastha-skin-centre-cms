# Third-party UI / motion notices

The Editorial v37 production migration intentionally uses third-party libraries only in scoped enhancement layers.

## Motion

- Project: Motion
- Website: https://motion.dev/
- Package: `motion` pinned in `frontend/package.json`
- Use: public editorial motion and React-island animation primitives.
- Runtime is bundled into Aastha static assets for production; no third-party CDN is required.

## Kokonut UI

- Project: Kokonut UI
- Source: https://github.com/kokonut-labs/kokonutui
- License: MIT (component source)
- Adapted component: Action Search Bar interaction model.
- Use: lazy-loaded patient-facing Explore / command search.
- Aastha routes, styling, accessibility behavior and content are project-specific.

## Bklit UI

- Project: Bklit UI
- Source: https://github.com/bklit/bklit-ui
- License: MIT for the chart component source used as reference.
- Adapted component: ring-chart composition.
- Use: authenticated Wagtail Website Insights only.
- Only real CMS inventory is visualized; traffic/conversion data remains absent until a verified analytics source is connected.

## Manus

Manus is not distributed with the website. It is an external development / QA workflow tool. See `docs/MANUS_WEBSITE_QA_WORKFLOW.md`.
