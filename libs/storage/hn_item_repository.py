from __future__ import annotations

from typing import TYPE_CHECKING

from libs.schemas.hn_item import HNItem

if TYPE_CHECKING:
    import duckdb

_UPSERT_SQL = """
INSERT INTO hn_item (
    id, "type", "by", author_hash, "time", "text", text_clean,
    parent, kids, title, url, score, descendants, deleted, dead
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT (id) DO UPDATE SET
    "type" = COALESCE(excluded."type", hn_item."type"),
    "by" = COALESCE(excluded."by", hn_item."by"),
    author_hash = COALESCE(excluded.author_hash, hn_item.author_hash),
    "time" = COALESCE(excluded."time", hn_item."time"),
    "text" = COALESCE(excluded."text", hn_item."text"),
    text_clean = COALESCE(excluded.text_clean, hn_item.text_clean),
    parent = COALESCE(excluded.parent, hn_item.parent),
    kids = COALESCE(excluded.kids, hn_item.kids),
    title = COALESCE(excluded.title, hn_item.title),
    url = COALESCE(excluded.url, hn_item.url),
    score = COALESCE(excluded.score, hn_item.score),
    descendants = COALESCE(excluded.descendants, hn_item.descendants),
    deleted = COALESCE(excluded.deleted, hn_item.deleted),
    dead = COALESCE(excluded.dead, hn_item.dead)
"""

_COLUMNS = (
    'id, "type", "by", author_hash, "time", "text", text_clean, '
    "parent, kids, title, url, score, descendants, deleted, dead"
)


def _row_to_item(row: tuple[object, ...]) -> HNItem:
    return HNItem(
        id=row[0],  # type: ignore[arg-type]
        type=row[1],  # type: ignore[arg-type]
        by=row[2],  # type: ignore[arg-type]
        author_hash=row[3],  # type: ignore[arg-type]
        time=row[4],  # type: ignore[arg-type]
        text=row[5],  # type: ignore[arg-type]
        text_clean=row[6],  # type: ignore[arg-type]
        parent=row[7],  # type: ignore[arg-type]
        kids=row[8],  # type: ignore[arg-type]
        title=row[9],  # type: ignore[arg-type]
        url=row[10],  # type: ignore[arg-type]
        score=row[11],  # type: ignore[arg-type]
        descendants=row[12],  # type: ignore[arg-type]
        deleted=row[13],  # type: ignore[arg-type]
        dead=row[14],  # type: ignore[arg-type]
    )


class HNItemRepository:
    def __init__(self, conn: duckdb.DuckDBPyConnection) -> None:
        self._conn = conn

    def upsert(self, item: HNItem) -> None:
        self._conn.execute(
            _UPSERT_SQL,
            [
                item.id, item.type, item.by, item.author_hash, item.time,
                item.text, item.text_clean, item.parent, item.kids,
                item.title, item.url, item.score, item.descendants,
                item.deleted, item.dead,
            ],
        )

    def get_by_id(self, item_id: int) -> HNItem | None:
        row = self._conn.execute(
            f"SELECT {_COLUMNS} FROM hn_item WHERE id = ?", [item_id]
        ).fetchone()
        return _row_to_item(row) if row else None

    def get_by_ids(self, item_ids: list[int]) -> list[HNItem]:
        if not item_ids:
            return []
        placeholders = ", ".join("?" for _ in item_ids)
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM hn_item WHERE id IN ({placeholders})",
            item_ids,
        ).fetchall()
        return [_row_to_item(r) for r in rows]

    def get_recent(self, limit: int = 50, type_filter: str | None = None) -> list[HNItem]:
        if type_filter:
            rows = self._conn.execute(
                f'SELECT {_COLUMNS} FROM hn_item WHERE "type" = ? '
                f'ORDER BY "time" DESC LIMIT ?',
                [type_filter, limit],
            ).fetchall()
        else:
            rows = self._conn.execute(
                f'SELECT {_COLUMNS} FROM hn_item ORDER BY "time" DESC LIMIT ?',
                [limit],
            ).fetchall()
        return [_row_to_item(r) for r in rows]
