from __future__ import annotations
from datetime import datetime
from urllib.parse import urlparse
import psycopg2
import requests
import validators
from bs4 import BeautifulSoup
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
    return (
        render_template("index.html", url_value=url_value, error=error),
        status_code,
    )


def extract_seo_fields(html: str) -> tuple[str | None, str | None, str | None]:
    """
    Extract SEO fields from HTML:
    - h1 text
    - title text
    - meta description content

    Returns: (h1, title, description)
    """
    if not html:
        return None, None, None

    try:
        soup = BeautifulSoup(html, "lxml")

        h1_tag = soup.find("h1")
        h1 = h1_tag.get_text(strip=True) if h1_tag else None

        title_tag = soup.find("title")
        title = title_tag.get_text(strip=True) if title_tag else None

        meta_desc = soup.find("meta", attrs={"name": "description"})
        desc_raw = meta_desc.get("content") if meta_desc else None
        description = desc_raw.strip() if desc_raw else None

        return h1 or None, title or None, description or None
    except Exception:
        return None, None, None


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
            cur.execute(
                "SELECT id FROM urls WHERE name = %s;",
                (normalized,),
            )
            existing = fetch_one(cur)
            if existing:
                flash("URL already exists", "info")
                return redirect(url_for("url_show", id=existing["id"]))

            created_at = datetime.utcnow()
            cur.execute(
                "INSERT INTO urls (name, created_at) "
                "VALUES (%s, %s) "
                "RETURNING id;",
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


@app.post("/urls/<int:id>/checks")
def url_checks_create(id: int):
    try:
        conn = get_db_connection()
    except Exception:
        flash("Database connection error", "danger")
        return redirect(url_for("urls_index"))

    try:
        with conn.cursor() as cur:
            cur.execute(
                "SELECT id, name FROM urls WHERE id = %s;",
                (id,),
            )
            url_row = fetch_one(cur)
            if not url_row:
                flash("URL not found", "danger")
                return redirect(url_for("urls_index"))

            url_name = url_row["name"]

        try:
            response = requests.get(url_name, timeout=5)
            response.raise_for_status()
        except requests.RequestException:
            flash("Произошла ошибка при проверке", "danger")
            return redirect(url_for("url_show", id=id))

        status_code = response.status_code
        h1, title, description = extract_seo_fields(response.text)
        created_at = datetime.utcnow()

        with conn.cursor() as cur:
            cur.execute(
                "INSERT INTO url_checks "
                "(url_id, status_code, h1, title, description, created_at) "
                "VALUES (%s, %s, %s, %s, %s, %s);",
                (id, status_code, h1, title, description, created_at),
            )
            conn.commit()

        flash("URL has been checked", "success")
        return redirect(url_for("url_show", id=id))
    except psycopg2.Error:
        try:
            conn.rollback()
        except Exception:
            pass
        flash("Database error", "danger")
        return redirect(url_for("url_show", id=id))
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
            cur.execute(
                "SELECT "
                "  u.id, "
                "  u.name, "
                "  u.created_at, "
                "  lc.created_at AS last_check, "
                "  lc.status_code AS last_status_code "
                "FROM urls AS u "
                "LEFT JOIN LATERAL ( "
                "  SELECT created_at, status_code "
                "  FROM url_checks "
                "  WHERE url_id = u.id "
                "  ORDER BY id DESC "
                "  LIMIT 1 "
                ") AS lc ON TRUE "
                "ORDER BY u.id DESC;"
            )
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
            cur.execute(
                "SELECT id, name, created_at "
                "FROM urls "
                "WHERE id = %s;",
                (id,),
            )
            url_row = fetch_one(cur)

            if not url_row:
                flash("URL not found", "danger")
                return redirect(url_for("urls_index"))

            cur.execute(
                "SELECT id, status_code, h1, title, description, created_at "
                "FROM url_checks "
                "WHERE url_id = %s "
                "ORDER BY id DESC;",
                (id,),
            )
            checks = fetch_all(cur)

        return render_template("url.html", url=url_row, checks=checks)
    finally:
        conn.close()
