from __future__ import annotations

import os

from dotenv import load_dotenv


def load_env() -> None:
    load_dotenv(override=False)


def get_database_url() -> str | None:
    return os.environ.get("DATABASE_URL")


def get_secret_key() -> str:
    return os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
