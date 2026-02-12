import duckdb

from libs.storage.schema import init_schema


def _connect() -> duckdb.DuckDBPyConnection:
    return duckdb.connect(":memory:")


def test_creates_hn_item_table():
    conn = _connect()
    init_schema(conn)
    tables = conn.execute("SHOW TABLES").fetchall()
    assert ("hn_item",) in tables
    conn.close()


def test_idempotent():
    conn = _connect()
    init_schema(conn)
    init_schema(conn)
    tables = conn.execute("SHOW TABLES").fetchall()
    assert ("hn_item",) in tables
    conn.close()


def test_column_types():
    conn = _connect()
    init_schema(conn)
    cols = conn.execute(
        "SELECT column_name, data_type FROM information_schema.columns "
        "WHERE table_name = 'hn_item' ORDER BY ordinal_position"
    ).fetchall()
    col_map = dict(cols)
    assert col_map["id"] == "INTEGER"
    assert col_map["type"] == "VARCHAR"
    assert col_map["kids"] == "INTEGER[]"
    assert col_map["deleted"] == "BOOLEAN"
    assert col_map["time"] == "INTEGER"
    conn.close()
