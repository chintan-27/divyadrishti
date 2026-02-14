import duckdb
from fastapi.testclient import TestClient

from apps.api.db import set_db
from apps.api.main import app
from libs.storage.schema import init_schema


def _setup() -> tuple[duckdb.DuckDBPyConnection, TestClient]:
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    set_db(conn)
    return conn, TestClient(app)


def test_health():
    conn, client = _setup()
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}
    conn.close()
