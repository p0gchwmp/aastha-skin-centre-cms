#!/usr/bin/env bash
set -Eeuo pipefail

# Create a portable PostgreSQL custom-format dump without printing credentials.
# Usage:
#   DATABASE_URL='postgresql://...' bash tools/create_portable_database_backup.sh
# Optional:
#   BACKUP_DIR=/secure/offsite/path DATABASE_URL='...' bash tools/create_portable_database_backup.sh

if [[ -z "${DATABASE_URL:-}" ]]; then
  echo "ERROR: DATABASE_URL is required." >&2
  exit 2
fi

for command in pg_dump pg_restore sha256sum; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "ERROR: $command is not installed or not on PATH." >&2
    exit 3
  fi
done

umask 077
backup_dir="${BACKUP_DIR:-backups/database}"
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
backup_file="$backup_dir/aastha-cms-$timestamp.dump"
manifest_file="$backup_file.list"
checksum_file="$backup_file.sha256"

mkdir -p "$backup_dir"

echo "Creating PostgreSQL backup at $backup_file"
pg_dump \
  --format=custom \
  --no-owner \
  --no-privileges \
  --file="$backup_file" \
  "$DATABASE_URL"

# pg_restore --list parses the archive and fails when the dump is unreadable.
pg_restore --list "$backup_file" > "$manifest_file"
sha256sum "$backup_file" > "$checksum_file"

if [[ ! -s "$backup_file" || ! -s "$manifest_file" || ! -s "$checksum_file" ]]; then
  echo "ERROR: Backup verification files were not created correctly." >&2
  exit 4
fi

echo "Backup created and structurally verified."
echo "Archive:   $backup_file"
echo "Manifest:  $manifest_file"
echo "Checksum:  $checksum_file"
echo "Store these files outside Render and test restoration into an empty database."
