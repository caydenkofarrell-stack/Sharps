"""Shared SQLite helpers for the Uncommon Hours Clip Engine.

Every module talks to the database through here so the connection settings,
schema bootstrap, and row factory stay in one place.
"""
from __future__ import annotations

import json
import sqlite3
from pathlib import Path

from config_loader import get_settings, project_root

SCHEMA_PATH = project_root() / "database" / "schema.sql"


def db_path() -> Path:
    settings = get_settings()
    return project_root() / settings["paths"]["database"]


def connect() -> sqlite3.Connection:
    """Open a connection with sane defaults and the schema guaranteed to exist."""
    path = db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Create tables from schema.sql if they don't exist yet."""
    schema = SCHEMA_PATH.read_text(encoding="utf-8")
    conn = connect()
    try:
        conn.executescript(schema)
        conn.commit()
    finally:
        conn.close()


def sync_sources(sources: list[dict]) -> None:
    """Upsert the source list from sources.json into the sources table."""
    conn = connect()
    try:
        for s in sources:
            conn.execute(
                """
                INSERT INTO sources (id, name, url, category, attribution, enabled)
                VALUES (?, ?, ?, ?, ?, ?)
                ON CONFLICT(id) DO UPDATE SET
                    name=excluded.name,
                    url=excluded.url,
                    category=excluded.category,
                    attribution=excluded.attribution,
                    enabled=excluded.enabled
                """,
                (
                    s["id"],
                    s.get("name", s["id"]),
                    s.get("url", ""),
                    s.get("category", ""),
                    s.get("attribution_text", ""),
                    1 if s.get("enabled") else 0,
                ),
            )
        conn.commit()
    finally:
        conn.close()


def json_dumps(value) -> str:
    return json.dumps(value, ensure_ascii=False)


if __name__ == "__main__":
    init_db()
    print(f"Initialized database at {db_path()}")
