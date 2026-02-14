from unittest.mock import MagicMock, patch

import duckdb

from agents.metric_mapper.tasks import map_items_to_metrics
from libs.schemas.hn_item import HNItem
from libs.schemas.metric_node import MetricNode
from libs.storage.embedding_repository import EmbeddingRepository
from libs.storage.hn_item_repository import HNItemRepository
from libs.storage.item_metric_edge_repository import ItemMetricEdgeRepository
from libs.storage.metric_node_repository import MetricNodeRepository
from libs.storage.schema import init_schema
from tests.agents.test_normalizer import _ConnWrapper


def test_map_items_to_metrics():
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    repo = HNItemRepository(conn)
    repo.upsert(HNItem(id=1, type="comment", text_clean="AI safety is important"))
    repo.upsert(HNItem(id=2, type="comment", text_clean="Python programming rocks"))

    # add metric nodes with centroids
    node_repo = MetricNodeRepository(conn)
    node_repo.upsert(MetricNode(node_id="n1", label="AI", centroid=[0.5] * 384))
    node_repo.upsert(MetricNode(node_id="n2", label="Programming", centroid=[0.3] * 384))

    mock_model = MagicMock()
    mock_model.encode_batch.return_value = [
        [0.5] * 384,  # similar to n1
        [0.3] * 384,  # similar to n2
    ]

    wrapper = _ConnWrapper(conn)
    with (
        patch("agents.metric_mapper.tasks.get_worker_conn", return_value=wrapper),
        patch("agents.metric_mapper.tasks.get_model", return_value=mock_model),
    ):
        count = map_items_to_metrics()

    assert count == 2

    # verify embeddings stored
    emb_repo = EmbeddingRepository(conn)
    assert emb_repo.get_by_item_id(1) is not None
    assert emb_repo.get_by_item_id(2) is not None

    # verify edges created
    edge_repo = ItemMetricEdgeRepository(conn)
    edges1 = edge_repo.get_edges_for_item(1)
    assert len(edges1) > 0
    conn.close()


def test_map_items_no_centroids():
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    repo = HNItemRepository(conn)
    repo.upsert(HNItem(id=1, type="comment", text_clean="hello world"))

    mock_model = MagicMock()
    mock_model.encode_batch.return_value = [[0.1] * 384]

    wrapper = _ConnWrapper(conn)
    with (
        patch("agents.metric_mapper.tasks.get_worker_conn", return_value=wrapper),
        patch("agents.metric_mapper.tasks.get_model", return_value=mock_model),
    ):
        count = map_items_to_metrics()

    assert count == 1
    # embedding still stored even without centroids
    emb_repo = EmbeddingRepository(conn)
    assert emb_repo.get_by_item_id(1) is not None
    conn.close()
