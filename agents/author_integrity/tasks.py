from __future__ import annotations

from agents.celery_app import app, get_worker_conn
from libs.schemas.author_profile import AuthorProfile
from libs.storage.author_profile_repository import AuthorProfileRepository

_BOT_COMMENT_RATE_THRESHOLD = 50  # comments per hour average


def _compute_bot_likelihood(comment_count: int, story_count: int,
                            first_seen: int, last_seen: int) -> float:
    """Heuristic bot detection based on posting rate."""
    span_hours = max((last_seen - first_seen) / 3600, 1.0)
    total = comment_count + story_count
    rate = total / span_hours
    if rate > _BOT_COMMENT_RATE_THRESHOLD:
        return min(rate / _BOT_COMMENT_RATE_THRESHOLD, 1.0)
    return 0.0


@app.task(name="author_integrity.update_author_profiles")
def update_author_profiles(batch_size: int = 200) -> int:
    """Compute author profiles from hn_item data."""
    conn = get_worker_conn()
    repo = AuthorProfileRepository(conn)

    try:
        rows = conn.execute(
            "SELECT author_hash, "
            'MIN("time") as first_seen, MAX("time") as last_seen, '
            "SUM(CASE WHEN \"type\" = 'comment' THEN 1 ELSE 0 END) as comments, "
            "SUM(CASE WHEN \"type\" = 'story' THEN 1 ELSE 0 END) as stories "
            "FROM hn_item WHERE author_hash IS NOT NULL "
            "GROUP BY author_hash LIMIT ?",
            [batch_size],
        ).fetchall()

        count = 0
        for author_hash, first_seen, last_seen, comments, stories in rows:
            bot_likelihood = _compute_bot_likelihood(
                comments, stories, first_seen or 0, last_seen or 0,
            )
            profile = AuthorProfile(
                author_hash=author_hash,
                first_seen_time=first_seen or 0,
                last_seen_time=last_seen or 0,
                comment_count=comments,
                story_count=stories,
                bot_likelihood=bot_likelihood,
            )
            repo.upsert(profile)
            count += 1
        return count
    finally:
        conn.close()
