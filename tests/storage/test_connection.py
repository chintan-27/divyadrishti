import tempfile
from pathlib import Path

from libs.storage.connection import DuckDBConnection


def test_in_memory_connection():
    db = DuckDBConnection()
    conn = db.connect()
    result = conn.execute("SELECT 1 AS n").fetchone()
    assert result == (1,)
    db.close()


def test_file_based_connection():
    with tempfile.TemporaryDirectory() as tmpdir:
        path = str(Path(tmpdir) / "test.duckdb")
        db = DuckDBConnection(path)
        db.connect().execute("CREATE TABLE t (x INTEGER)")
        db.close()

        db2 = DuckDBConnection(path)
        rows = db2.connect().execute("SELECT * FROM t").fetchall()
        assert rows == []
        db2.close()


def test_connect_reuses_connection():
    db = DuckDBConnection()
    c1 = db.connect()
    c2 = db.connect()
    assert c1 is c2
    db.close()


def test_close_allows_reconnect():
    db = DuckDBConnection()
    db.connect().execute("SELECT 1")
    db.close()
    result = db.connect().execute("SELECT 2 AS n").fetchone()
    assert result == (2,)
    db.close()


def test_cursor_context_manager():
    db = DuckDBConnection()
    db.connect().execute("CREATE TABLE t (x INTEGER)")
    db.connect().execute("INSERT INTO t VALUES (42)")
    with db.cursor() as cur:
        row = cur.execute("SELECT x FROM t").fetchone()
        assert row == (42,)
    db.close()
