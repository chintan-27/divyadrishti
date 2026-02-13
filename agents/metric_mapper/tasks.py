from __future__ import annotations

import time

import duckdb

from agents.celery_app import app
from agents.config import AgentConfig
from libs.nlp.embeddings import cosine_similarity, get_model, softmax_weights
from libs.schemas.embedding import Embedding
from libs.schemas.item_metric_edge import ItemMetricEdge
from libs.storage.embedding_repository import EmbeddingRepository
from libs.storage.item_metric_edge_repository import ItemMetricEdgeRepository
from libs.storage.metric_node_repository import MetricNodeRepository
from libs.storage.schema import init_schema

_TOP_K = 5
_MIN_WEIGHT = 0.12


@app.task(name="metric_mapper.map_items_to_metrics")
def map_items_to_metrics(batch_size: int = 50) -> int:
    """Embed items and map them to metric nodes."""
    config = AgentConfig()
    conn = duckdb.connect(config.db_path)
    init_schema(conn)
    emb_repo = EmbeddingRepository(conn)
    node_repo = MetricNodeRepository(conn)
    edge_repo = ItemMetricEdgeRepository(conn)

    try:
        # find items with text_clean but no embedding
        rows = conn.execute(
            "SELECT h.id, h.text_clean FROM hn_item h "
            "LEFT JOIN embedding e ON h.id = e.item_id "
            "WHERE h.text_clean IS NOT NULL AND e.item_id IS NULL "
            "LIMIT ?",
            [batch_size],
        ).fetchall()

        if not rows:
            return 0

        model = get_model()
        item_ids = [r[0] for r in rows]
        texts = [r[1] for r in rows]
        vectors = model.encode_batch(texts)

        # get all active centroids
        centroids = node_repo.get_all_centroids()
        now = int(time.time())
        count = 0

        for item_id, vec in zip(item_ids, vectors):
            emb_repo.upsert(Embedding(
                item_id=item_id, embedding=vec, model_version="all-MiniLM-L6-v2",
            ))

            if not centroids:
                count += 1
                continue

            # compute similarities
            sims = [cosine_similarity(vec, c) for _, c in centroids]

            # top-K indices
            indexed = sorted(enumerate(sims), key=lambda x: x[1], reverse=True)[:_TOP_K]
            top_indices = [i for i, _ in indexed]
            top_sims = [sims[i] for i in top_indices]

            # softmax weights
            weights = softmax_weights(top_sims)

            for idx, w in zip(top_indices, weights):
                if w >= _MIN_WEIGHT:
                    node_id = centroids[idx][0]
                    edge_repo.upsert(ItemMetricEdge(
                        item_id=item_id, node_id=node_id,
                        weight=round(w, 4), created_at=now,
                    ))
            count += 1

        return count
    finally:
        conn.close()
