#!/usr/bin/env bash
set -euo pipefail

# Simple SQLite backup script for lostandfound.db
# Usage: ./backup_database.sh

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DB_PATH="$SCRIPT_DIR/lostandfound.db"

if [[ ! -f "$DB_PATH" ]]; then
  echo "Database file not found at: $DB_PATH"
  echo "Nothing to backup. If you are using a different DATABASE_URL, back it up manually."
  exit 1
fi

TIMESTAMP="$(date +%Y%m%d_%H%M%S)"
BACKUP_PATH="$SCRIPT_DIR/lostandfound.db.backup.${TIMESTAMP}"

cp "$DB_PATH" "$BACKUP_PATH"
echo "Backup created: $BACKUP_PATH"
