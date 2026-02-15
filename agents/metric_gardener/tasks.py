from __future__ import annotations

import uuid

from agents.celery_app import app, get_worker_conn
from agents.metric_gardener.topic_discovery import (
    anchor_topics,
    discover_topics,
    reconcile_topics,
)
from libs.schemas.metric_node import MetricNode
from libs.storage.metric_node_repository import MetricNodeRepository

_MIN_ITEMS = 10


@app.task(name="metric_gardener.garden_metrics")
def garden_metrics() -> int:
    """Discover and maintain metric nodes using LLM-guided topic discovery."""
    conn = get_worker_conn()
    node_repo = MetricNodeRepository(conn)

    try:
        rows = conn.execute(
            "SELECT COALESCE(h.title, '') || ' ' || COALESCE(h.text_clean, '') "
            "FROM hn_item h "
            "WHERE h.text_clean IS NOT NULL OR h.title IS NOT NULL "
            "ORDER BY h.\"time\" DESC LIMIT 100"
        ).fetchall()

        if len(rows) < _MIN_ITEMS:
            return 0

        texts = [r[0].strip() for r in rows if r[0].strip()]
        if len(texts) < _MIN_ITEMS:
            return 0

        # Phase 1: Discover topics from recent content
        raw_topics = discover_topics(texts)
        if not raw_topics:
            return 0

        # Phase 2: Create centroid embeddings for each topic
        anchored = anchor_topics(raw_topics)

        # Phase 3: Reconcile with existing nodes
        existing = [
            (n.node_id, n.label, n.centroid)
            for n in node_repo.get_active()
        ]
        to_create, to_update, to_retire = reconcile_topics(anchored, existing)

        count = 0

        # Create new nodes
        for topic in to_create:
            node_id = f"auto-{uuid.uuid4().hex[:12]}"
            node_repo.upsert(MetricNode(
                node_id=node_id,
                label=str(topic.get("label", "")),
                definition=str(topic.get("definition", "")),
                centroid=topic.get("centroid", []),  # type: ignore[arg-type]
                status="active",
            ))
            count += 1

        # Update merged nodes
        for update in to_update:
            node_repo.upsert(MetricNode(
                node_id=str(update["node_id"]),
                label=str(update.get("label", "")),
                definition=str(update.get("definition", "")),
                centroid=update.get("centroid", []),  # type: ignore[arg-type]
                status="active",
            ))
            count += 1

        # Retire stale nodes
        for node_id in to_retire:
            existing_node = node_repo.get_by_id(node_id)
            if existing_node:
                existing_node.status = "retired"
                node_repo.upsert(existing_node)

        return count
    finally:
        conn.close()
