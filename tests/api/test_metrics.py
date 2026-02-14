import duckdb
from fastapi.testclient import TestClient

from apps.api.db import set_db
from apps.api.main import app
from libs.schemas.hn_item import HNItem
from libs.schemas.item_metric_edge import ItemMetricEdge
from libs.schemas.metric_node import MetricNode
from libs.storage.hn_item_repository import HNItemRepository
from libs.storage.item_metric_edge_repository import ItemMetricEdgeRepository
from libs.storage.metric_node_repository import MetricNodeRepository
from libs.storage.schema import init_schema


def _setup():
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    set_db(conn)
    return conn, TestClient(app)


def test_top_metrics_empty():
    conn, client = _setup()
    resp = client.get("/metrics/top")
    assert resp.status_code == 200
    assert resp.json() == []
    conn.close()


def test_top_metrics():
    conn, client = _setup()
    node_repo = MetricNodeRepository(conn)
    node_repo.upsert(MetricNode(node_id="n1", label="AI", centroid=[0.1] * 384))
    node_repo.upsert(MetricNode(node_id="n2", label="Rust", centroid=[0.2] * 384))

    edge_repo = ItemMetricEdgeRepository(conn)
    item_repo = HNItemRepository(conn)
    item_repo.upsert(HNItem(id=1, type="story"))
    item_repo.upsert(HNItem(id=2, type="story"))
    edge_repo.upsert(ItemMetricEdge(item_id=1, node_id="n1", weight=0.8))
    edge_repo.upsert(ItemMetricEdge(item_id=2, node_id="n1", weight=0.5))
    edge_repo.upsert(ItemMetricEdge(item_id=1, node_id="n2", weight=0.3))

    resp = client.get("/metrics/top")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 2
    assert data[0]["id"] == "n1"  # most items
    assert data[0]["item_count"] == 2
    conn.close()


def test_get_metric():
    conn, client = _setup()
    node_repo = MetricNodeRepository(conn)
    node_repo.upsert(MetricNode(node_id="n1", label="AI", centroid=[0.1] * 384))
    resp = client.get("/metrics/n1")
    assert resp.status_code == 200
    assert resp.json()["label"] == "AI"
    conn.close()


def test_get_metric_not_found():
    conn, client = _setup()
    resp = client.get("/metrics/missing")
    assert resp.status_code == 404
    conn.close()


def test_get_metric_examples():
    conn, client = _setup()
    node_repo = MetricNodeRepository(conn)
    node_repo.upsert(MetricNode(node_id="n1", label="AI", centroid=[0.1] * 384))
    item_repo = HNItemRepository(conn)
    item_repo.upsert(HNItem(id=1, type="story", title="AI News", text_clean="about AI"))
    edge_repo = ItemMetricEdgeRepository(conn)
    edge_repo.upsert(ItemMetricEdge(item_id=1, node_id="n1", weight=0.9))

    resp = client.get("/metrics/n1/examples")
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["title"] == "AI News"
    conn.close()
