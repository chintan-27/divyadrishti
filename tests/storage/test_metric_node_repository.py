import duckdb

from libs.schemas.metric_node import MetricNode
from libs.storage.metric_node_repository import MetricNodeRepository
from libs.storage.schema import init_schema


def _setup() -> tuple[duckdb.DuckDBPyConnection, MetricNodeRepository]:
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    return conn, MetricNodeRepository(conn)


def test_upsert_and_get():
    conn, repo = _setup()
    centroid = [0.5] * 384
    node = MetricNode(node_id="n1", label="AI Safety", centroid=centroid)
    repo.upsert(node)
    result = repo.get_by_id("n1")
    assert result is not None
    assert result.label == "AI Safety"
    assert len(result.centroid) == 384
    conn.close()


def test_get_active():
    conn, repo = _setup()
    repo.upsert(MetricNode(node_id="n1", label="A", status="active"))
    repo.upsert(MetricNode(node_id="n2", label="B", status="inactive"))
    repo.upsert(MetricNode(node_id="n3", label="C", status="active"))
    active = repo.get_active()
    assert len(active) == 2
    conn.close()


def test_get_all_centroids():
    conn, repo = _setup()
    c1 = [1.0] * 384
    c2 = [2.0] * 384
    repo.upsert(MetricNode(node_id="n1", centroid=c1))
    repo.upsert(MetricNode(node_id="n2", centroid=c2, status="inactive"))
    centroids = repo.get_all_centroids()
    assert len(centroids) == 1
    assert centroids[0][0] == "n1"
    conn.close()


def test_get_not_found():
    conn, repo = _setup()
    assert repo.get_by_id("missing") is None
    conn.close()
