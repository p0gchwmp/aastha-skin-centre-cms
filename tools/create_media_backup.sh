#!/usr/bin/env bash
set -Eeuo pipefail

# Archive Wagtail uploads from Render's persistent media disk.
# Run from a Render shell, then transfer the archive and checksum off Render.
# Optional overrides:
#   MEDIA_ROOT=/var/data/media BACKUP_DIR=/var/data/backups bash tools/create_media_backup.sh

media_root="${MEDIA_ROOT:-/var/data/media}"
backup_dir="${BACKUP_DIR:-/var/data/backups}"

for command in tar sha256sum find; do
  if ! command -v "$command" >/dev/null 2>&1; then
    echo "ERROR: $command is not installed or not on PATH." >&2
    exit 3
  fi
done

if [[ ! -d "$media_root" ]]; then
  echo "ERROR: MEDIA_ROOT does not exist: $media_root" >&2
  exit 2
fi

umask 077
timestamp="$(date -u +%Y%m%dT%H%M%SZ)"
archive="$backup_dir/aastha-media-$timestamp.tar.gz"
manifest="$archive.list"
checksum="$archive.sha256"

mkdir -p "$backup_dir"

echo "Archiving uploaded media from $media_root"
tar -C "$media_root" -czf "$archive" .
tar -tzf "$archive" > "$manifest"
sha256sum "$archive" > "$checksum"

file_count="$(find "$media_root" -type f | wc -l | tr -d ' ')"

if [[ ! -s "$archive" || ! -s "$checksum" ]]; then
  echo "ERROR: Media archive verification failed." >&2
  exit 4
fi

echo "Media archive created and verified."
echo "Files seen: $file_count"
echo "Archive:    $archive"
echo "Manifest:   $manifest"
echo "Checksum:   $checksum"
echo "IMPORTANT: This copy is still on Render. Transfer it to secure offsite storage."
