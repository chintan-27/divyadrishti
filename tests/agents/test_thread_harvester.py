import json
from unittest.mock import AsyncMock, patch

import duckdb
import fakeredis

from agents.thread_harvester.tasks import _item_from_raw, harvest_threads
from libs.schemas.watchlist import WatchlistEntry
from libs.storage.hn_item_repository import HNItemRepository
from libs.storage.schema import init_schema
from libs.storage.watchlist_repository import WatchlistRepository
from tests.agents.test_normalizer import _ConnWrapper


def test_item_from_raw():
    raw = {"id": 1, "type": "story", "by": "pg", "time": 1000, "title": "Hello"}
    item = _item_from_raw(raw, "salt")
    assert item.id == 1
    assert item.by == "pg"
    assert item.author_hash is not None
    assert len(item.author_hash) == 64


def test_item_from_raw_no_author():
    raw = {"id": 1, "type": "story"}
    item = _item_from_raw(raw, "salt")
    assert item.author_hash is None


def test_harvest_threads():
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    watchlist = WatchlistRepository(conn)
    watchlist.upsert(WatchlistEntry(story_id=100, priority_score=5.0, ttl_expires=9999999999))

    redis = fakeredis.FakeRedis()

    story_raw = {"id": 100, "type": "story", "by": "pg", "kids": [101], "title": "Hi"}
    comment_raw = {"id": 101, "type": "comment", "by": "alice", "parent": 100, "text": "Nice"}

    async def mock_get_item(item_id):
        return {100: story_raw, 101: comment_raw}.get(item_id)

    wrapper = _ConnWrapper(conn)
    with (
        patch("agents.thread_harvester.tasks.get_worker_conn", return_value=wrapper),
        patch("agents.thread_harvester.tasks.Redis") as mock_redis_cls,
        patch("agents.thread_harvester.tasks.FirebaseHNClient") as mock_fb_cls,
    ):
        mock_redis_cls.from_url.return_value = redis

        mock_client = AsyncMock()
        mock_client.get_item = AsyncMock(side_effect=mock_get_item)
        mock_client.close = AsyncMock()
        mock_fb_cls.return_value = mock_client

        total = harvest_threads(limit=10)

    assert total == 2

    messages = redis.xrange("hn.content")
    assert len(messages) == 1
    data = json.loads(messages[0][1][b"data"])
    assert data["story_id"] == 100
    assert data["items_count"] == 2
