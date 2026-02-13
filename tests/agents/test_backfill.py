from unittest.mock import AsyncMock, patch

import duckdb

from agents.trend_scout.backfill import backfill_stories
from libs.storage.backfill_state_repository import BackfillStateRepository
from libs.storage.schema import init_schema
from libs.storage.watchlist_repository import WatchlistRepository
from tests.agents.test_normalizer import _ConnWrapper


def test_backfill_stories():
    conn = duckdb.connect(":memory:")
    init_schema(conn)

    mock_hits = [
        {"objectID": "100", "points": 50},
        {"objectID": "200", "points": 100},
    ]

    wrapper = _ConnWrapper(conn)
    with (
        patch("agents.trend_scout.backfill.duckdb") as mock_duckdb,
        patch("agents.trend_scout.backfill.AlgoliaHNClient") as mock_algolia_cls,
    ):
        mock_duckdb.connect.return_value = wrapper

        mock_client = AsyncMock()
        mock_client.search_by_date.return_value = mock_hits
        mock_client.close = AsyncMock()
        mock_algolia_cls.return_value = mock_client

        count = backfill_stories()

    assert count == 2

    # verify checkpoint was set
    state = BackfillStateRepository(conn)
    checkpoint = state.get("backfill_checkpoint")
    assert checkpoint is not None
    assert int(checkpoint) > 0

    # verify watchlist entries
    watchlist = WatchlistRepository(conn)
    active = watchlist.get_active(now_ts=0)
    assert len(active) == 2
    conn.close()


def test_backfill_stories_resumes():
    conn = duckdb.connect(":memory:")
    init_schema(conn)

    # set checkpoint to recent past
    import time
    state = BackfillStateRepository(conn)
    state.set("backfill_checkpoint", str(int(time.time()) - 100), int(time.time()))

    wrapper = _ConnWrapper(conn)
    with (
        patch("agents.trend_scout.backfill.duckdb") as mock_duckdb,
        patch("agents.trend_scout.backfill.AlgoliaHNClient") as mock_algolia_cls,
    ):
        mock_duckdb.connect.return_value = wrapper

        mock_client = AsyncMock()
        mock_client.search_by_date.return_value = [{"objectID": "300", "points": 10}]
        mock_client.close = AsyncMock()
        mock_algolia_cls.return_value = mock_client

        count = backfill_stories()

    assert count == 1
    conn.close()
