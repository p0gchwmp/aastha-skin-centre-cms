# Aastha CMS launch status

Automated parity is complete. The remaining launch checklist is tracked in GitHub issue #9.

## Completed

- 75 legacy routes restored and audited
- Desktop/mobile parity checks passing
- Appointment interaction checks passing
- Static Render service retained for rollback
- Render aliases kept non-indexable

## Before public-domain cutover

- Confirm clinic facts and operational claims
- Verify the deployed release through `/healthz/`
- Complete Wagtail, real-device, backup and restore smoke tests
- Attach the approved custom domain
- Recheck canonicals, robots, schema and sitemap
- Submit the sitemap only after the custom domain is live
