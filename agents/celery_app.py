from __future__ import annotations

import duckdb
from celery import Celery

from agents.config import AgentConfig
from agents.supervisor.schedule import BEAT_SCHEDULE
from libs.storage.schema import init_schema

config = AgentConfig()

_schema_initialized = False


def get_worker_conn() -> duckdb.DuckDBPyConnection:
    """Open a fresh DuckDB write connection for a task.

    Caller must close the connection when done.
    """
    global _schema_initialized  # noqa: PLW0603
    conn = duckdb.connect(config.db_path)
    if not _schema_initialized:
        init_schema(conn)
        _schema_initialized = True
    return conn


app = Celery("divyadrishti")
app.autodiscover_tasks([
    "agents.trend_scout",
    "agents.thread_harvester",
    "agents.supervisor",
    "agents.normalizer",
    "agents.author_integrity",
    "agents.opinion_analyst",
    "agents.moderator",
    "agents.metric_mapper",
    "agents.metric_gardener",
    "agents.rollup_accountant",
], related_name="tasks")
app.autodiscover_tasks(["agents.trend_scout"], related_name="backfill")
app.conf.update(
    broker_url=config.redis_url,
    result_backend=config.redis_url,
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule=BEAT_SCHEDULE,
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    task_default_retry_delay=10,
    task_annotations={
        "*": {"max_retries": 3, "retry_backoff": True, "retry_backoff_max": 120},
    },
    worker_concurrency=1,
)
