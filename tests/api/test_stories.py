import duckdb
from fastapi.testclient import TestClient

from apps.api.db import set_db
from apps.api.main import app
from libs.schemas.hn_item import HNItem
from libs.storage.hn_item_repository import HNItemRepository
from libs.storage.schema import init_schema


def _setup() -> tuple[duckdb.DuckDBPyConnection, TestClient, HNItemRepository]:
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    set_db(conn)
    repo = HNItemRepository(conn)
    return conn, TestClient(app), repo


def test_trending_empty():
    conn, client, _repo = _setup()
    resp = client.get("/stories/trending")
    assert resp.status_code == 200
    assert resp.json() == []
    conn.close()


def test_trending_returns_stories():
    conn, client, repo = _setup()
    repo.upsert(HNItem(id=1, type="story", title="A", score=100, time=1000))
    repo.upsert(HNItem(id=2, type="story", title="B", score=200, time=2000))
    repo.upsert(HNItem(id=3, type="comment", text="nope", time=3000))
    resp = client.get("/stories/trending")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["score"] == 200  # highest first
    conn.close()


def test_get_story():
    conn, client, repo = _setup()
    repo.upsert(HNItem(id=42, type="story", title="Hello", score=10))
    resp = client.get("/stories/42")
    assert resp.status_code == 200
    assert resp.json()["title"] == "Hello"
    conn.close()


def test_get_story_not_found():
    conn, client, _repo = _setup()
    resp = client.get("/stories/999")
    assert resp.status_code == 404
    conn.close()


def test_get_comments():
    conn, client, repo = _setup()
    repo.upsert(HNItem(id=1, type="story", title="S"))
    repo.upsert(HNItem(id=10, type="comment", parent=1, text="c1", time=100))
    repo.upsert(HNItem(id=11, type="comment", parent=1, text="c2", time=200))
    resp = client.get("/stories/1/comments")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["text"] == "c1"
    conn.close()
