from __future__ import annotations

import time

import duckdb

from agents.celery_app import app
from agents.config import AgentConfig
from libs.storage.schema import init_schema
from libs.storage.watchlist_repository import WatchlistRepository


@app.task(name="supervisor.cleanup_watchlist")
def cleanup_watchlist() -> int:
    """Remove expired watchlist entries."""
    config = AgentConfig()
    conn = duckdb.connect(config.db_path)
    init_schema(conn)
    repo = WatchlistRepository(conn)
    try:
        return repo.remove_expired(int(time.time()))
    finally:
        conn.close()
