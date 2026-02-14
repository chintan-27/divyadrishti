from __future__ import annotations

from agents.celery_app import app, get_worker_conn
from libs.utils.text_clean import clean_hn_html, content_hash


@app.task(name="normalizer.normalize_items")
def normalize_items(batch_size: int = 100) -> int:
    """Clean text for items that have raw text but no text_clean."""
    conn = get_worker_conn()

    try:
        rows = conn.execute(
            'SELECT id, "text" FROM hn_item '
            'WHERE "text" IS NOT NULL AND text_clean IS NULL '
            "LIMIT ?",
            [batch_size],
        ).fetchall()

        seen_hashes: set[str] = set()
        count = 0
        for item_id, text in rows:
            cleaned = clean_hn_html(text)
            if not cleaned:
                continue
            h = content_hash(cleaned)
            if h in seen_hashes:
                continue
            seen_hashes.add(h)
            conn.execute(
                "UPDATE hn_item SET text_clean = ? WHERE id = ?",
                [cleaned, item_id],
            )
            count += 1
        return count
    finally:
        conn.close()
