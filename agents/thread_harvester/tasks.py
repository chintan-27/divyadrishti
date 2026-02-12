from __future__ import annotations

import asyncio
import time
from typing import Any

import duckdb
from redis import Redis

from agents.celery_app import app
from agents.config import AgentConfig
from libs.events.channels import HN_CONTENT
from libs.events.publisher import EventPublisher
from libs.hn_clients.firebase import FirebaseHNClient
from libs.schemas.hn_item import HNItem
from libs.storage.hn_item_repository import HNItemRepository
from libs.storage.schema import init_schema
from libs.storage.watchlist_repository import WatchlistRepository
from libs.utils.hashing import hash_author

_MAX_DEPTH = 3
_MAX_COMMENTS = 200


def _item_from_raw(raw: dict[str, Any], salt: str) -> HNItem:
    author = raw.get("by")
    return HNItem(
        id=raw["id"],
        type=raw.get("type"),
        by=author,
        author_hash=hash_author(author, salt) if author else None,
        time=raw.get("time"),
        text=raw.get("text"),
        parent=raw.get("parent"),
        kids=raw.get("kids"),
        title=raw.get("title"),
        url=raw.get("url"),
        score=raw.get("score"),
        descendants=raw.get("descendants"),
        deleted=raw.get("deleted"),
        dead=raw.get("dead"),
    )


async def _fetch_tree(
    client: FirebaseHNClient,
    item_id: int,
    salt: str,
    depth: int = 0,
) -> list[HNItem]:
    """Recursively fetch an item and its comment tree."""
    raw = await client.get_item(item_id)
    if raw is None:
        return []

    items = [_item_from_raw(raw, salt)]
    if depth >= _MAX_DEPTH or len(items) >= _MAX_COMMENTS:
        return items

    kid_ids: list[int] = raw.get("kids") or []
    for kid_id in kid_ids[:50]:  # cap per-level fanout
        items.extend(await _fetch_tree(client, kid_id, salt, depth + 1))
        if len(items) >= _MAX_COMMENTS:
            break
    return items


@app.task(name="thread_harvester.harvest_threads")
def harvest_threads(limit: int = 10) -> int:
    """Fetch watchlist stories + comment trees and store in hn_item."""
    config = AgentConfig()
    conn = duckdb.connect(config.db_path)
    init_schema(conn)
    repo = HNItemRepository(conn)
    watchlist = WatchlistRepository(conn)
    redis = Redis.from_url(config.redis_url)
    publisher = EventPublisher(redis)

    try:
        now = int(time.time())
        entries = watchlist.get_active(now, limit=limit)
        total = 0

        for entry in entries:
            items = asyncio.run(
                _fetch_tree(FirebaseHNClient(), entry.story_id, config.author_salt)
            )
            for item in items:
                repo.upsert(item)
            watchlist.mark_fetched(entry.story_id, now)
            publisher.publish(
                HN_CONTENT,
                {"story_id": entry.story_id, "items_count": len(items)},
            )
            total += len(items)
        return total
    finally:
        conn.close()
        redis.close()
