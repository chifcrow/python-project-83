#!/usr/bin/env bash
set -euo pipefail

# Always run from the directory where this script is located (repo root)
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "Working directory: $(pwd)"
echo "Listing files in repo root:"
ls -la

# Install PostgreSQL client if it's missing (psql is required for schema apply)
if ! command -v psql >/dev/null 2>&1; then
  echo "psql not found, installing postgresql-client..."
  apt-get update
  apt-get install -y --no-install-recommends postgresql-client
fi

# Install project dependencies (creates .venv and installs packages)
make install

# Apply schema to the database
if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL is not set"
  exit 1
fi

SQL_FILE="$SCRIPT_DIR/database.sql"
if [ ! -f "$SQL_FILE" ]; then
  echo "ERROR: SQL file not found at $SQL_FILE"
  exit 1
fi

psql -a -d "$DATABASE_URL" -f "$SQL_FILE"
