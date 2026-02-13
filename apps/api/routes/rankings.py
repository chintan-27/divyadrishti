from __future__ import annotations

from typing import TYPE_CHECKING

from fastapi import APIRouter

from libs.schemas.api_responses import RollupResponse
from libs.storage.metric_rollup_repository import MetricRollupRepository

if TYPE_CHECKING:
    import duckdb

router = APIRouter(prefix="/rankings", tags=["rankings"])

_db_conn: duckdb.DuckDBPyConnection | None = None

_LENS_FIELDS = {
    "top": "presence",
    "controversial": "split_score",
    "consensus_pos": "consensus_pos",
    "consensus_neg": "consensus_neg",
    "heated": "heat_score",
    "rising": "momentum",
}


def set_db(conn: duckdb.DuckDBPyConnection) -> None:
    global _db_conn  # noqa: PLW0603
    _db_conn = conn


def _conn() -> duckdb.DuckDBPyConnection:
    if _db_conn is None:
        raise RuntimeError("Database not initialized")
    return _db_conn


@router.get("", response_model=list[RollupResponse])
def get_rankings(
    window: str = "today",
    lens: str = "top",
    limit: int = 20,
) -> list[RollupResponse]:
    field = _LENS_FIELDS.get(lens, "presence")
    repo = MetricRollupRepository(_conn())
    rollups = repo.get_top_by_field(window, field, limit)
    return [RollupResponse(**r.model_dump()) for r in rollups]
