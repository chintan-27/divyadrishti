import duckdb

from libs.schemas.item_metric_edge import ItemMetricEdge
from libs.storage.item_metric_edge_repository import ItemMetricEdgeRepository
from libs.storage.schema import init_schema


def _setup() -> tuple[duckdb.DuckDBPyConnection, ItemMetricEdgeRepository]:
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    return conn, ItemMetricEdgeRepository(conn)


def test_upsert_and_get_for_item():
    conn, repo = _setup()
    repo.upsert(ItemMetricEdge(item_id=1, node_id="n1", weight=0.8, created_at=1000))
    repo.upsert(ItemMetricEdge(item_id=1, node_id="n2", weight=0.2, created_at=1000))
    edges = repo.get_edges_for_item(1)
    assert len(edges) == 2
    conn.close()


def test_get_edges_for_node():
    conn, repo = _setup()
    repo.upsert(ItemMetricEdge(item_id=1, node_id="n1", weight=0.9))
    repo.upsert(ItemMetricEdge(item_id=2, node_id="n1", weight=0.5))
    repo.upsert(ItemMetricEdge(item_id=3, node_id="n2", weight=0.7))
    edges = repo.get_edges_for_node("n1")
    assert len(edges) == 2
    assert edges[0].weight == 0.9  # ordered desc
    conn.close()


def test_upsert_updates_weight():
    conn, repo = _setup()
    repo.upsert(ItemMetricEdge(item_id=1, node_id="n1", weight=0.5))
    repo.upsert(ItemMetricEdge(item_id=1, node_id="n1", weight=0.9))
    edges = repo.get_edges_for_item(1)
    assert len(edges) == 1
    assert edges[0].weight == 0.9
    conn.close()
