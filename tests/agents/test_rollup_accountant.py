import time
from unittest.mock import patch

import duckdb

from agents.rollup_accountant.tasks import compute_rollups
from libs.schemas.hn_item import HNItem
from libs.schemas.item_metric_edge import ItemMetricEdge
from libs.schemas.metric_node import MetricNode
from libs.schemas.opinion_signal import OpinionSignal
from libs.storage.hn_item_repository import HNItemRepository
from libs.storage.item_metric_edge_repository import ItemMetricEdgeRepository
from libs.storage.metric_node_repository import MetricNodeRepository
from libs.storage.metric_rollup_repository import MetricRollupRepository
from libs.storage.opinion_signal_repository import OpinionSignalRepository
from libs.storage.schema import EMBEDDING_DIM, init_schema
from tests.agents.test_normalizer import _ConnWrapper


def test_compute_rollups():
    conn = duckdb.connect(":memory:")
    init_schema(conn)

    now = int(time.time())
    item_repo = HNItemRepository(conn)
    sig_repo = OpinionSignalRepository(conn)
    edge_repo = ItemMetricEdgeRepository(conn)
    node_repo = MetricNodeRepository(conn)

    # create a metric node
    node_repo.upsert(MetricNode(node_id="n1", label="Test", centroid=[0.1] * EMBEDDING_DIM))

    # create items with different authors and recent timestamps
    for i in range(1, 6):
        item_repo.upsert(HNItem(
            id=i, type="comment", by=f"user{i}",
            author_hash=f"hash{i}", time=now - 100,
            text_clean=f"comment {i}",
        ))
        sig_repo.upsert(OpinionSignal(
            item_id=i,
            valence=50.0 if i <= 3 else -30.0,
            intensity=0.8,
            confidence=0.9,
            label="positive" if i <= 3 else "negative",
        ))
        edge_repo.upsert(ItemMetricEdge(
            item_id=i, node_id="n1", weight=0.5, created_at=now,
        ))

    wrapper = _ConnWrapper(conn)
    with patch("agents.rollup_accountant.tasks.get_worker_conn", return_value=wrapper):
        count = compute_rollups()

    assert count > 0

    rollup_repo = MetricRollupRepository(conn)
    # should have at least the "hour" window rollup (min_authors=1)
    latest = rollup_repo.get_latest("n1", "hour")
    assert latest is not None
    assert latest.unique_authors == 5
    assert latest.sentiment_positive > 0
    assert latest.sentiment_negative > 0
    conn.close()
