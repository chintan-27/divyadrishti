import duckdb
from fastapi.testclient import TestClient

from apps.api.db import set_db
from apps.api.main import app
from libs.schemas.metric_node import MetricNode
from libs.schemas.metric_rollup import MetricRollup
from libs.storage.metric_node_repository import MetricNodeRepository
from libs.storage.metric_rollup_repository import MetricRollupRepository
from libs.storage.schema import init_schema


def _setup():
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    set_db(conn)
    return conn, TestClient(app)


def test_rankings_empty():
    conn, client = _setup()
    resp = client.get("/rankings?window=today&lens=top")
    assert resp.status_code == 200
    assert resp.json() == []
    conn.close()


def test_rankings_top():
    conn, client = _setup()
    node_repo = MetricNodeRepository(conn)
    node_repo.upsert(MetricNode(node_id="n1", label="AI", centroid=[0.1] * 384))
    node_repo.upsert(MetricNode(node_id="n2", label="Rust", centroid=[0.2] * 384))
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
    assert data[0]["rank"] == 1
    assert data[0]["metric"]["id"] == "n1"  # higher presence
    conn.close()


def test_rankings_heated():
    conn, client = _setup()
    node_repo = MetricNodeRepository(conn)
    node_repo.upsert(MetricNode(node_id="n1", label="AI", centroid=[0.1] * 384))
    node_repo.upsert(MetricNode(node_id="n2", label="Rust", centroid=[0.2] * 384))
    repo = MetricRollupRepository(conn)
    repo.upsert(MetricRollup(
        node_id="n1", window="today", bucket_start=1000, heat_score=10.0,
    ))
    repo.upsert(MetricRollup(
        node_id="n2", window="today", bucket_start=1000, heat_score=50.0,
    ))
    resp = client.get("/rankings?window=today&lens=heated")
    data = resp.json()
    assert data[0]["metric"]["id"] == "n2"  # higher heat
    conn.close()
