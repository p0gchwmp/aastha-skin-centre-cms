# Editorial production tooling v38

This production migration uses three specialist tools deliberately rather than loading them everywhere.

## Motion.dev
Runtime role: patient-facing motion and interaction enhancement.
- Pinned version: 13.4.0.
- Loaded only when AASTHA_EDITORIAL_V37 is enabled.
- Used for transform/opacity entrances, scroll-linked parallax, card/control feedback and treatment storytelling.
- Reduced-motion always wins.
- The site remains fully usable if the Motion module cannot load.

## Manus
Workflow role: autonomous QA and research, never a patient-facing dependency.
Use Manus for:
- multi-route browser sweeps across desktop/tablet/mobile;
- screenshot-based visual regression review;
- competitive/moodboard research with source capture;
- content-gap and broken-route audits;
- repetitive QA reports before a release candidate.

Architecture, code review, production merges and final medical/compliance wording remain controlled in the main repository workflow.

## Bklit UI
Staff role: analytics and data visualisation only.
Bklit UI is a React/shadcn chart library. The public site is Django/Wagtail and should not carry a React runtime solely for charts.

Current bridge:
- authenticated /admin/website-insights/ page;
- real CMS inventory only;
- no fabricated traffic or conversion data;
- data contract prepared for traffic, search and booking funnel metrics.

Future direct Bklit island:
1. connect Search Console / analytics / booking-event data;
2. add a small admin-only React build;
3. install Bklit charts through its shadcn registry;
4. render time-series, funnel and content-performance charts only inside the staff area.

## Production rule
Do not add a tool because it is fashionable. Each dependency must improve either patient understanding, staff utility, performance, or QA quality.
