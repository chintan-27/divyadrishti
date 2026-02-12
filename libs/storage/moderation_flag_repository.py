from __future__ import annotations

from typing import TYPE_CHECKING

from libs.schemas.moderation_flag import ModerationFlag

if TYPE_CHECKING:
    import duckdb

_UPSERT_SQL = """
INSERT INTO moderation_flag (item_id, status, reason, flagged_at)
VALUES (?, ?, ?, ?)
ON CONFLICT (item_id) DO UPDATE SET
    status = excluded.status,
    reason = excluded.reason,
    flagged_at = excluded.flagged_at
"""

_COLUMNS = "item_id, status, reason, flagged_at"


def _row_to_flag(row: tuple[object, ...]) -> ModerationFlag:
    return ModerationFlag(
        item_id=row[0],  # type: ignore[arg-type]
        status=row[1],  # type: ignore[arg-type]
        reason=row[2],  # type: ignore[arg-type]
        flagged_at=row[3],  # type: ignore[arg-type]
    )


class ModerationFlagRepository:
    def __init__(self, conn: duckdb.DuckDBPyConnection) -> None:
        self._conn = conn

    def upsert(self, flag: ModerationFlag) -> None:
        self._conn.execute(
            _UPSERT_SQL,
            [flag.item_id, flag.status, flag.reason, flag.flagged_at],
        )

    def get_by_item_id(self, item_id: int) -> ModerationFlag | None:
        row = self._conn.execute(
            f"SELECT {_COLUMNS} FROM moderation_flag WHERE item_id = ?",
            [item_id],
        ).fetchone()
        return _row_to_flag(row) if row else None

    def get_by_status(self, status: str, limit: int = 50) -> list[ModerationFlag]:
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM moderation_flag WHERE status = ? LIMIT ?",
            [status, limit],
        ).fetchall()
        return [_row_to_flag(r) for r in rows]
