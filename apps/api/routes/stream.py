from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from starlette.requests import Request

from apps.api.db import get_conn, is_test_conn

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

router = APIRouter(prefix="/stream", tags=["stream"])


def _query_and_close(sql: str) -> list:
    conn = get_conn()
    try:
        return conn.execute(sql).fetchall()
    finally:
        if not is_test_conn():
            conn.close()


async def _trending_generator(request: Request) -> AsyncGenerator[str]:
    while True:
        if await request.is_disconnected():
            break
        rows = _query_and_close(
            'SELECT id, title, score FROM hn_item WHERE "type" = \'story\' '
            "ORDER BY score DESC NULLS LAST LIMIT 10"
        )
        data = [{"id": r[0], "title": r[1], "score": r[2]} for r in rows]
        yield json.dumps(data)
        await asyncio.sleep(5)


@router.get("/trending")
async def stream_trending(request: Request) -> EventSourceResponse:
    return EventSourceResponse(_trending_generator(request))


async def _metrics_generator(request: Request) -> AsyncGenerator[str]:
    while True:
        if await request.is_disconnected():
            break
        rows = _query_and_close(
            'SELECT node_id, "window", presence, valence_score, heat_score, momentum '
            'FROM metric_rollup WHERE "window" = \'today\' '
            "ORDER BY presence DESC LIMIT 20"
        )
        data = [
            {
                "node_id": r[0], "window": r[1], "presence": r[2],
                "valence_score": r[3], "heat_score": r[4], "momentum": r[5],
            }
            for r in rows
        ]
        yield json.dumps(data)
        await asyncio.sleep(5)


@router.get("/metrics")
async def stream_metrics(request: Request) -> EventSourceResponse:
    return EventSourceResponse(_metrics_generator(request))
