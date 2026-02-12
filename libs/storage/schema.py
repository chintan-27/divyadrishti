import duckdb

_HN_ITEM_DDL = """
CREATE TABLE IF NOT EXISTS hn_item (
    id INTEGER PRIMARY KEY,
    "type" VARCHAR,
    "by" VARCHAR,
    author_hash VARCHAR,
    "time" INTEGER,
    "text" VARCHAR,
    text_clean VARCHAR,
    parent INTEGER,
    kids INTEGER[],
    title VARCHAR,
    url VARCHAR,
    score INTEGER,
    descendants INTEGER,
    deleted BOOLEAN,
    dead BOOLEAN
);

CREATE INDEX IF NOT EXISTS idx_hn_item_type_time ON hn_item ("type", "time");
CREATE INDEX IF NOT EXISTS idx_hn_item_parent ON hn_item (parent);
CREATE INDEX IF NOT EXISTS idx_hn_item_time ON hn_item ("time");
"""


def init_schema(conn: duckdb.DuckDBPyConnection) -> None:
    """Create hn_item table and indexes if they don't exist."""
    conn.execute(_HN_ITEM_DDL)
