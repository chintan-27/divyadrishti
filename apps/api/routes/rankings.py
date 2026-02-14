from __future__ import annotations

import duckdb
from fastapi import APIRouter, Depends

from apps.api.db import get_db
from libs.schemas.api_responses import (
    MetricNodeResponse,
    RankingEntryResponse,
    SentimentResponse,
)

router = APIRouter(prefix="/rankings", tags=["rankings"])

_LENS_FIELDS = {
    "top": "presence",
    "controversial": "split_score",
    "consensus_pos": "consensus_pos",
    "consensus_neg": "consensus_neg",
    "heated": "heat_score",
    "rising": "momentum",
}


@router.get("", response_model=list[RankingEntryResponse])
def get_rankings(
    window: str = "today",
    lens: str = "top",
    limit: int = 20,
    conn: duckdb.DuckDBPyConnection = Depends(get_db),
) -> list[RankingEntryResponse]:
    field = _LENS_FIELDS.get(lens, "presence")
    rows = conn.execute(
        "SELECT r.node_id, m.label, m.definition, "
        "r.presence, r.valence_score, r.heat_score, r.momentum, "
        "r.sentiment_positive, r.sentiment_negative, r.sentiment_neutral "
        "FROM metric_rollup r "
        "JOIN metric_node m ON r.node_id = m.node_id "
        f'WHERE r."window" = ? AND m.status = \'active\' '
        f"ORDER BY r.{field} DESC LIMIT ?",
        [window, limit],
    ).fetchall()
    return [
        RankingEntryResponse(
            rank=i + 1,
            metric=MetricNodeResponse(
                id=r[0], label=r[1], definition=r[2],
                presence_pct=r[3] * 100, valence=r[4], heat=r[5], momentum=r[6],
                sentiment=SentimentResponse(positive=r[7], negative=r[8], neutral=r[9]),
            ),
        )
        for i, r in enumerate(rows)
    ]
