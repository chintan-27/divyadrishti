"""Celery Beat schedule for agent tasks."""

from celery.schedules import schedule

BEAT_SCHEDULE: dict[str, dict[str, object]] = {
    "discover-trending": {
        "task": "trend_scout.discover_trending",
        "schedule": schedule(run_every=90),
    },
    "harvest-threads": {
        "task": "thread_harvester.harvest_threads",
        "schedule": schedule(run_every=20),
    },
    "cleanup-watchlist": {
        "task": "supervisor.cleanup_watchlist",
        "schedule": schedule(run_every=300),
    },
}
