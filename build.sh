#!/usr/bin/env bash
# Build script for Render deployment.
# - Installs dependencies
# - Applies database schema to PostgreSQL using DATABASE_URL and database.sql

set -euo pipefail

# Install PostgreSQL client if it's missing (psql is required for schema apply)
if ! command -v psql >/dev/null 2>&1; then
  echo "psql not found, installing postgresql-client..."
  apt-get update
  apt-get install -y --no-install-recommends postgresql-client
fi

# Install project dependencies (creates .venv and installs packages)
make install

# Apply schema to the database
# DATABASE_URL must be provided by the platform (Render) as an environment variable
if [ -z "${DATABASE_URL:-}" ]; then
  echo "ERROR: DATABASE_URL is not set"
  exit 1
fi

psql -a -d "$DATABASE_URL" -f database.sql
