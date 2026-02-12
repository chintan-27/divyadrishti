from __future__ import annotations

from typing import TYPE_CHECKING

from libs.schemas.opinion_signal import OpinionSignal

if TYPE_CHECKING:
    import duckdb

_UPSERT_SQL = """
INSERT INTO opinion_signal (item_id, valence, intensity, confidence, label, model_version)
VALUES (?, ?, ?, ?, ?, ?)
ON CONFLICT (item_id) DO UPDATE SET
    valence = excluded.valence,
    intensity = excluded.intensity,
    confidence = excluded.confidence,
    label = excluded.label,
    model_version = excluded.model_version
"""

_COLUMNS = "item_id, valence, intensity, confidence, label, model_version"


def _row_to_signal(row: tuple[object, ...]) -> OpinionSignal:
    return OpinionSignal(
        item_id=row[0],  # type: ignore[arg-type]
        valence=row[1],  # type: ignore[arg-type]
        intensity=row[2],  # type: ignore[arg-type]
        confidence=row[3],  # type: ignore[arg-type]
        label=row[4],  # type: ignore[arg-type]
        model_version=row[5],  # type: ignore[arg-type]
    )


class OpinionSignalRepository:
    def __init__(self, conn: duckdb.DuckDBPyConnection) -> None:
        self._conn = conn

    def upsert(self, signal: OpinionSignal) -> None:
        self._conn.execute(
            _UPSERT_SQL,
            [signal.item_id, signal.valence, signal.intensity,
             signal.confidence, signal.label, signal.model_version],
        )

    def get_by_item_id(self, item_id: int) -> OpinionSignal | None:
        row = self._conn.execute(
            f"SELECT {_COLUMNS} FROM opinion_signal WHERE item_id = ?",
            [item_id],
        ).fetchone()
        return _row_to_signal(row) if row else None

    def get_by_item_ids(self, item_ids: list[int]) -> list[OpinionSignal]:
        if not item_ids:
            return []
        placeholders = ", ".join("?" for _ in item_ids)
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM opinion_signal WHERE item_id IN ({placeholders})",
            item_ids,
        ).fetchall()
        return [_row_to_signal(r) for r in rows]

    def get_recent(self, limit: int = 50) -> list[OpinionSignal]:
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM opinion_signal ORDER BY item_id DESC LIMIT ?",
            [limit],
        ).fetchall()
        return [_row_to_signal(r) for r in rows]
