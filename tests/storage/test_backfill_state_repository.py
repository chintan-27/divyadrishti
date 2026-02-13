import duckdb

from libs.storage.backfill_state_repository import BackfillStateRepository
from libs.storage.schema import init_schema


def _setup() -> tuple[duckdb.DuckDBPyConnection, BackfillStateRepository]:
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    return conn, BackfillStateRepository(conn)


def test_get_missing():
    conn, repo = _setup()
    assert repo.get("missing") is None
    conn.close()


def test_set_and_get():
    conn, repo = _setup()
    repo.set("checkpoint", "12345", 1000)
    assert repo.get("checkpoint") == "12345"
    conn.close()


def test_set_updates():
    conn, repo = _setup()
    repo.set("checkpoint", "100", 1000)
    repo.set("checkpoint", "200", 2000)
    assert repo.get("checkpoint") == "200"
    conn.close()
