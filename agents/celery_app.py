from celery import Celery

from agents.config import AgentConfig

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
)
