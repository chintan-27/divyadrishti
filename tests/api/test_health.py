import duckdb
from fastapi.testclient import TestClient

from apps.api.main import app
from apps.api.routes import stories, stream
from libs.storage.schema import init_schema


def _setup() -> tuple[duckdb.DuckDBPyConnection, TestClient]:
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    stories.set_db(conn)
    stream.set_db(conn)
    return conn, TestClient(app)


def test_health():
    conn, client = _setup()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
    conn.close()
