from __future__ import annotations

import time

import duckdb

from agents.celery_app import app
from agents.config import AgentConfig
from agents.rollup_accountant.formulas import (
    compute_consensus,
    compute_heat,
    compute_momentum,
    compute_split,
)
from libs.schemas.metric_rollup import MetricRollup
from libs.storage.metric_node_repository import MetricNodeRepository
from libs.storage.metric_rollup_repository import MetricRollupRepository
from libs.storage.schema import init_schema

_WINDOWS = {
    "hour": 3600,
    "today": 86400,
    "week": 604800,
    "month": 2592000,
}

_MIN_AUTHORS = {"hour": 1, "today": 5, "week": 20, "month": 50}
_INFLUENCE_CAP = 5  # max items per author per node per window


@app.task(name="rollup_accountant.compute_rollups")
def compute_rollups() -> int:
    """Compute metric rollups for all active nodes across all windows."""
    config = AgentConfig()
    conn = duckdb.connect(config.db_path)
    init_schema(conn)
    node_repo = MetricNodeRepository(conn)
    rollup_repo = MetricRollupRepository(conn)

    try:
        nodes = node_repo.get_active()
        now = int(time.time())
        count = 0

        for node in nodes:
            for window_name, window_secs in _WINDOWS.items():
                bucket_start = now - window_secs
                min_authors = _MIN_AUTHORS.get(window_name, 1)

                # Get items for this node in this window with opinion signals
                rows = conn.execute(
                    'SELECT h.id, h.author_hash, h."type", '
                    "o.valence, o.intensity, o.confidence, o.label, "
                    "e.weight "
                    "FROM item_metric_edge e "
                    "JOIN hn_item h ON e.item_id = h.id "
                    'LEFT JOIN opinion_signal o ON h.id = o.item_id '
                    'WHERE e.node_id = ? AND h."time" >= ? ',
                    [node.node_id, bucket_start],
                ).fetchall()

                if not rows:
                    continue

                # Apply per-author influence cap
                author_counts: dict[str | None, int] = {}
                capped_rows = []
                for row in rows:
                    author = row[1]
                    author_counts[author] = author_counts.get(author, 0) + 1
                    if author_counts[author] <= _INFLUENCE_CAP:
                        capped_rows.append(row)

                unique_authors = len({r[1] for r in capped_rows if r[1]})
                if unique_authors < min_authors:
                    continue

                # Compute sentiment shares (confidence-weighted)
                total_weight = 0.0
                pos_weight = 0.0
                neg_weight = 0.0
                neu_weight = 0.0
                total_valence = 0.0
                total_intensity = 0.0
                thread_ids = set()

                for row in capped_rows:
                    item_type = row[2]
                    valence = row[3] or 0.0
                    intensity = row[4] or 0.0
                    confidence = row[5] or 0.0
                    label = row[6] or "neutral"
                    edge_weight = row[7] or 0.0

                    w = confidence * edge_weight
                    total_weight += w

                    if label == "positive":
                        pos_weight += w
                    elif label == "negative":
                        neg_weight += w
                    else:
                        neu_weight += w

                    total_valence += valence * w
                    total_intensity += intensity * edge_weight

                    if item_type == "story":
                        thread_ids.add(row[0])

                if total_weight == 0:
                    continue

                pos_share = pos_weight / total_weight
                neg_share = neg_weight / total_weight
                neu_share = neu_weight / total_weight
                avg_valence = total_valence / total_weight
                presence = len(capped_rows) / max(len(rows), 1)

                split = compute_split(pos_share, neg_share)
                cons_pos, cons_neg = compute_consensus(pos_share, neg_share)
                heat = compute_heat(total_intensity, unique_authors)

                # Get baseline for momentum (previous window)
                prev_rollup = rollup_repo.get_latest(node.node_id, window_name)
                baseline = prev_rollup.presence if prev_rollup else 0.0
                momentum = compute_momentum(presence, baseline)

                rollup = MetricRollup(
                    node_id=node.node_id,
                    window=window_name,
                    bucket_start=bucket_start,
                    presence=round(presence, 4),
                    sentiment_positive=round(pos_share, 4),
                    sentiment_negative=round(neg_share, 4),
                    sentiment_neutral=round(neu_share, 4),
                    valence_score=round(avg_valence, 2),
                    split_score=split,
                    consensus_pos=cons_pos,
                    consensus_neg=cons_neg,
                    heat_score=heat,
                    momentum=momentum,
                    unique_authors=unique_authors,
                    thread_count=len(thread_ids),
                )
                rollup_repo.upsert(rollup)
                count += 1

        return count
    finally:
        conn.close()
