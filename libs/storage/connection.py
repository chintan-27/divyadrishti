from __future__ import annotations

from contextlib import contextmanager
from typing import TYPE_CHECKING

import duckdb

if TYPE_CHECKING:
    from collections.abc import Generator


class DuckDBConnection:
    """Thin wrapper around a duckdb connection."""

    def __init__(self, db_path: str | None = None) -> None:
        self._db_path = db_path or ":memory:"
        self._conn: duckdb.DuckDBPyConnection | None = None

    def connect(self) -> duckdb.DuckDBPyConnection:
        if self._conn is None:
            self._conn = duckdb.connect(self._db_path)
        return self._conn

    def close(self) -> None:
        if self._conn is not None:
            self._conn.close()
            self._conn = None

    @contextmanager
    def cursor(self) -> Generator[duckdb.DuckDBPyConnection]:
        conn = self.connect()
        cur = conn.cursor()
        try:
            yield cur
        finally:
            cur.close()
