# Search and conversion measurement setup

## Current technical state

The canonical website is technically ready for Google Search Console and GA4:

- a GA4 Measurement ID is configured in Wagtail;
- analytics runs only on the canonical public domain and outside preview mode;
- the external GA4 library loads after rendering or on first interaction;
- a Google URL-prefix verification meta token is present;
- the canonical XML sitemap and public robots declaration are live;
- `generate_lead` is emitted after a valid appointment request opens WhatsApp;
- analytics events exclude patient-identifying and clinical form data.

The live-domain workflow runs `tools/audit_google_measurement_readiness.py` and
blocks deployment verification if any of those public signals disappears. The
audit masks the verification token and Measurement ID in its evidence output.

## What automation cannot prove

Repository and public-site audits cannot access the authenticated Google
accounts. The following account-side states must be confirmed by an authorised
user:

- the Search Console domain property is verified through DNS;
- the URL-prefix property is verified;
- the sitemap appears as **Success** in Search Console;
- `generate_lead` is starred as a GA4 key event;
- the clinic team has the correct Google account roles.

## GA4 events

| Event | Trigger | Parameters |
| --- | --- | --- |
| `contact_click` | Phone or WhatsApp link | `contact_method`, `phone_role`, `clinic_branch`, `page_path` |
| `map_click` | Google Maps link | `clinic_branch`, `page_path` |
| `appointment_cta_click` | Appointment/contact CTA | `clinic_branch`, `page_path` |
| `branch_select` | Branch field selection | `clinic_branch`, `page_path` |
| `generate_lead` | Valid appointment request opens WhatsApp | `lead_source`, `clinic_branch`, `has_preferred_date`, `has_preferred_time`, `page_path` |
| `outbound_profile_click` | Instagram, Facebook, YouTube, Practo or Justdial | `profile_name`, `clinic_branch`, `page_path` |

Use `generate_lead` as the primary key event. Phone, WhatsApp and map actions
should remain supporting events unless the clinic deliberately adopts a broader
assisted-conversion definition. Follow `docs/GA4_KEY_EVENT_CHECKLIST.md` for the
one-time GA4 activation and safe verification sequence.

## Search Console one-time setup

### Domain property

1. Add the domain property `aasthaskincentre.in`.
2. Copy Google's DNS TXT verification record.
3. Add it at the DNS provider without deleting existing SPF, DKIM or other TXT
   records.
4. Return to Search Console and click **Verify**.

A domain property covers HTTP/HTTPS and all subdomains. DNS verification cannot
be replaced by the website's HTML meta token.

### URL-prefix property

1. Add `https://www.aasthaskincentre.in/` exactly.
2. Choose **HTML tag** verification.
3. The Wagtail `search_console_verification` field already emits the required
   meta token on the canonical site.
4. Click **Verify** and leave the token published permanently.

### Submit and monitor the sitemap

1. Select the canonical property in Search Console.
2. Open **Indexing → Sitemaps**.
3. Submit `sitemap.xml`.
4. Confirm the resolved URL is
   `https://www.aasthaskincentre.in/sitemap.xml`.
5. Confirm the status becomes **Success**.
6. Use the sitemap filter in the Page indexing report to monitor indexed URLs.

Do not submit the Render alias, internal search results or pages intentionally
marked `noindex`.

## Priority URL inspection

After the properties and sitemap are confirmed, inspect and request indexing for
only the highest-priority canonical pages:

- homepage;
- Dr. Cheena Langer profile;
- Karan Nagar clinic page;
- Paloura clinic page;
- acne treatment;
- acne-scar treatment;
- laser hair reduction;
- hair-loss treatment;
- melasma/pigmentation treatment;
- book-appointment page.

Use the sitemap for bulk discovery rather than requesting every URL manually.

## Monthly report

Review:

- organic users and engaged sessions;
- landing-page calls, WhatsApp clicks, map clicks and appointment leads;
- `generate_lead` count and session key-event rate;
- branch selection;
- non-brand versus brand Search Console queries;
- pages with impressions but weak click-through rate;
- pages with traffic but weak conversion actions;
- index coverage and sitemap errors;
- device split and mobile conversion quality;
- medical pages approaching their next review date.

Do not evaluate success from one ranking screenshot. Compare qualified organic
traffic and patient actions over rolling 28-day and 90-day periods.
