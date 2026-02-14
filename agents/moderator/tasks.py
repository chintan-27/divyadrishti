from __future__ import annotations

import time

from agents.celery_app import app, get_worker_conn
from libs.schemas.moderation_flag import ModerationFlag
from libs.storage.moderation_flag_repository import ModerationFlagRepository
from libs.utils.moderation import check_offensive, redact_pii


@app.task(name="moderator.moderate_items")
def moderate_items(batch_size: int = 100) -> int:
    """Scan text_clean for PII and offensive content."""
    conn = get_worker_conn()
    repo = ModerationFlagRepository(conn)

    try:
        rows = conn.execute(
            "SELECT h.id, h.text_clean FROM hn_item h "
            "LEFT JOIN moderation_flag m ON h.id = m.item_id "
            "WHERE h.text_clean IS NOT NULL AND m.item_id IS NULL "
            "LIMIT ?",
            [batch_size],
        ).fetchall()

        now = int(time.time())
        count = 0
        for item_id, text_clean in rows:
            is_offensive, reason = check_offensive(text_clean)
            if is_offensive:
                repo.upsert(ModerationFlag(
                    item_id=item_id, status="blocked",
                    reason=reason, flagged_at=now,
                ))
            else:
                redacted = redact_pii(text_clean)
                if redacted != text_clean:
                    conn.execute(
                        "UPDATE hn_item SET text_clean = ? WHERE id = ?",
                        [redacted, item_id],
                    )
                    repo.upsert(ModerationFlag(
                        item_id=item_id, status="sensitive",
                        reason="pii_redacted", flagged_at=now,
                    ))
                else:
                    repo.upsert(ModerationFlag(
                        item_id=item_id, status="clean", flagged_at=now,
                    ))
            count += 1
        return count
    finally:
        conn.close()
