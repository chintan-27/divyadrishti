import duckdb

from libs.schemas.hn_item import HNItem
from libs.storage.hn_item_repository import HNItemRepository
from libs.storage.schema import init_schema


def _setup() -> tuple[duckdb.DuckDBPyConnection, HNItemRepository]:
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    return conn, HNItemRepository(conn)


def test_insert_and_get():
    conn, repo = _setup()
    item = HNItem(id=1, type="story", by="pg", time=1000, title="Hello")
    repo.upsert(item)
    result = repo.get_by_id(1)
    assert result is not None
    assert result.id == 1
    assert result.title == "Hello"
    assert result.by == "pg"
    conn.close()


def test_upsert_updates_existing():
    conn, repo = _setup()
    repo.upsert(HNItem(id=1, type="story", title="v1", score=10))
    repo.upsert(HNItem(id=1, score=42))
    result = repo.get_by_id(1)
    assert result is not None
    assert result.score == 42
    assert result.title == "v1"  # preserved via COALESCE
    conn.close()


def test_get_by_id_not_found():
    conn, repo = _setup()
    assert repo.get_by_id(999) is None
    conn.close()


def test_get_by_ids():
    conn, repo = _setup()
    for i in range(1, 4):
        repo.upsert(HNItem(id=i, type="story", time=i * 100))
    results = repo.get_by_ids([1, 3])
    assert len(results) == 2
    ids = {r.id for r in results}
    assert ids == {1, 3}
    conn.close()


def test_get_by_ids_empty():
    _, repo = _setup()
    assert repo.get_by_ids([]) == []


def test_get_recent():
    conn, repo = _setup()
    for i in range(1, 6):
        repo.upsert(HNItem(id=i, type="story", time=i * 100))
    results = repo.get_recent(limit=3)
    assert len(results) == 3
    assert results[0].time == 500
    conn.close()


def test_get_recent_with_type_filter():
    conn, repo = _setup()
    repo.upsert(HNItem(id=1, type="story", time=100))
    repo.upsert(HNItem(id=2, type="comment", time=200))
    repo.upsert(HNItem(id=3, type="story", time=300))
    results = repo.get_recent(limit=10, type_filter="story")
    assert len(results) == 2
    assert all(r.type == "story" for r in results)
    conn.close()


def test_kids_array():
    conn, repo = _setup()
    repo.upsert(HNItem(id=1, type="story", kids=[10, 20, 30]))
    result = repo.get_by_id(1)
    assert result is not None
    assert result.kids == [10, 20, 30]
    conn.close()
