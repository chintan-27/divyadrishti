from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter, HTTPException

from libs.schemas.api_responses import (
    MetricDetailResponse,
    MetricExampleResponse,
    MetricNodeResponse,
    RollupResponse,
)
from libs.storage.metric_rollup_repository import MetricRollupRepository

if TYPE_CHECKING:
    import duckdb

router = APIRouter(prefix="/metrics", tags=["metrics"])

_db_conn: duckdb.DuckDBPyConnection | None = None


def set_db(conn: duckdb.DuckDBPyConnection) -> None:
    global _db_conn  # noqa: PLW0603
    _db_conn = conn


def _conn() -> duckdb.DuckDBPyConnection:
    if _db_conn is None:
        raise RuntimeError("Database not initialized")
    return _db_conn


@router.get("/top", response_model=list[MetricNodeResponse])
def top_metrics(limit: int = 20) -> list[MetricNodeResponse]:
    rows = _conn().execute(
        "SELECT m.node_id, m.label, m.definition, m.status, "
        "COUNT(e.item_id) as item_count "
        "FROM metric_node m "
        "LEFT JOIN item_metric_edge e ON m.node_id = e.node_id "
        "WHERE m.status = 'active' "
        "GROUP BY m.node_id, m.label, m.definition, m.status "
        "ORDER BY item_count DESC LIMIT ?",
        [limit],
    ).fetchall()
    return [
        MetricNodeResponse(
            node_id=r[0], label=r[1], definition=r[2],
            status=r[3], item_count=r[4],
        )
        for r in rows
    ]


@router.get("/{node_id}", response_model=MetricDetailResponse)
def get_metric(node_id: str, window: str = "today") -> MetricDetailResponse:
    row = _conn().execute(
        "SELECT m.node_id, m.label, m.definition, m.status, "
        "COUNT(e.item_id) as item_count "
        "FROM metric_node m "
        "LEFT JOIN item_metric_edge e ON m.node_id = e.node_id "
        "WHERE m.node_id = ? "
        "GROUP BY m.node_id, m.label, m.definition, m.status",
        [node_id],
    ).fetchone()
    if not row:
        raise HTTPException(status_code=404, detail="Metric node not found")

    rollup_repo = MetricRollupRepository(_conn())
    latest = rollup_repo.get_latest(node_id, window)
    latest_resp = None
    if latest:
        latest_resp = RollupResponse(**latest.model_dump())

    return MetricDetailResponse(
        node_id=row[0], label=row[1], definition=row[2],
        status=row[3], item_count=row[4], latest_rollup=latest_resp,
    )


@router.get("/{node_id}/series", response_model=list[RollupResponse])
def get_metric_series(
    node_id: str, window: str = "hour", start: int = 0, end: int = 0,
) -> list[RollupResponse]:
    import time as _time
    if end == 0:
        end = int(_time.time())
    if start == 0:
        start = end - 86400 * 7  # default 7 days
    rollup_repo = MetricRollupRepository(_conn())
    series = rollup_repo.get_series(node_id, window, start, end)
    return [RollupResponse(**r.model_dump()) for r in series]


@router.get("/{node_id}/examples", response_model=list[MetricExampleResponse])
def get_metric_examples(node_id: str, limit: int = 10) -> list[MetricExampleResponse]:
    rows = _conn().execute(
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
