from unittest.mock import patch

import duckdb
import numpy as np

from agents.metric_gardener.labeling import generate_label
from agents.metric_gardener.tasks import garden_metrics
from libs.schemas.embedding import Embedding
from libs.schemas.hn_item import HNItem
from libs.storage.embedding_repository import EmbeddingRepository
from libs.storage.hn_item_repository import HNItemRepository
from libs.storage.metric_node_repository import MetricNodeRepository
from libs.storage.schema import init_schema
from tests.agents.test_normalizer import _ConnWrapper


def test_generate_label():
    texts = [
        "machine learning model training",
        "deep learning neural network",
        "training a machine learning classifier",
    ]
    label, definition = generate_label(texts)
    assert label  # non-empty
    assert "related to" in definition.lower()


def test_generate_label_empty():
    label, definition = generate_label([])
    assert label == "unknown"


def test_garden_metrics():
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    item_repo = HNItemRepository(conn)
    emb_repo = EmbeddingRepository(conn)

    rng = np.random.RandomState(42)
    # create 30 items in 2 clusters
    for i in range(1, 31):
        text = f"topic {'alpha' if i <= 15 else 'beta'} discussion {i}"
        item_repo.upsert(HNItem(id=i, type="comment", text_clean=text))
        if i <= 15:
            vec = (rng.randn(384) + 1.0).tolist()  # cluster around +1
        else:
            vec = (rng.randn(384) - 1.0).tolist()  # cluster around -1
        emb_repo.upsert(Embedding(item_id=i, embedding=vec))

    wrapper = _ConnWrapper(conn)
    with patch("agents.metric_gardener.tasks.duckdb") as mock_duckdb:
        mock_duckdb.connect.return_value = wrapper
        count = garden_metrics(n_clusters=3)

    assert count >= 2  # at least 2 clusters with enough items

    node_repo = MetricNodeRepository(conn)
    active = node_repo.get_active()
    assert len(active) >= 2
    for node in active:
        assert node.label
        assert len(node.centroid) == 384
    conn.close()


def test_garden_metrics_too_few_embeddings():
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    item_repo = HNItemRepository(conn)
    emb_repo = EmbeddingRepository(conn)

    # only 5 items - below minimum
    for i in range(1, 6):
        item_repo.upsert(HNItem(id=i, type="comment", text_clean=f"text {i}"))
        emb_repo.upsert(Embedding(item_id=i, embedding=[0.1] * 384))

    wrapper = _ConnWrapper(conn)
    with patch("agents.metric_gardener.tasks.duckdb") as mock_duckdb:
        mock_duckdb.connect.return_value = wrapper
        count = garden_metrics()

    assert count == 0
    conn.close()
