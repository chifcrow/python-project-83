"""
Database helpers for PostgreSQL (psycopg2).

This module:
- Reads DATABASE_URL from environment (optionally via .env)
- Creates connections
- Can apply the schema from database.sql (simple manual "migration")
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

import psycopg2
from psycopg2.extensions import connection as PgConnection

from page_analyzer.config import get_database_url, load_env


def get_db_connection() -> PgConnection:
    """
    Create and return a new PostgreSQL connection using DATABASE_URL.
    """
    load_env()
    database_url = get_database_url()
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set")

    return psycopg2.connect(database_url)


def init_db(sql_path: str | None = None) -> None:
    """
    Apply SQL schema from database.sql to the configured database.

    Note:
    - This is a simple approach for the educational project.
    - For production systems, use migrations tooling.
    """
    load_env()

    if sql_path is None:
        project_root = Path(__file__).resolve().parents[1]
        sql_path = str(project_root / "database.sql")

    sql_file = Path(sql_path)
    if not sql_file.exists():
        raise FileNotFoundError(f"SQL file not found: {sql_file}")

    schema_sql = sql_file.read_text(encoding="utf-8").strip()
    if not schema_sql:
        return

    conn = get_db_connection()
    try:
        with conn.cursor() as cur:
            cur.execute(schema_sql)
        conn.commit()
    finally:
        conn.close()


def fetch_one(cur: Any) -> dict[str, Any] | None:
    """
    Fetch one row from a cursor and map it to a dict using column names.
    """
    row = cur.fetchone()
    if row is None:
        return None
    columns = [desc[0] for desc in cur.description]
    return dict(zip(columns, row))


def fetch_all(cur: Any) -> list[dict[str, Any]]:
    """
    Fetch all rows from a cursor and map them to a list of dicts.
    """
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    return [dict(zip(columns, row)) for row in rows]
