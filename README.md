# Aastha Skin Centre CMS v28

See `RELEASE_NOTES_V28.md` for the imported-content, editor and QA totals.

This is the editable successor to the static website. It imports the verified
v28 content into a Wagtail 7.4 LTS control centre while preserving the public
URLs.

## What the administrator can change without code

- Every page title, introduction, section and SEO field
- Section order by drag and drop
- Width, colour theme, alignment, spacing, anchor and mobile/desktop visibility
- Images, galleries, videos and image/video carousels
- Internal page links that survive page moves and URL changes
- External links plus global Call, WhatsApp and Email actions
- Consultation fee, follow-up period, phones, email, branding, navigation,
  announcement banner, disclaimer, analytics and social links from one screen
- Blog posts, treatments, conditions and ordinary static pages
- Doctors, clinics and reusable site-wide sections
- Drafts, previews, scheduled publishing, moderation, revisions and rollback
- Per-page medical-review status, reviewer, review date and next-review date
- Redirects when a page URL changes

The imported starter site contains 77 public pages, including 52 clinical pages
and 10 dedicated blog guides.

## Local Windows preview

Run these files in order:

```text
30_Verify_CMS_v28.bat
32_Create_Local_Admin_v28.bat
31_Preview_CMS_v28.bat
```

Then open:

- Public site: `http://localhost:8000`
- Control centre: `http://localhost:8000/admin/`

The verification script uses its own disposable database. The preview uses
`db.sqlite3`, which is ignored by Git.

## Render deployment

This CMS is a dynamic application. It cannot save edits on the existing Render
Static Site.

Keep the current static staging service online, then create a separate Render
Blueprint from this repository and test the CMS before switching the domain.
The included `render.yaml` creates:

- A paid Starter Python web service
- A paid Basic PostgreSQL database in Singapore
- A 1 GB persistent media disk
- An HTTP database health check
- Staging search-engine protection

During Blueprint creation, Render prompts for:

```text
DJANGO_SUPERUSER_USERNAME
DJANGO_SUPERUSER_EMAIL
DJANGO_SUPERUSER_PASSWORD
```

Use a unique password and do not commit it. The first build imports v28 only
when the database is empty; later deploys never overwrite admin edits.

After deployment:

1. Open `/admin/` and sign in.
2. Confirm 77 pages, 10 blog posts, 2 clinics and Dr. Cheena's profile.
3. Test edits, previews, drafts, image upload and rollback.
4. Keep the `onrender.com` staging URL private from search engines.
5. Add the production domain only after content and medical acceptance.
6. Set `SITE_HOSTNAME` and `WAGTAILADMIN_BASE_URL` to the production host, then
   redeploy.
7. Verify HTTPS, sitemap, canonical URLs, robots, calls, WhatsApp and forms.

Read [ADMIN_GUIDE.md](ADMIN_GUIDE.md) before editing and
[docs/BACKUP_AND_RECOVERY.md](docs/BACKUP_AND_RECOVERY.md) before launch or any
bulk content operation.

## Safe operating notes

- Never commit `.env`, passwords, `db.sqlite3`, `media/`, `staticfiles/` or backup
  archives.
- Back up the database and uploaded media before a major redesign or bulk edit.
- Uploaded media requires persistent or cloud storage; an ephemeral web service
  will lose uploads on restart.
- Use the internal page chooser for links to this website.
- Prefer the visual blocks. “Advanced HTML” is for trusted administrators only.
- Clinical claims and new articles should remain in Medical review required
  until approved by Dr. Cheena.
