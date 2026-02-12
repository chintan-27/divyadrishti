from __future__ import annotations

import asyncio
import json
from typing import TYPE_CHECKING

from fastapi import APIRouter
from sse_starlette.sse import EventSourceResponse
from starlette.requests import Request

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

    import duckdb

router = APIRouter(prefix="/stream", tags=["stream"])

_db_conn: duckdb.DuckDBPyConnection | None = None


def set_db(conn: duckdb.DuckDBPyConnection) -> None:
    global _db_conn  # noqa: PLW0603
    _db_conn = conn


def _conn() -> duckdb.DuckDBPyConnection:
    if _db_conn is None:
        raise RuntimeError("Database not initialized")
    return _db_conn


async def _trending_generator(request: Request) -> AsyncGenerator[str]:
    while True:
        if await request.is_disconnected():
            break
        rows = _conn().execute(
            'SELECT id, title, score FROM hn_item WHERE "type" = \'story\' '
            "ORDER BY score DESC NULLS LAST LIMIT 10"
        ).fetchall()
        data = [{"id": r[0], "title": r[1], "score": r[2]} for r in rows]
        yield json.dumps(data)
        await asyncio.sleep(5)


@router.get("/trending")
async def stream_trending(request: Request) -> EventSourceResponse:
    return EventSourceResponse(_trending_generator(request))
