from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import duckdb

_UPSERT_SQL = """
INSERT INTO backfill_state ("key", value, updated_at)
VALUES (?, ?, ?)
ON CONFLICT ("key") DO UPDATE SET
    value = excluded.value,
    updated_at = excluded.updated_at
"""


class BackfillStateRepository:
    def __init__(self, conn: duckdb.DuckDBPyConnection) -> None:
        self._conn = conn

    def get(self, key: str) -> str | None:
        row = self._conn.execute(
            'SELECT value FROM backfill_state WHERE "key" = ?',
            [key],
        ).fetchone()
        return row[0] if row else None  # type: ignore[index]

    def set(self, key: str, value: str, updated_at: int) -> None:
        self._conn.execute(_UPSERT_SQL, [key, value, updated_at])
