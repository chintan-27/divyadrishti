from __future__ import annotations

import logging
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

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    db_path = "divyadrishti.duckdb"
    # Always init schema (handles dimension migration if needed)
    tmp = duckdb.connect(db_path)
    init_schema(tmp)
    tmp.close()
    set_db_path(db_path)

    # Eagerly init the OpenAI client on the main thread to avoid
    # import deadlocks when multiple agent threads import openai submodules.
    try:
        from libs.nlp.navigator import get_client
        client = get_client()
        # Force lazy submodule imports by touching .chat and .embeddings
        _ = client.chat
        _ = client.embeddings
    except Exception:
        logger.warning("Navigator client not configured — NLP agents will fail")

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
