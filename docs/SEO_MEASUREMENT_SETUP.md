# Search and conversion measurement setup

## Safety state

Analytics remains disabled until an administrator adds a valid GA4 Measurement
ID in Wagtail **Settings → Aastha Site Settings → Compliance, SEO and
analytics**. The conversion script exits immediately while analytics is disabled.

The tracking layer never sends patient names, phone numbers, ages, concerns,
notes, OPD numbers or appointment-message content. It records only the action,
page path, branch classification and whether optional date/time choices were
made.

## GA4 events

| Event | Trigger | Parameters |
| --- | --- | --- |
| `contact_click` | Phone or WhatsApp link | `contact_method`, `phone_role`, `clinic_branch`, `page_path` |
| `map_click` | Google Maps link | `clinic_branch`, `page_path` |
| `appointment_cta_click` | Appointment/contact CTA | `clinic_branch`, `page_path` |
| `branch_select` | Branch field selection | `clinic_branch`, `page_path` |
| `generate_lead` | Valid appointment request opens WhatsApp | `lead_source`, `clinic_branch`, `has_preferred_date`, `has_preferred_time`, `page_path` |
| `outbound_profile_click` | Instagram, Facebook, YouTube, Practo or Justdial | `profile_name`, `clinic_branch`, `page_path` |

Mark `generate_lead` as a key event in GA4. Phone, WhatsApp and map actions can
also be marked as key events when the clinic wants a broader assisted-conversion
view.

## Search Console

1. Verify the domain property for `aasthaskincentre.in` through DNS.
2. Verify the URL-prefix property for `https://www.aasthaskincentre.in/`.
3. Submit `https://www.aasthaskincentre.in/sitemap.xml`.
4. Inspect the homepage, doctor page, both clinic pages and priority treatment
   pages after major content updates.
5. Do not request indexing for internal search results, the Render alias or
   pages intentionally marked noindex.

The existing Wagtail `search_console_verification` field can emit a URL-prefix
HTML verification token. Domain-property verification still requires the DNS
TXT record supplied by Google.

## Monthly report

Review:

- organic users and engaged sessions;
- landing-page calls, WhatsApp clicks, map clicks and appointment leads;
- branch selection;
- non-brand versus brand Search Console queries;
- pages with impressions but weak click-through rate;
- pages with traffic but weak conversion actions;
- index coverage and sitemap errors;
- device split and mobile conversion quality;
- medical pages approaching their next review date.

Do not evaluate success from one ranking screenshot. Compare qualified organic
traffic and patient actions over rolling 28-day and 90-day periods.
