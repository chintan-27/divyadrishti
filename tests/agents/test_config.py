from agents.config import AgentConfig


def test_defaults():
    cfg = AgentConfig()
    assert cfg.redis_url == "redis://localhost:6379/0"
    assert cfg.db_path == "divyadrishti.duckdb"
    assert cfg.author_salt == "default-salt"


def test_env_override(monkeypatch):
    monkeypatch.setenv("DD_REDIS_URL", "redis://custom:1234/1")
    monkeypatch.setenv("DD_DB_PATH", "/tmp/test.duckdb")
    monkeypatch.setenv("DD_AUTHOR_SALT", "secret")
    cfg = AgentConfig()
    assert cfg.redis_url == "redis://custom:1234/1"
    assert cfg.db_path == "/tmp/test.duckdb"
    assert cfg.author_salt == "secret"
