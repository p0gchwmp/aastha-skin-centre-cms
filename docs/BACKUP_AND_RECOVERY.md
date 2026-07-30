# Aastha CMS backup and recovery runbook

This runbook covers the production Wagtail database and uploaded media. It does
not place patient or clinic data in GitHub.

## Production storage map

The Render Blueprint defines two separate data stores:

- PostgreSQL database: `aastha-cms-db`
- Persistent media disk: `aastha-cms-media`, mounted at `/var/data/media`

Both must be recoverable. A database restore does not restore uploaded files,
and a disk restore does not restore Wagtail records.

## Minimum backup policy

| Data | Automatic protection | Portable copy | Restore rehearsal |
|---|---|---|---|
| PostgreSQL | Render point-in-time recovery on the paid database | Weekly and before migrations, imports or bulk edits | Quarterly |
| Uploaded media | Render daily disk snapshots | Monthly and before bulk image replacement | Quarterly |

Download portable copies to encrypted storage controlled by the clinic. Keep at
least one copy outside Render. Never store a database dump, media archive or
connection string in GitHub, email drafts or a public cloud folder.

## Before launch

1. Open the Render database service `aastha-cms-db`.
2. Open **Recovery** and confirm Point-in-Time Recovery is available.
3. Select **Create export** and wait for the logical export to finish.
4. Download the `.dir.tar.gz` export to encrypted clinic-controlled storage.
5. Open the web service `aastha-skin-centre-cms` and then **Disks**.
6. Confirm the `aastha-cms-media` disk is attached at `/var/data/media` and that
   snapshots are visible.
7. Create a portable media archive using the Render shell procedure below.
8. Record the backup time, operator, file names and verification result in the
   backup log at the end of this document.

## Portable PostgreSQL backup from a trusted computer

Install PostgreSQL client tools that match the database major version. Copy the
**external** database URL from Render only when needed and keep it out of shell
history where possible.

```bash
read -s -p "Database URL: " DATABASE_URL
export DATABASE_URL
BACKUP_DIR="$HOME/secure-aastha-backups" \
  bash tools/create_portable_database_backup.sh
unset DATABASE_URL
```

The script creates:

- a custom-format `.dump` file;
- a `pg_restore --list` manifest, proving that PostgreSQL can parse the archive;
- a SHA-256 checksum.

Move all three files to encrypted offsite storage.

## Portable uploaded-media backup from the Render shell

Open the web service shell and run:

```bash
MEDIA_ROOT=/var/data/media \
BACKUP_DIR=/var/data/backups \
  bash tools/create_media_backup.sh
```

The script creates a compressed archive, file manifest and SHA-256 checksum.
The initial copy remains on the same Render disk and is **not** an offsite
backup. Transfer all three files to clinic-controlled encrypted storage, then
remove old temporary archives from `/var/data/backups` after verifying the
offsite copy.

## Recovery decision guide

### One page, snippet or setting was edited incorrectly

Use Wagtail history and revisions first. This is the lowest-risk recovery method
and does not affect unrelated content.

### Database data was deleted or damaged recently

Use Render Point-in-Time Recovery. Restore to a **new database instance**, check
it in isolation, then update `DATABASE_URL` only after validation. Do not delete
the original database until the application is confirmed against the recovery
instance.

### A portable database export is required

Restore only into an empty temporary database:

```bash
createdb aastha_restore_test
pg_restore \
  --dbname="postgresql://localhost/aastha_restore_test" \
  --no-owner \
  --no-privileges \
  --verbose \
  /secure/path/aastha-cms-YYYYMMDDTHHMMSSZ.dump
```

For a Render-generated `.dir.tar.gz` export, extract it first and point
`pg_restore` at the extracted directory.

Never test a restore over the live production database.

### Uploaded media was deleted or corrupted

For recent loss, use the Render disk snapshot interface. A disk snapshot restore
reverts the whole media disk, so files uploaded after the chosen snapshot are
lost. For selective or older recovery, extract the portable media archive into
an empty temporary directory, verify it, and copy only the required files.

## Restore validation checklist

After restoring into a temporary environment:

- `/healthz/` returns `status: ok`;
- Wagtail admin login works;
- expected page, blog, clinic and doctor counts are present;
- the homepage, appointment page and representative clinical pages load;
- uploaded logo, doctor, clinic and article images render;
- internal links, Call, WhatsApp, Maps and appointment submission work;
- database migrations show no pending changes;
- light and dark modes remain readable;
- no production DNS or search-indexing setting points to the temporary restore.

Record the recovery duration and any correction needed. A backup is not proven
until it has been restored successfully at least once.

## Emergency cautions

- Do not run `import_v28_site --reset` against production.
- Do not restore a dump into a non-empty database containing important data.
- Do not expose the external database URL in screenshots, tickets or chat.
- Do not assume a successful archive command guarantees a successful restore.
- Keep the static site online until the CMS domain cutover and rollback window
  are complete.

## Backup log

| UTC date | Operator | Database export | Media archive | Offsite location | Verification / restore result |
|---|---|---|---|---|---|
| | | | | | |
