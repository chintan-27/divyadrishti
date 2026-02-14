from __future__ import annotations

import uuid

import numpy as np
from sklearn.cluster import MiniBatchKMeans

from agents.celery_app import app, get_worker_conn
from agents.metric_gardener.labeling import generate_label
from libs.schemas.metric_node import MetricNode
from libs.storage.metric_node_repository import MetricNodeRepository

_MIN_EMBEDDINGS = 20
_MAX_CLUSTERS = 50


@app.task(name="metric_gardener.garden_metrics")
def garden_metrics(n_clusters: int | None = None) -> int:
    """Cluster embeddings to discover/update metric nodes."""
    conn = get_worker_conn()
    node_repo = MetricNodeRepository(conn)

    try:
        rows = conn.execute(
            "SELECT e.item_id, e.embedding, h.text_clean "
            "FROM embedding e JOIN hn_item h ON e.item_id = h.id "
            "WHERE h.text_clean IS NOT NULL"
        ).fetchall()

        if len(rows) < _MIN_EMBEDDINGS:
            return 0

        item_ids = [r[0] for r in rows]
        vectors = np.array([list(r[1]) for r in rows], dtype=np.float32)
        texts = [r[2] for r in rows]

        k = n_clusters or min(max(len(rows) // 10, 3), _MAX_CLUSTERS)
        kmeans = MiniBatchKMeans(n_clusters=k, random_state=42, batch_size=100, n_init=3)
        labels = kmeans.fit_predict(vectors)
        centroids = kmeans.cluster_centers_

        count = 0
        for cluster_idx in range(k):
            mask = labels == cluster_idx
            cluster_texts = [texts[i] for i in range(len(texts)) if mask[i]]
            if len(cluster_texts) < 2:
                continue

            centroid = centroids[cluster_idx].tolist()
            label, definition = generate_label(cluster_texts)
            node_id = f"auto-{uuid.uuid4().hex[:12]}"

            node_repo.upsert(MetricNode(
                node_id=node_id,
                label=label,
                definition=definition,
                centroid=centroid,
                status="active",
            ))
            count += 1

        return count
    finally:
        conn.close()
