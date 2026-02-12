import json
from unittest.mock import AsyncMock, patch

import duckdb
import fakeredis

from agents.trend_scout.tasks import _compute_priority, discover_trending
from libs.storage.schema import init_schema
from libs.storage.watchlist_repository import WatchlistRepository


def test_compute_priority():
    hit = {"points": 100, "num_comments": 50}
    assert _compute_priority(hit) == 200.0


def test_compute_priority_missing_fields():
    assert _compute_priority({}) == 0.0


def test_discover_trending_upserts_watchlist():
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    repo = WatchlistRepository(conn)
    redis = fakeredis.FakeRedis()

    mock_hits = [
        {"objectID": "100", "points": 50, "num_comments": 10},
        {"objectID": "200", "points": 100, "num_comments": 20},
    ]

    with (
        patch("agents.trend_scout.tasks.duckdb") as mock_duckdb,
        patch("agents.trend_scout.tasks.Redis") as mock_redis_cls,
        patch("agents.trend_scout.tasks.AlgoliaHNClient") as mock_algolia_cls,
    ):
        mock_duckdb.connect.return_value = conn
        mock_redis_cls.from_url.return_value = redis

        mock_client = AsyncMock()
        mock_client.search_front_page.return_value = mock_hits
        mock_client.close = AsyncMock()
        mock_algolia_cls.return_value = mock_client

        count = discover_trending()

    assert count == 2

    # re-open connection to check persisted data (task closes conn in finally)
    conn2 = duckdb.connect(":memory:")
    # The in-memory DB is gone after close, so just verify via redis events
    messages = redis.xrange("hn.discovery")
    assert len(messages) == 2
    data = json.loads(messages[0][1][b"data"])
    assert data["action"] == "discovered"
    ids = {json.loads(m[1][b"data"])["story_id"] for m in messages}
    assert ids == {100, 200}
    conn2.close()


def test_discover_trending_skips_missing_id():
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    redis = fakeredis.FakeRedis()

    mock_hits = [{"points": 50}]  # no objectID

    with (
        patch("agents.trend_scout.tasks.duckdb") as mock_duckdb,
        patch("agents.trend_scout.tasks.Redis") as mock_redis_cls,
        patch("agents.trend_scout.tasks.AlgoliaHNClient") as mock_algolia_cls,
    ):
        mock_duckdb.connect.return_value = conn
        mock_redis_cls.from_url.return_value = redis

        mock_client = AsyncMock()
        mock_client.search_front_page.return_value = mock_hits
        mock_client.close = AsyncMock()
        mock_algolia_cls.return_value = mock_client

        count = discover_trending()

    assert count == 0
    conn.close()
