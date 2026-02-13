import duckdb

from libs.schemas.metric_rollup import MetricRollup
from libs.storage.metric_rollup_repository import MetricRollupRepository
from libs.storage.schema import init_schema


def _setup() -> tuple[duckdb.DuckDBPyConnection, MetricRollupRepository]:
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    return conn, MetricRollupRepository(conn)


def test_upsert_and_get_latest():
    conn, repo = _setup()
    repo.upsert(MetricRollup(node_id="n1", window="today", bucket_start=1000,
                              presence=0.5, valence_score=30.0, unique_authors=10))
    repo.upsert(MetricRollup(node_id="n1", window="today", bucket_start=2000,
                              presence=0.7, valence_score=40.0, unique_authors=15))
    latest = repo.get_latest("n1", "today")
    assert latest is not None
    assert latest.bucket_start == 2000
    assert latest.presence == 0.7
    conn.close()


def test_get_latest_not_found():
    conn, repo = _setup()
    assert repo.get_latest("missing", "today") is None
    conn.close()


def test_upsert_updates():
    conn, repo = _setup()
    repo.upsert(MetricRollup(node_id="n1", window="today", bucket_start=1000, presence=0.5))
    repo.upsert(MetricRollup(node_id="n1", window="today", bucket_start=1000, presence=0.9))
    latest = repo.get_latest("n1", "today")
    assert latest is not None
    assert latest.presence == 0.9
    conn.close()


def test_get_series():
    conn, repo = _setup()
    for i in range(5):
        repo.upsert(MetricRollup(node_id="n1", window="hour",
                                  bucket_start=1000 + i * 3600, presence=float(i) / 10))
    series = repo.get_series("n1", "hour", 1000, 1000 + 3 * 3600)
    assert len(series) == 4
    assert series[0].bucket_start == 1000
    conn.close()


def test_get_top_by_field():
    conn, repo = _setup()
    repo.upsert(MetricRollup(node_id="n1", window="today", bucket_start=1000,
                              heat_score=10.0))
    repo.upsert(MetricRollup(node_id="n2", window="today", bucket_start=1000,
                              heat_score=50.0))
    top = repo.get_top_by_field("today", "heat_score", limit=2)
    assert len(top) == 2
    assert top[0].node_id == "n2"
    conn.close()
