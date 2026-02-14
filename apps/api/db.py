"""Shared DB access helpers for API routes.

Since DuckDB only supports single-process access, the API and background tasks
run in the same process.  Routes open short-lived connections per request;
background tasks do the same.

In tests, ``set_db(conn)`` injects an in-memory connection directly.
"""
from __future__ import annotations

from collections.abc import Generator
from typing import TYPE_CHECKING

import duckdb

if TYPE_CHECKING:
    pass

_db_conn: duckdb.DuckDBPyConnection | None = None
_db_path: str | None = None


def set_db(conn: duckdb.DuckDBPyConnection) -> None:
    """Inject a connection directly (used by tests)."""
    global _db_conn  # noqa: PLW0603
    _db_conn = conn


def set_db_path(path: str) -> None:
    """Store the DB path for per-request connections."""
    global _db_path  # noqa: PLW0603
    _db_path = path


def get_conn() -> duckdb.DuckDBPyConnection:
    """Return a DuckDB connection.

    If a test connection was injected via ``set_db()``, return it.
    Otherwise open a fresh short-lived connection from the configured path.
    """
    if _db_conn is not None:
        return _db_conn
    if _db_path is not None:
        return duckdb.connect(_db_path)
    msg = "Database not configured — call set_db() or set_db_path() first"
    raise RuntimeError(msg)


def is_test_conn() -> bool:
    """Return True if a test connection was injected (skip close in that case)."""
    return _db_conn is not None


def get_db() -> Generator[duckdb.DuckDBPyConnection]:
    """FastAPI dependency that yields a connection and closes it after the request."""
    conn = get_conn()
    try:
        yield conn
    finally:
        if not is_test_conn():
            conn.close()
