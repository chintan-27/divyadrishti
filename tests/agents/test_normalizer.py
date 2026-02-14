from unittest.mock import patch

import duckdb

from agents.normalizer.tasks import normalize_items
from libs.schemas.hn_item import HNItem
from libs.storage.hn_item_repository import HNItemRepository
from libs.storage.schema import init_schema


class _ConnWrapper:
    """Wrapper that delegates to real conn but makes close() a no-op."""

    def __init__(self, conn: duckdb.DuckDBPyConnection) -> None:
        self._conn = conn

    def execute(self, *args, **kwargs):
        return self._conn.execute(*args, **kwargs)

    def close(self) -> None:
        pass  # no-op so tests can verify after


def test_normalize_items():
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    repo = HNItemRepository(conn)
    repo.upsert(HNItem(id=1, type="comment", text="<b>Hello</b> world"))
    repo.upsert(HNItem(id=2, type="comment", text="<p>Second<p>paragraph"))
    repo.upsert(HNItem(id=3, type="comment", text_clean="already clean"))

    wrapper = _ConnWrapper(conn)
    with patch("agents.normalizer.tasks.get_worker_conn", return_value=wrapper):
        count = normalize_items()

    assert count == 2
    item1 = repo.get_by_id(1)
    assert item1 is not None
    assert item1.text_clean == "Hello world"

    item3 = repo.get_by_id(3)
    assert item3 is not None
    assert item3.text_clean == "already clean"
    conn.close()


def test_normalize_items_skips_empty():
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    repo = HNItemRepository(conn)
    repo.upsert(HNItem(id=1, type="comment", text=""))

    wrapper = _ConnWrapper(conn)
    with patch("agents.normalizer.tasks.get_worker_conn", return_value=wrapper):
        count = normalize_items()

    assert count == 0
    conn.close()
