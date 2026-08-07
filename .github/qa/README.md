# Preview QA checkpoints

Normal design commits should not run the full browser suites.

Touch only the matching trigger when evidence is intentionally needed:

- `run-preview` — light/dark screenshot capture
- `run-mobile` — Chromium + WebKit mobile audit
- `run-quality` — Lighthouse + accessibility
- `run-parity` — full prelaunch parity suite

This keeps GitHub Actions usage low while preserving full QA at deliberate checkpoints.
