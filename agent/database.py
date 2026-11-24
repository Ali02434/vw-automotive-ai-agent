"""SQLite for Issue #5 (Prototype).

Stores name, beschreibung, preis, url plus created_at / updated_at.
Insert new row or update if the same url already exists and content changed.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from agent.settings import loadconfig

PRODUCT_FIELDS = (
    "name",
    "beschreibung",
    "preis",
    "url",
)

_SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    beschreibung TEXT,
    preis REAL,
    url TEXT NOT NULL,
    created_at TEXT NOT NULL,
    updated_at TEXT,
    UNIQUE(url)
);
"""


def _now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _project_root() -> Path:
    return Path(__file__).resolve().parent.parent


def _normalize_preis(value: Any) -> float | None:
    """Keep preis comparable (string \"499.0\" vs float 499.0)."""
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def get_db_path(config: dict[str, Any] | None = None) -> Path:
    cfg = config if config is not None else loadconfig()
    relative = cfg.get("database", {}).get("path", "data/products.db")
    path = Path(relative)
    if not path.is_absolute():
        path = _project_root() / path
    return path


def connect(db_path: Path | None = None) -> sqlite3.Connection:
    path = db_path or get_db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON;")
    return conn


def init_db(conn: sqlite3.Connection | None = None) -> sqlite3.Connection:
    """Create DB file + products table if missing. Returns open connection."""
    own = conn is None
    connection = connect() if own else conn
    assert connection is not None
    try:
        connection.execute(_SCHEMA)
        connection.commit()
        return connection
    except Exception:
        if own:
            connection.close()
        raise


def _normalize_product(data: dict[str, Any]) -> dict[str, Any]:
    row = {key: data.get(key) for key in PRODUCT_FIELDS}
    if not row.get("url"):
        raise ValueError("url is required")
    row["preis"] = _normalize_preis(row.get("preis"))
    return row


def _content_tuple(row: dict[str, Any]) -> tuple:
    """Compare content fields only (ignore id / timestamps / url)."""
    return tuple(row.get(k) for k in PRODUCT_FIELDS if k != "url")


def save_product(
    data: dict[str, Any], conn: sqlite3.Connection | None = None
) -> dict[str, Any]:
    """Insert, or update when the same url already exists and content changed."""
    own = conn is None
    connection = init_db() if own else conn
    assert connection is not None
    try:
        product = _normalize_product(data)
        url = product["url"]

        existing = connection.execute(
            "SELECT * FROM products WHERE url = ?", (url,)
        ).fetchone()

        if existing is None:
            created = _now_iso()
            connection.execute(
                """
                INSERT INTO products (
                    name, beschreibung, preis, url, created_at, updated_at
                ) VALUES (?, ?, ?, ?, ?, NULL)
                """,
                (
                    product["name"],
                    product["beschreibung"],
                    product["preis"],
                    product["url"],
                    created,
                ),
            )
            connection.commit()
        else:
            existing_dict = dict(existing)
            if _content_tuple(existing_dict) == _content_tuple(product):
                return existing_dict

            updated = _now_iso()
            connection.execute(
                """
                UPDATE products SET
                    name = ?, beschreibung = ?, preis = ?, updated_at = ?
                WHERE url = ?
                """,
                (
                    product["name"],
                    product["beschreibung"],
                    product["preis"],
                    updated,
                    url,
                ),
            )
            connection.commit()

        row = connection.execute(
            "SELECT * FROM products WHERE url = ?", (url,)
        ).fetchone()
        return dict(row)
    finally:
        if own:
            connection.close()


def get_product_by_url(
    url: str, conn: sqlite3.Connection | None = None
) -> dict[str, Any] | None:
    own = conn is None
    connection = init_db() if own else conn
    assert connection is not None
    try:
        row = connection.execute(
            "SELECT * FROM products WHERE url = ?", (url,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        if own:
            connection.close()


def get_product_by_id(
    product_id: int, conn: sqlite3.Connection | None = None
) -> dict[str, Any] | None:
    own = conn is None
    connection = init_db() if own else conn
    assert connection is not None
    try:
        row = connection.execute(
            "SELECT * FROM products WHERE id = ?", (product_id,)
        ).fetchone()
        return dict(row) if row else None
    finally:
        if own:
            connection.close()


def list_products(conn: sqlite3.Connection | None = None) -> list[dict[str, Any]]:
    own = conn is None
    connection = init_db() if own else conn
    assert connection is not None
    try:
        rows = connection.execute(
            "SELECT * FROM products ORDER BY id ASC"
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        if own:
            connection.close()
