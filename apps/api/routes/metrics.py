from __future__ import annotations

from datetime import datetime, timezone

import duckdb
from fastapi import APIRouter, Depends, HTTPException

from apps.api.db import get_db
from libs.schemas.api_responses import (
    MetricDetailResponse,
    MetricExampleResponse,
    MetricNodeResponse,
    RollupDataResponse,
    SentimentResponse,
    SeriesPointResponse,
    StoryResponse,
)
from libs.storage.metric_rollup_repository import MetricRollupRepository

router = APIRouter(prefix="/metrics", tags=["metrics"])


def _rollup_to_metric_node(
    node_id: str, label: str, definition: str, item_count: int,
    rollup: object | None,
) -> MetricNodeResponse:
    """Build a MetricNodeResponse, pulling stats from the rollup if available."""
    if rollup is None:
        return MetricNodeResponse(id=node_id, label=label, definition=definition, item_count=item_count)
    return MetricNodeResponse(
        id=node_id, label=label, definition=definition, item_count=item_count,
        presence_pct=rollup.presence * 100,
        valence=rollup.valence_score,
        heat=rollup.heat_score,
        momentum=rollup.momentum,
        sentiment=SentimentResponse(
            positive=rollup.sentiment_positive,
            negative=rollup.sentiment_negative,
            neutral=rollup.sentiment_neutral,
        ),
    )


@router.get("/top", response_model=list[MetricNodeResponse])
def top_metrics(
    limit: int = 20, conn: duckdb.DuckDBPyConnection = Depends(get_db),
) -> list[MetricNodeResponse]:
    rows = conn.execute(
        "SELECT m.node_id, m.label, m.definition, "
        "COUNT(e.item_id) as item_count, "
        "COALESCE(r.presence, 0) as presence, "
        "COALESCE(r.valence_score, 0) as valence, "
        "COALESCE(r.heat_score, 0) as heat, "
        "COALESCE(r.momentum, 0) as momentum, "
        "COALESCE(r.sentiment_positive, 0) as sent_pos, "
        "COALESCE(r.sentiment_negative, 0) as sent_neg, "
        "COALESCE(r.sentiment_neutral, 0) as sent_neu "
        "FROM metric_node m "
        "LEFT JOIN item_metric_edge e ON m.node_id = e.node_id "
        "LEFT JOIN ("
        "  SELECT node_id, presence, valence_score, heat_score, momentum, "
        "    sentiment_positive, sentiment_negative, sentiment_neutral, "
        "    ROW_NUMBER() OVER (PARTITION BY node_id ORDER BY bucket_start DESC) as rn "
        "  FROM metric_rollup"
        ") r ON m.node_id = r.node_id AND r.rn = 1 "
        "WHERE m.status = 'active' "
        "GROUP BY m.node_id, m.label, m.definition, "
        "r.presence, r.valence_score, r.heat_score, r.momentum, "
        "r.sentiment_positive, r.sentiment_negative, r.sentiment_neutral "
        "ORDER BY item_count DESC LIMIT ?",
        [limit],
    ).fetchall()
    return [
        MetricNodeResponse(
            id=r[0], label=r[1], definition=r[2], item_count=r[3],
            presence_pct=r[4] * 100, valence=r[5], heat=r[6], momentum=r[7],
            sentiment=SentimentResponse(positive=r[8], negative=r[9], neutral=r[10]),
        )
        for r in rows
    ]


@router.get("/{node_id}", response_model=MetricDetailResponse)
def get_metric(
    node_id: str, window: str = "today",
    conn: duckdb.DuckDBPyConnection = Depends(get_db),
) -> MetricDetailResponse:
    row = conn.execute(
        "SELECT m.node_id, m.label, m.definition "
        "FROM metric_node m WHERE m.node_id = ?",
        [node_id],
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Metric node not found")

    rollup_repo = MetricRollupRepository(conn)
    latest = rollup_repo.get_latest(node_id, window)

    rollup_data = RollupDataResponse(window=window)
    if latest:
        rollup_data = RollupDataResponse(
            window=latest.window,
            presence_pct=latest.presence * 100,
            valence=latest.valence_score,
            heat=latest.heat_score,
            momentum=latest.momentum,
            split=latest.split_score,
            consensus=latest.consensus_pos - latest.consensus_neg,
            unique_authors=latest.unique_authors,
            sentiment=SentimentResponse(
                positive=latest.sentiment_positive,
                negative=latest.sentiment_negative,
                neutral=latest.sentiment_neutral,
            ),
        )

    # Fetch example items
    example_rows = conn.execute(
        "SELECT h.id, h.title, h.url, h.score, h.\"by\", h.\"time\", h.descendants, h.\"type\" "
        "FROM item_metric_edge e "
        "JOIN hn_item h ON e.item_id = h.id "
        "WHERE e.node_id = ? "
        "ORDER BY e.weight DESC LIMIT 10",
        [node_id],
    ).fetchall()
    examples = [
        StoryResponse(
            id=r[0], title=r[1], url=r[2], score=r[3],
            by=r[4], time=r[5], descendants=r[6], type=r[7],
        )
        for r in example_rows
    ]

    return MetricDetailResponse(
        id=row[0], label=row[1], definition=row[2],
        rollup=rollup_data, example_items=examples,
    )


@router.get("/{node_id}/series", response_model=list[SeriesPointResponse])
def get_metric_series(
    node_id: str, window: str = "hour", start: int = 0, end: int = 0,
    conn: duckdb.DuckDBPyConnection = Depends(get_db),
) -> list[SeriesPointResponse]:
    import time as _time
    if end == 0:
        end = int(_time.time())
    if start == 0:
        start = end - 86400 * 7  # default 7 days
    rollup_repo = MetricRollupRepository(conn)
    series = rollup_repo.get_series(node_id, window, start, end)
    return [
        SeriesPointResponse(
            ts=datetime.fromtimestamp(r.bucket_start, tz=timezone.utc).isoformat(),
            presence_pct=r.presence * 100,
            valence=r.valence_score,
            heat=r.heat_score,
            momentum=r.momentum,
        )
        for r in series
    ]


@router.get("/{node_id}/examples", response_model=list[MetricExampleResponse])
def get_metric_examples(
    node_id: str, limit: int = 10,
    conn: duckdb.DuckDBPyConnection = Depends(get_db),
) -> list[MetricExampleResponse]:
    rows = conn.execute(
        "SELECT h.id, h.title, h.text_clean, e.weight "
        "FROM item_metric_edge e "
        "JOIN hn_item h ON e.item_id = h.id "
        "WHERE e.node_id = ? "
        "ORDER BY e.weight DESC LIMIT ?",
        [node_id, limit],
    ).fetchall()
    return [
        MetricExampleResponse(
            item_id=r[0], title=r[1], text=r[2], weight=r[3],
        )
        for r in rows
    ]
