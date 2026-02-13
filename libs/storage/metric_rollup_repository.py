from __future__ import annotations

from typing import TYPE_CHECKING

from libs.schemas.metric_rollup import MetricRollup

if TYPE_CHECKING:
    import duckdb

_UPSERT_SQL = """
INSERT INTO metric_rollup (
    node_id, "window", bucket_start, presence,
    sentiment_positive, sentiment_negative, sentiment_neutral,
    valence_score, split_score, consensus_pos, consensus_neg,
    heat_score, momentum, unique_authors, thread_count
) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT (node_id, "window", bucket_start) DO UPDATE SET
    presence = excluded.presence,
    sentiment_positive = excluded.sentiment_positive,
    sentiment_negative = excluded.sentiment_negative,
    sentiment_neutral = excluded.sentiment_neutral,
    valence_score = excluded.valence_score,
    split_score = excluded.split_score,
    consensus_pos = excluded.consensus_pos,
    consensus_neg = excluded.consensus_neg,
    heat_score = excluded.heat_score,
    momentum = excluded.momentum,
    unique_authors = excluded.unique_authors,
    thread_count = excluded.thread_count
"""

_COLUMNS = (
    'node_id, "window", bucket_start, presence, '
    "sentiment_positive, sentiment_negative, sentiment_neutral, "
    "valence_score, split_score, consensus_pos, consensus_neg, "
    "heat_score, momentum, unique_authors, thread_count"
)


def _row_to_rollup(row: tuple[object, ...]) -> MetricRollup:
    return MetricRollup(
        node_id=row[0],  # type: ignore[arg-type]
        window=row[1],  # type: ignore[arg-type]
        bucket_start=row[2],  # type: ignore[arg-type]
        presence=row[3],  # type: ignore[arg-type]
        sentiment_positive=row[4],  # type: ignore[arg-type]
        sentiment_negative=row[5],  # type: ignore[arg-type]
        sentiment_neutral=row[6],  # type: ignore[arg-type]
        valence_score=row[7],  # type: ignore[arg-type]
        split_score=row[8],  # type: ignore[arg-type]
        consensus_pos=row[9],  # type: ignore[arg-type]
        consensus_neg=row[10],  # type: ignore[arg-type]
        heat_score=row[11],  # type: ignore[arg-type]
        momentum=row[12],  # type: ignore[arg-type]
        unique_authors=row[13],  # type: ignore[arg-type]
        thread_count=row[14],  # type: ignore[arg-type]
    )


class MetricRollupRepository:
    def __init__(self, conn: duckdb.DuckDBPyConnection) -> None:
        self._conn = conn

    def upsert(self, rollup: MetricRollup) -> None:
        self._conn.execute(
            _UPSERT_SQL,
            [
                rollup.node_id, rollup.window, rollup.bucket_start, rollup.presence,
                rollup.sentiment_positive, rollup.sentiment_negative,
                rollup.sentiment_neutral, rollup.valence_score, rollup.split_score,
                rollup.consensus_pos, rollup.consensus_neg, rollup.heat_score,
                rollup.momentum, rollup.unique_authors, rollup.thread_count,
            ],
        )

    def get_latest(self, node_id: str, window: str) -> MetricRollup | None:
        row = self._conn.execute(
            f'SELECT {_COLUMNS} FROM metric_rollup '
            'WHERE node_id = ? AND "window" = ? '
            'ORDER BY bucket_start DESC LIMIT 1',
            [node_id, window],
        ).fetchone()
        return _row_to_rollup(row) if row else None

    def get_series(self, node_id: str, window: str,
                   start: int, end: int) -> list[MetricRollup]:
        rows = self._conn.execute(
            f'SELECT {_COLUMNS} FROM metric_rollup '
            'WHERE node_id = ? AND "window" = ? '
            'AND bucket_start >= ? AND bucket_start <= ? '
            'ORDER BY bucket_start ASC',
            [node_id, window, start, end],
        ).fetchall()
        return [_row_to_rollup(r) for r in rows]

    def get_top_by_field(self, window: str, field: str,
                         limit: int = 20) -> list[MetricRollup]:
        allowed = {
            "presence", "valence_score", "split_score",
            "consensus_pos", "consensus_neg", "heat_score", "momentum",
        }
        if field not in allowed:
            field = "presence"
        rows = self._conn.execute(
            f'SELECT {_COLUMNS} FROM metric_rollup r1 '
            'WHERE "window" = ? AND bucket_start = ('
            '  SELECT MAX(r2.bucket_start) FROM metric_rollup r2 '
            '  WHERE r2.node_id = r1.node_id AND r2."window" = r1."window"'
            f') ORDER BY {field} DESC LIMIT ?',
            [window, limit],
        ).fetchall()
        return [_row_to_rollup(r) for r in rows]
