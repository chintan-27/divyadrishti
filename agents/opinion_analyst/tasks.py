from __future__ import annotations

from agents.celery_app import app, get_worker_conn
from libs.nlp.sentiment import get_model
from libs.schemas.opinion_signal import OpinionSignal
from libs.storage.opinion_signal_repository import OpinionSignalRepository


@app.task(name="opinion_analyst.analyze_opinions")
def analyze_opinions(batch_size: int = 50) -> int:
    """Run sentiment analysis on items with text_clean but no opinion_signal."""
    conn = get_worker_conn()
    repo = OpinionSignalRepository(conn)

    try:
        rows = conn.execute(
            "SELECT h.id, h.text_clean FROM hn_item h "
            "LEFT JOIN opinion_signal o ON h.id = o.item_id "
            "WHERE h.text_clean IS NOT NULL AND o.item_id IS NULL "
            "LIMIT ?",
            [batch_size],
        ).fetchall()

        if not rows:
            return 0

        item_ids = [r[0] for r in rows]
        texts = [r[1] for r in rows]

        model = get_model()
        signals = model.predict_batch(texts)

        count = 0
        for item_id, signal in zip(item_ids, signals):
            repo.upsert(OpinionSignal(
                item_id=item_id,
                valence=signal.valence,
                intensity=signal.intensity,
                confidence=signal.confidence,
                label=signal.label,
                model_version=signal.model_version,
            ))
            count += 1
        return count
    finally:
        conn.close()
