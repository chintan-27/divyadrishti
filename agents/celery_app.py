from celery import Celery

from agents.config import AgentConfig
from agents.supervisor.schedule import BEAT_SCHEDULE

config = AgentConfig()

app = Celery("divyadrishti")
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
