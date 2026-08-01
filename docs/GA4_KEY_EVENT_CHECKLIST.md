# GA4 `generate_lead` key-event checklist

## What the website already does

- The canonical public website sends the recommended GA4 event `generate_lead`
  only after a valid appointment request opens WhatsApp.
- The event contains only `lead_source`, `clinic_branch`, preferred-date/time
  booleans and `page_path`.
- Patient names, mobile numbers, ages, gender, concerns, notes, OPD details and
  WhatsApp message text are never sent to Analytics.
- The production smoke workflow blocks a release if the GA4 Measurement ID,
  deferred loader, analytics event bundle or privacy allowlist disappears.

## One-time authenticated GA4 action

This action requires **Marketer** access or higher to the Aastha Skin Centre GA4
property.

1. Open the correct Aastha Skin Centre GA4 property.
2. Go to **Admin → Data display → Events**.
3. Search for `generate_lead` in **Recent events**.
4. When it is present, click the star beside it to mark it as a key event.
5. If it has not appeared yet, click **Create event**, enter exactly
   `generate_lead`, enable **Mark as key event**, choose **Create with code**,
   keep the recommended **Once per event** counting method and save.
6. Do not assign a monetary value until the clinic has an approved, documented
   lead-value model.

Marking the event affects future data only; it does not turn historical event
rows into key events.

## Safe verification

1. On `https://www.aasthaskincentre.in/book-appointment/`, complete the form with
   clearly synthetic QA details rather than patient information.
2. Submit until WhatsApp opens. Sending the WhatsApp message is not required.
3. In GA4, open **Reports → Realtime**.
4. Confirm `generate_lead` appears in **Key events by Event name**.
5. Confirm the event parameters contain branch and preference metadata only.
6. Check the processed Events/Key events reports again the following day; normal
   reports can take up to 24 hours to populate.

## Recommended reporting use

Treat `generate_lead` as the primary website lead. Keep calls, WhatsApp clicks,
map clicks and appointment CTA clicks as supporting engagement events unless the
clinic intentionally decides to count assisted actions as additional key events.
