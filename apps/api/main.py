from __future__ import annotations

from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

import duckdb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api.middleware import RequestLoggingMiddleware
from apps.api.routes import health, metrics, rankings, stories, stream
from libs.storage.schema import init_schema

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    conn = duckdb.connect("divyadrishti.duckdb")
    init_schema(conn)
    stories.set_db(conn)
    stream.set_db(conn)
    metrics.set_db(conn)
    rankings.set_db(conn)
    yield
    conn.close()


app = FastAPI(title="divyadrishti", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.include_router(health.router)
app.include_router(stories.router)
app.include_router(stream.router)
app.include_router(metrics.router)
app.include_router(rankings.router)
