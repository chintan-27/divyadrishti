from __future__ import annotations

from typing import TYPE_CHECKING

from libs.schemas.watchlist import WatchlistEntry

if TYPE_CHECKING:
    import duckdb

_UPSERT_SQL = """
INSERT INTO watchlist (story_id, priority_score, ttl_expires, last_fetched)
VALUES (?, ?, ?, ?)
ON CONFLICT (story_id) DO UPDATE SET
    priority_score = COALESCE(excluded.priority_score, watchlist.priority_score),
    ttl_expires = COALESCE(excluded.ttl_expires, watchlist.ttl_expires),
    last_fetched = COALESCE(excluded.last_fetched, watchlist.last_fetched)
"""

_COLUMNS = "story_id, priority_score, ttl_expires, last_fetched"


def _row_to_entry(row: tuple[object, ...]) -> WatchlistEntry:
    return WatchlistEntry(
        story_id=row[0],  # type: ignore[arg-type]
        priority_score=row[1],  # type: ignore[arg-type]
        ttl_expires=row[2],  # type: ignore[arg-type]
        last_fetched=row[3],  # type: ignore[arg-type]
    )


class WatchlistRepository:
    def __init__(self, conn: duckdb.DuckDBPyConnection) -> None:
        self._conn = conn

    def upsert(self, entry: WatchlistEntry) -> None:
        self._conn.execute(
            _UPSERT_SQL,
            [entry.story_id, entry.priority_score, entry.ttl_expires, entry.last_fetched],
        )

    def get_active(self, now_ts: int, limit: int = 50) -> list[WatchlistEntry]:
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM watchlist "
            "WHERE ttl_expires > ? "
            "ORDER BY priority_score DESC LIMIT ?",
            [now_ts, limit],
        ).fetchall()
        return [_row_to_entry(r) for r in rows]

    def mark_fetched(self, story_id: int, now_ts: int) -> None:
        self._conn.execute(
            "UPDATE watchlist SET last_fetched = ? WHERE story_id = ?",
            [now_ts, story_id],
        )

    def remove_expired(self, now_ts: int) -> int:
        result = self._conn.execute(
            "DELETE FROM watchlist WHERE ttl_expires <= ? RETURNING story_id",
            [now_ts],
        ).fetchall()
        return len(result)
