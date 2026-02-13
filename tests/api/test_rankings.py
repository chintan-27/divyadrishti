import duckdb
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.routes import metrics, rankings, stories, stream
from libs.schemas.metric_rollup import MetricRollup
from libs.storage.metric_rollup_repository import MetricRollupRepository
from libs.storage.schema import init_schema


def _setup():
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    stories.set_db(conn)
    stream.set_db(conn)
    metrics.set_db(conn)
    rankings.set_db(conn)
    return conn, TestClient(app)


def test_rankings_empty():
    conn, client = _setup()
    resp = client.get("/rankings?window=today&lens=top")
    assert resp.status_code == 200
    assert resp.json() == []
    conn.close()


def test_rankings_top():
    conn, client = _setup()
    repo = MetricRollupRepository(conn)
    repo.upsert(MetricRollup(
        node_id="n1", window="today", bucket_start=1000,
        presence=0.8, heat_score=10.0,
    ))
    repo.upsert(MetricRollup(
        node_id="n2", window="today", bucket_start=1000,
        presence=0.3, heat_score=50.0,
    ))
    resp = client.get("/rankings?window=today&lens=top")
    data = resp.json()
    assert len(data) == 2
    assert data[0]["node_id"] == "n1"  # higher presence
    conn.close()


def test_rankings_heated():
    conn, client = _setup()
    repo = MetricRollupRepository(conn)
    repo.upsert(MetricRollup(
        node_id="n1", window="today", bucket_start=1000, heat_score=10.0,
    ))
    repo.upsert(MetricRollup(
        node_id="n2", window="today", bucket_start=1000, heat_score=50.0,
    ))
    resp = client.get("/rankings?window=today&lens=heated")
    data = resp.json()
    assert data[0]["node_id"] == "n2"  # higher heat
    conn.close()
