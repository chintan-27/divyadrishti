from __future__ import annotations

import logging
import os
from contextlib import asynccontextmanager
from typing import TYPE_CHECKING

import duckdb
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from apps.api import scheduler
from apps.api.db import set_db_path
from apps.api.middleware import RequestLoggingMiddleware
from apps.api.routes import health, metrics, rankings, stories, stream
from libs.storage.schema import init_schema

if TYPE_CHECKING:
    from collections.abc import AsyncGenerator

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    db_path = "divyadrishti.duckdb"
    # Bootstrap schema if DB doesn't exist yet
    if not os.path.exists(db_path):
        tmp = duckdb.connect(db_path)
        init_schema(tmp)
        tmp.close()
    set_db_path(db_path)

    # Start background agent tasks in-process
    scheduler.start()
    logger.info("Background scheduler started")

    yield

    scheduler.stop()
    logger.info("Background scheduler stopped")


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
