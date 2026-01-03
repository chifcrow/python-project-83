from __future__ import annotations
from datetime import datetime
from urllib.parse import urlparse

import psycopg2
import validators
from flask import Flask, flash, redirect, render_template, request, url_for

from page_analyzer.config import get_database_url, get_secret_key, load_env
from page_analyzer.db import fetch_all, fetch_one, get_db_connection, init_db

load_env()

app = Flask(__name__)
app.config["SECRET_KEY"] = get_secret_key()
app.config["DATABASE_URL"] = get_database_url()

try:
    init_db()
except Exception:
    pass


def normalize_url(raw_url: str) -> str:
    parsed = urlparse(raw_url)
    scheme = (parsed.scheme or "").lower()
    netloc = (parsed.netloc or "").lower()
    return f"{scheme}://{netloc}"


def is_valid_url(raw_url: str) -> bool:
    if not raw_url:
        return False
    if len(raw_url) > 255:
        return False
    if not validators.url(raw_url):
        return False
    parsed = urlparse(raw_url)
    return bool(parsed.scheme and parsed.netloc)


def render_index(url_value: str, error: str | None, status_code: int = 200):
    return render_template(
        "index.html", url_value=url_value, error=error), status_code


@app.get("/")
def index():
    return render_index("", None)


@app.post("/urls")
def urls_create():
    url_value = request.form.get("url", "").strip()

    if not is_valid_url(url_value):
        flash("Invalid URL", "danger")
        return render_index(url_value, "Invalid URL", 422)

    normalized = normalize_url(url_value)

    try:
        conn = get_db_connection()
    except Exception:
        flash("Database connection error", "danger")
        return render_index(url_value, "Database connection error", 500)

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id FROM urls WHERE name = %s;", (normalized,))
            existing = fetch_one(cur)
            if existing:
                flash("URL already exists", "info")
                return redirect(url_for("url_show", id=existing["id"]))

            created_at = datetime.utcnow()
            cur.execute(
                "INSERT INTO urls (name, created_at) VALUES (%s, %s) RETURNING id;",
                (normalized, created_at),
            )
            new_row = fetch_one(cur)
            conn.commit()

        flash("URL has been added", "success")
        return redirect(url_for("url_show", id=new_row["id"]))
    except psycopg2.Error:
        try:
            conn.rollback()
        except Exception:
            pass
        flash("Database error", "danger")
        return render_index(url_value, "Database error", 500)
    finally:
        conn.close()


@app.get("/urls")
def urls_index():
    try:
        conn = get_db_connection()
    except Exception:
        flash("Database connection error", "danger")
        return render_template("urls.html", urls=[]), 500

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, created_at FROM urls ORDER BY id DESC;")
            urls = fetch_all(cur)
        return render_template("urls.html", urls=urls)
    finally:
        conn.close()


@app.get("/urls/<int:id>")
def url_show(id: int):
    try:
        conn = get_db_connection()
    except Exception:
        flash("Database connection error", "danger")
        return redirect(url_for("urls_index"))

    try:
        with conn.cursor() as cur:
            cur.execute("SELECT id, name, created_at FROM urls WHERE id = %s;", (id,))
            url_row = fetch_one(cur)

        if not url_row:
            flash("URL not found", "danger")
            return redirect(url_for("urls_index"))

        return render_template("url.html", url=url_row)
    finally:
        conn.close()
