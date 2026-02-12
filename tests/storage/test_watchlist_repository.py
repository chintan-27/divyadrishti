import duckdb

from libs.schemas.watchlist import WatchlistEntry
from libs.storage.schema import init_schema
from libs.storage.watchlist_repository import WatchlistRepository


def _setup() -> tuple[duckdb.DuckDBPyConnection, WatchlistRepository]:
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    return conn, WatchlistRepository(conn)


def test_upsert_and_get_active():
    conn, repo = _setup()
    entry = WatchlistEntry(story_id=100, priority_score=5.0, ttl_expires=2000)
    repo.upsert(entry)
    active = repo.get_active(now_ts=1000)
    assert len(active) == 1
    assert active[0].story_id == 100
    assert active[0].priority_score == 5.0
    conn.close()


def test_upsert_updates_existing():
    conn, repo = _setup()
    repo.upsert(WatchlistEntry(story_id=1, priority_score=1.0, ttl_expires=2000))
    repo.upsert(WatchlistEntry(story_id=1, priority_score=9.0, ttl_expires=3000))
    active = repo.get_active(now_ts=1000)
    assert len(active) == 1
    assert active[0].priority_score == 9.0
    assert active[0].ttl_expires == 3000
    conn.close()


def test_get_active_filters_expired():
    conn, repo = _setup()
    repo.upsert(WatchlistEntry(story_id=1, priority_score=5.0, ttl_expires=500))
    repo.upsert(WatchlistEntry(story_id=2, priority_score=3.0, ttl_expires=2000))
    active = repo.get_active(now_ts=1000)
    assert len(active) == 1
    assert active[0].story_id == 2
    conn.close()


def test_get_active_orders_by_priority():
    conn, repo = _setup()
    repo.upsert(WatchlistEntry(story_id=1, priority_score=1.0, ttl_expires=5000))
    repo.upsert(WatchlistEntry(story_id=2, priority_score=9.0, ttl_expires=5000))
    repo.upsert(WatchlistEntry(story_id=3, priority_score=5.0, ttl_expires=5000))
    active = repo.get_active(now_ts=1000)
    assert [e.story_id for e in active] == [2, 3, 1]
    conn.close()


def test_get_active_respects_limit():
    conn, repo = _setup()
    for i in range(1, 6):
        repo.upsert(WatchlistEntry(story_id=i, priority_score=float(i), ttl_expires=5000))
    active = repo.get_active(now_ts=1000, limit=2)
    assert len(active) == 2
    conn.close()


def test_mark_fetched():
    conn, repo = _setup()
    repo.upsert(WatchlistEntry(story_id=1, priority_score=5.0, ttl_expires=5000))
    repo.mark_fetched(1, now_ts=3000)
    active = repo.get_active(now_ts=1000)
    assert active[0].last_fetched == 3000
    conn.close()


def test_remove_expired():
    conn, repo = _setup()
    repo.upsert(WatchlistEntry(story_id=1, priority_score=5.0, ttl_expires=500))
    repo.upsert(WatchlistEntry(story_id=2, priority_score=3.0, ttl_expires=1000))
    repo.upsert(WatchlistEntry(story_id=3, priority_score=7.0, ttl_expires=2000))
    removed = repo.remove_expired(now_ts=1000)
    assert removed == 2
    active = repo.get_active(now_ts=0)
    assert len(active) == 1
    assert active[0].story_id == 3
    conn.close()
