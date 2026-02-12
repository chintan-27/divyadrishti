from pydantic_settings import BaseSettings


class AgentConfig(BaseSettings):
    redis_url: str = "redis://localhost:6379/0"
    db_path: str = "divyadrishti.duckdb"
    author_salt: str = "default-salt"

    model_config = {"env_prefix": "DD_"}
