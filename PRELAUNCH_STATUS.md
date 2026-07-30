# Aastha website pre-launch status

This file records the release gates for replacing the retained static Render service with the Wagtail CMS.

## Automated gates

The `Prelaunch parity QA` workflow now checks:

- all 75 legacy routes against the retained static reference;
- complete `main#main-content` markup, H1 and heading hierarchy;
- disclosure/accordion and form structure;
- titles, descriptions, canonicals, robots directives and JSON-LD validity;
- every discovered internal page and asset destination;
- full-page screenshots at 1440 px desktop and 390 px mobile widths;
- mobile navigation, theme switching and one WhatsApp appointment submission;
- Django system checks, migrations, snapshot validation and the full test suite.

## Safety rules

- Temporary `*.onrender.com` hosts must always return `noindex,nofollow`.
- Only the final clinic custom domain may become indexable.
- The retained static service remains active until the deployed CMS audit passes and the custom-domain launch is verified.
- Experience and medical credential claims are page-reviewed content; global settings must not rewrite them.
- Clinic facts controlled globally are limited to approved operational details such as fee, follow-up period, phone, WhatsApp and email.

## Manual launch gates

The technical parity result does not replace clinic sign-off. Before domain cutover, confirm:

1. Dr. Cheena Langer's approved qualifications, registration details and experience wording.
2. Both clinic addresses, PIN codes, map links, phone routing, doctor timings, reception timings and procedure timings.
3. Consultation fee and follow-up policy.
4. Treatments actually offered at each branch and the exact approved device/machine names.
5. Patient-consented photographs, before-and-after media, testimonials and image alt text.
6. Privacy policy, medical disclaimer, contact/appointment wording and analytics consent requirements.
7. Final domain, redirects, Search Console, sitemap submission, Google Business Profile links and analytics measurement.

## Cutover rule

Keep the static service as rollback protection during launch. It can be suspended only after the custom domain serves the CMS correctly, redirects and canonicals are confirmed, forms and calls are re-tested, Search Console sees the sitemap, and several days of error monitoring show no regression.