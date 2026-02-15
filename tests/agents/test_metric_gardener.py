from unittest.mock import MagicMock, patch

import duckdb
import numpy as np

from agents.metric_gardener.tasks import garden_metrics
from agents.metric_gardener.topic_discovery import reconcile_topics
from libs.nlp.embeddings import cosine_similarity
from libs.schemas.hn_item import HNItem
from libs.storage.hn_item_repository import HNItemRepository
from libs.storage.metric_node_repository import MetricNodeRepository
from libs.storage.schema import EMBEDDING_DIM, init_schema
from tests.agents.test_normalizer import _ConnWrapper


def test_reconcile_creates_new():
    centroid = [0.5] * EMBEDDING_DIM
    new_topics = [{"label": "AI Safety", "definition": "Concerns about AI", "centroid": centroid}]
    to_create, to_update, to_retire = reconcile_topics(new_topics, [])
    assert len(to_create) == 1
    assert to_create[0]["label"] == "AI Safety"
    assert len(to_update) == 0
    assert len(to_retire) == 0


def test_reconcile_merges_similar():
    centroid = [0.5] * EMBEDDING_DIM
    new_topics = [{"label": "AI Safety", "definition": "Concerns about AI", "centroid": centroid}]
    existing = [("n1", "AI Alignment", centroid)]  # identical centroid = sim 1.0
    to_create, to_update, to_retire = reconcile_topics(new_topics, existing)
    assert len(to_create) == 0
    assert len(to_update) == 1
    assert to_update[0]["node_id"] == "n1"
    assert len(to_retire) == 0


def test_reconcile_retires_unmatched():
    centroid_a = [1.0] + [0.0] * (EMBEDDING_DIM - 1)
    centroid_b = [0.0] + [1.0] + [0.0] * (EMBEDDING_DIM - 2)
    new_topics = [{"label": "Topic A", "centroid": centroid_a}]
    existing = [("n1", "Topic B", centroid_b)]  # orthogonal = no match
    to_create, to_update, to_retire = reconcile_topics(new_topics, existing)
    assert len(to_create) == 1
    assert len(to_retire) == 1
    assert to_retire[0] == "n1"


def test_garden_metrics():
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    item_repo = HNItemRepository(conn)

    # create 30 items
    for i in range(1, 31):
        item_repo.upsert(HNItem(
            id=i, type="comment", text_clean=f"discussion about topic {i}",
        ))

    mock_topics = [
        {"label": "AI Safety", "definition": "AI risk concerns", "keywords": ["AI", "safety"]},
        {"label": "Rust Lang", "definition": "Rust programming", "keywords": ["rust", "memory"]},
    ]
    mock_centroids = [
        [0.5] * EMBEDDING_DIM,
        [0.3] * EMBEDDING_DIM,
    ]

    def mock_anchor(topics):
        for topic, centroid in zip(topics, mock_centroids):
            topic["centroid"] = centroid
        return topics

    wrapper = _ConnWrapper(conn)
    with (
        patch("agents.metric_gardener.tasks.get_worker_conn", return_value=wrapper),
        patch("agents.metric_gardener.tasks.discover_topics", return_value=mock_topics),
        patch("agents.metric_gardener.tasks.anchor_topics", side_effect=mock_anchor),
    ):
        count = garden_metrics()

    assert count == 2

    node_repo = MetricNodeRepository(conn)
    active = node_repo.get_active()
    assert len(active) == 2
    labels = {n.label for n in active}
    assert "AI Safety" in labels
    assert "Rust Lang" in labels
    for node in active:
        assert len(node.centroid) == EMBEDDING_DIM
    conn.close()


def test_garden_metrics_too_few_items():
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    item_repo = HNItemRepository(conn)

    # only 5 items - below minimum
    for i in range(1, 6):
        item_repo.upsert(HNItem(id=i, type="comment", text_clean=f"text {i}"))

    wrapper = _ConnWrapper(conn)
    with patch("agents.metric_gardener.tasks.get_worker_conn", return_value=wrapper):
        count = garden_metrics()

    assert count == 0
    conn.close()
