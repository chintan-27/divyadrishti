from __future__ import annotations

import time

from agents.celery_app import app, get_worker_conn
from libs.storage.watchlist_repository import WatchlistRepository


@app.task(name="supervisor.cleanup_watchlist")
def cleanup_watchlist() -> int:
    """Remove expired watchlist entries."""
    conn = get_worker_conn()
    repo = WatchlistRepository(conn)
    try:
        return repo.remove_expired(int(time.time()))
    finally:
        conn.close()
