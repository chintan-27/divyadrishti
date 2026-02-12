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

_WATCHLIST_DDL = """
CREATE TABLE IF NOT EXISTS watchlist (
    story_id INTEGER PRIMARY KEY,
    priority_score DOUBLE DEFAULT 0.0,
    ttl_expires BIGINT DEFAULT 0,
    last_fetched BIGINT
);

CREATE INDEX IF NOT EXISTS idx_watchlist_ttl_priority
    ON watchlist (ttl_expires, priority_score DESC);
"""


def init_schema(conn: duckdb.DuckDBPyConnection) -> None:
    """Create all tables and indexes if they don't exist."""
    conn.execute(_HN_ITEM_DDL)
    conn.execute(_WATCHLIST_DDL)
