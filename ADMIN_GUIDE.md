# Aastha website control centre — plain-English guide

## The four places you will use

1. **Pages** — homepage, blog posts, treatments, conditions, contact and legal
   pages.
2. **Images** — logo, doctor photo, clinic photos and content images.
3. **Snippets** — doctors, clinic locations and reusable sections.
4. **Settings → Aastha website settings** — facts that must update everywhere.

The dashboard links directly to each area.

## Change the consultation fee everywhere

1. Open **Settings → Aastha website settings**.
2. Open **Global fees and policy**.
3. Change **Consultation fee**.
4. Confirm the follow-up days and fee note.
5. Save.

Pricing blocks marked **Use global consultation fee**, the consultation
sidebar, header and imported fee references update together.

The same screen controls the main phones, WhatsApp, email, logo, favicon,
default social image, navigation, announcement, disclaimer and analytics.

## Edit a page

1. Open **Pages**.
2. Browse to the page and select **Edit**.
3. Change the title, introduction or hero.
4. In **Body**, select a section to edit it.
5. Drag the section handle to change its position.
6. Open **Layout and position** inside a section to set:
   - reading width;
   - colour theme;
   - left, centre or right alignment;
   - space above and below;
   - an optional anchor name;
   - mobile-only or desktop-only visibility.
7. Use **Preview**.
8. Save a draft, submit for moderation or publish.

## Add a blog article

1. Open **Pages → Blog**.
2. Select **Add child page**.
3. Choose **Blog page**.
4. Add the title, publication date, author, reading time and summary.
5. Build the article with text, image, gallery, video, FAQ, related-pages and
   CTA sections.
6. Add an SEO title, search description and social image under **Promote**.
7. Set the medical-review status and reviewer.
8. Preview on mobile and desktop, then submit or publish.

The Blog directory adds the new article automatically. It does not need a
manually created card.

## Add a treatment or condition

- Under **Treatments**, choose **Treatment page**.
- Under **Conditions**, choose **Condition page**.

Use a short URL slug, a patient-friendly introduction, complete FAQs, a related
pages section and the shared clinic/disclaimer switches. The parent directory
adds the page automatically.

For About, Contact, policy or another ordinary page, add a **Standard page**
under Home or a suitable directory.

## Connect text to another page

For a text link:

1. Highlight the words in the rich-text editor.
2. Select the link button.
3. Choose the internal page.

For a button or card:

1. Open its **Link** field.
2. Choose exactly one destination:
   - **Global action** for clinic Call, WhatsApp or Email;
   - **Page** for an internal website page;
   - **External URL** for another website.

Do not paste this site's URL into External URL. An internal page link follows
the page if it moves and Wagtail creates redirects when URLs change.

## Replace a placeholder image

1. Upload the approved original in **Images**.
2. Add or open an **Image** block.
3. Choose the image and add useful alternative text.
4. Choose landscape, square, portrait or original crop.
5. Set the layout and preview.

You can also set the site logo, favicon and default sharing image in Settings;
doctor photos in the Doctor snippet; and clinic photos in each Clinic snippet.

## Add video or a carousel

- Add a **Video** block and paste a supported YouTube or Vimeo URL.
- Add a **Carousel**, then add image or video slides and drag them into order.
- Autoplay is optional. Leave it off unless it materially helps the page.
- Every meaningful image needs alternative text; every video needs a clear
  heading or caption.

## Doctors, clinics and reusable sections

Open **Snippets**.

- **Doctors** stores credentials, role, photo, biography, interests and contact.
- **Clinic locations** stores address, map, phones, reception hours, doctor
  hours, procedure hours, directions and image.
- **Reusable sections** holds content used on several pages. Edit once to
  update every page using that snippet.

Doctors, clinics and reusable sections have drafts, publishing, revision
history and locking. Publish snippet changes only after checking every page
that uses them.

## Global values inside text

Most editors can use the Pricing block and Global action links without seeing
tokens. For exceptional text, these safe tokens are available:

```text
{{ consultation_fee }}
{{ follow_up_days }}
{{ primary_phone }}
{{ secondary_phone }}
{{ whatsapp_phone }}
{{ whatsapp_url }}
{{ email }}
{{ clinic_name }}
{{ clinic_short_name }}
```

They are replaced when the public page renders. Do not alter the spelling or
braces.

## Medical review and publishing

Every clinical page and blog article has:

- review status;
- reviewed by;
- medical review date;
- next review date.

Recommended workflow:

1. Editor saves a draft.
2. Editor previews desktop and mobile.
3. Editor submits for moderation.
4. Dr. Cheena or a Moderator checks claims, suitability, risks, recovery,
   timings, fee and destinations.
5. Moderator publishes.

Editing a revision already in moderation requires reapproval. Page history can
compare or restore older versions.

## Users and permissions

- **Editors** can prepare content and submit it.
- **Moderators** can review and publish.
- **Administrators** manage users, settings and advanced configuration.

Give each person their own account. Never share the main administrator password.
Use the smallest role they need.

## Before publishing any change

- Preview desktop and mobile.
- Check light and dark themes.
- Check headings, spacing, cards, FAQs and long addresses.
- Test every new internal link.
- Test Call, WhatsApp, Email, maps and appointment actions.
- Add SEO title, search description and social image.
- Confirm the page is not marked `noindex` unless intentionally hidden.
- Confirm the medical-review fields.

## Recovery

- Use **History** on a page or revision-enabled snippet to compare or restore.
- Use **Redirects** if an old external URL needs a new destination.
- Restore infrastructure backups only for major data loss; they affect more
  than one page.
- Do not run `import_v28_site --reset` on a populated production database.
