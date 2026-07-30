# Exact static-page parity

The public CMS keeps a verified copy of each legacy static page’s complete
`<main>` element in **Snippets → Exact page layouts**.

This preserves the original:

- page-specific hero and illustration;
- headings, sections, lists and content hierarchy;
- cards, clinic panels and sidebars;
- accordions and calls to action;
- appointment form markup and interactions; and
- responsive classes used by the original CSS and JavaScript.

The Wagtail shell still controls metadata, canonical URLs, schema, crawler
settings, search, the header, the footer and global clinic settings. Current
phone numbers, email, WhatsApp URL, consultation fee and follow-up period are
substituted when a page is rendered.

## Editing a parity page

Open **Snippets → Exact page layouts**, choose the public path and edit the
trusted HTML. Disable **Enabled** to make that route use its structured Wagtail
page-builder content instead.

## Rebuilding from the static source

```bash
python tools/build_exact_page_snapshots.py /path/to/static/source
python tools/verify_exact_page_snapshots.py
```

The verifier is also part of the Render build and blocks deployment if a
snapshot loses its main landmark, H1, internal route, referenced asset or
checksum integrity.
