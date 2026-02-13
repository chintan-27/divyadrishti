from __future__ import annotations

import asyncio
import time

import duckdb

from agents.celery_app import app
from agents.config import AgentConfig
from libs.hn_clients.algolia import AlgoliaHNClient
from libs.schemas.watchlist import WatchlistEntry
from libs.storage.backfill_state_repository import BackfillStateRepository
from libs.storage.schema import init_schema
from libs.storage.watchlist_repository import WatchlistRepository

_DAY_SECS = 86400
_TTL_SECONDS = 7200


async def _search_by_date(
    client: AlgoliaHNClient, start_ts: int, end_ts: int,
) -> list[dict[str, object]]:
    return await client.search_by_date(  # type: ignore[return-value]
        tags="story",
        hits_per_page=50,
        numeric_filters=f"created_at_i>={start_ts},created_at_i<{end_ts}",
    )


@app.task(name="trend_scout.backfill_stories")
def backfill_stories() -> int:
    """Backfill historical stories from Algolia in daily chunks."""
    config = AgentConfig()
    conn = duckdb.connect(config.db_path)
    init_schema(conn)
    state_repo = BackfillStateRepository(conn)
    watchlist = WatchlistRepository(conn)

    try:
        now = int(time.time())
        # default start: Jan 1, 2024
        checkpoint = state_repo.get("backfill_checkpoint")
        if checkpoint:
            start_ts = int(checkpoint)
        else:
            start_ts = 1704067200  # 2024-01-01

        end_ts = min(start_ts + _DAY_SECS, now)
        if start_ts >= now:
            return 0  # caught up

        hits = asyncio.run(_search_by_date(AlgoliaHNClient(), start_ts, end_ts))

        count = 0
        for hit in hits:
            story_id = int(hit.get("objectID") or 0)
            if not story_id:
                continue
            points = int(hit.get("points") or 0)
            entry = WatchlistEntry(
                story_id=story_id,
                priority_score=float(points),
                ttl_expires=now + _TTL_SECONDS,
            )
            watchlist.upsert(entry)
            count += 1

        state_repo.set("backfill_checkpoint", str(end_ts), now)
        return count
    finally:
        conn.close()
