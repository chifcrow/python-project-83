from __future__ import annotations
import os
from dotenv import load_dotenv


def load_env() -> None:
    """
    Load variables from .env (if present).
    In production (Render), environment variables are provided by the platform.
    """
    load_dotenv(override=False)


def get_database_url() -> str | None:
    """
    Return DATABASE_URL if present, otherwise None.
    """
    return os.environ.get("DATABASE_URL")


def get_secret_key() -> str:
    """
    Secret key for Flask sessions. Must be set in production.
    Falls back to a safe dev default if not provided.
    """
    return os.environ.get("SECRET_KEY", "dev-secret-key-change-me")
