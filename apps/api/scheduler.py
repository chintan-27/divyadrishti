"""In-process background scheduler for agent tasks.

DuckDB only supports single-process access, so we run periodic tasks in the
same process as the API server using background threads.
"""
from __future__ import annotations

import logging
import threading
import time

logger = logging.getLogger(__name__)

# Schedule: (task_name, callable, interval_seconds)
_SCHEDULE: list[tuple[str, callable, float]] = []
_stop_event = threading.Event()


def _build_schedule() -> list[tuple[str, callable, float]]:
    """Import and register all agent tasks with their intervals."""
    tasks: list[tuple[str, callable, float]] = []

    from agents.trend_scout.tasks import discover_trending
    tasks.append(("discover_trending", discover_trending, 90))

    from agents.trend_scout.backfill import backfill_stories
    tasks.append(("backfill_stories", backfill_stories, 300))

    from agents.thread_harvester.tasks import harvest_threads
    tasks.append(("harvest_threads", harvest_threads, 20))

    from agents.normalizer.tasks import normalize_items
    tasks.append(("normalize_items", normalize_items, 15))

    from agents.author_integrity.tasks import update_author_profiles
    tasks.append(("update_author_profiles", update_author_profiles, 60))

    from agents.opinion_analyst.tasks import analyze_opinions
    tasks.append(("analyze_opinions", analyze_opinions, 20))

    from agents.moderator.tasks import moderate_items
    tasks.append(("moderate_items", moderate_items, 30))

    from agents.metric_mapper.tasks import map_items_to_metrics
    tasks.append(("map_items_to_metrics", map_items_to_metrics, 20))

    from agents.metric_gardener.tasks import garden_metrics
    tasks.append(("garden_metrics", garden_metrics, 3600))

    from agents.rollup_accountant.tasks import compute_rollups
    tasks.append(("compute_rollups", compute_rollups, 45))

    from agents.supervisor.tasks import cleanup_watchlist
    tasks.append(("cleanup_watchlist", cleanup_watchlist, 300))

    return tasks


def _run_task_loop(name: str, fn: callable, interval: float) -> None:
    """Run a single task in a loop with the given interval."""
    while not _stop_event.is_set():
        try:
            result = fn()
            logger.info("Task %s completed: %s", name, result)
        except Exception:
            logger.exception("Task %s failed", name)
        _stop_event.wait(interval)


def start() -> None:
    """Start all background task threads."""
    schedule = _build_schedule()
    for name, fn, interval in schedule:
        t = threading.Thread(target=_run_task_loop, args=(name, fn, interval), daemon=True)
        t.start()
        logger.info("Started background task: %s (every %ds)", name, interval)


def stop() -> None:
    """Signal all task threads to stop."""
    _stop_event.set()
