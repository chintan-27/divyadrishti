from __future__ import annotations

import asyncio
import time

import duckdb
from redis import Redis

from agents.celery_app import app
from agents.config import AgentConfig
from libs.events.channels import HN_DISCOVERY
from libs.events.publisher import EventPublisher
from libs.hn_clients.algolia import AlgoliaHNClient
from libs.schemas.watchlist import WatchlistEntry
from libs.storage.schema import init_schema
from libs.storage.watchlist_repository import WatchlistRepository

_TTL_SECONDS = 7200  # 2 hours


def _compute_priority(hit: dict[str, object]) -> float:
    points = int(hit.get("points") or 0)
    comments = int(hit.get("num_comments") or 0)
    return float(points + comments * 2)


async def _fetch_front_page(client: AlgoliaHNClient) -> list[dict[str, object]]:
    return await client.search_front_page()  # type: ignore[return-value]


@app.task(name="trend_scout.discover_trending")
def discover_trending() -> int:
    """Discover trending HN stories and upsert into watchlist."""
    config = AgentConfig()
    conn = duckdb.connect(config.db_path)
    init_schema(conn)
    repo = WatchlistRepository(conn)
    redis = Redis.from_url(config.redis_url)
    publisher = EventPublisher(redis)

    try:
        hits = asyncio.run(_fetch_front_page(AlgoliaHNClient()))
        now = int(time.time())
        count = 0
        for hit in hits:
            story_id = int(hit.get("objectID") or hit.get("story_id") or 0)
            if not story_id:
                continue
            entry = WatchlistEntry(
                story_id=story_id,
                priority_score=_compute_priority(hit),
                ttl_expires=now + _TTL_SECONDS,
            )
            repo.upsert(entry)
            publisher.publish(HN_DISCOVERY, {"story_id": story_id, "action": "discovered"})
            count += 1
        return count
    finally:
        conn.close()
        redis.close()
