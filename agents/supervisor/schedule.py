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
    "normalize-items": {
        "task": "normalizer.normalize_items",
        "schedule": schedule(run_every=15),
    },
    "update-author-profiles": {
        "task": "author_integrity.update_author_profiles",
        "schedule": schedule(run_every=60),
    },
    "analyze-opinions": {
        "task": "opinion_analyst.analyze_opinions",
        "schedule": schedule(run_every=20),
    },
    "moderate-items": {
        "task": "moderator.moderate_items",
        "schedule": schedule(run_every=30),
    },
    "map-items-to-metrics": {
        "task": "metric_mapper.map_items_to_metrics",
        "schedule": schedule(run_every=20),
    },
    "garden-metrics": {
        "task": "metric_gardener.garden_metrics",
        "schedule": schedule(run_every=3600),
    },
    "compute-rollups": {
        "task": "rollup_accountant.compute_rollups",
        "schedule": schedule(run_every=45),
    },
    "backfill-stories": {
        "task": "trend_scout.backfill_stories",
        "schedule": schedule(run_every=300),
    },
}
