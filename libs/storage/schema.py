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


_AUTHOR_PROFILE_DDL = """
CREATE TABLE IF NOT EXISTS author_profile (
    author_hash VARCHAR PRIMARY KEY,
    first_seen_time BIGINT DEFAULT 0,
    last_seen_time BIGINT DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    story_count INTEGER DEFAULT 0,
    spam_score DOUBLE DEFAULT 0.0,
    bot_likelihood DOUBLE DEFAULT 0.0,
    influence_cap_state VARCHAR DEFAULT 'normal'
);
"""

_MODERATION_FLAG_DDL = """
CREATE TABLE IF NOT EXISTS moderation_flag (
    item_id INTEGER PRIMARY KEY,
    status VARCHAR DEFAULT 'clean',
    reason VARCHAR,
    flagged_at BIGINT DEFAULT 0
);
"""


_OPINION_SIGNAL_DDL = """
CREATE TABLE IF NOT EXISTS opinion_signal (
    item_id INTEGER PRIMARY KEY,
    valence DOUBLE DEFAULT 0.0,
    intensity DOUBLE DEFAULT 0.0,
    confidence DOUBLE DEFAULT 0.0,
    label VARCHAR DEFAULT 'neutral',
    model_version VARCHAR DEFAULT ''
);
"""


_EMBEDDING_DDL = """
CREATE TABLE IF NOT EXISTS embedding (
    item_id INTEGER PRIMARY KEY,
    embedding FLOAT[384],
    model_version VARCHAR DEFAULT ''
);
"""

_METRIC_NODE_DDL = """
CREATE TABLE IF NOT EXISTS metric_node (
    node_id VARCHAR PRIMARY KEY,
    label VARCHAR DEFAULT '',
    definition VARCHAR DEFAULT '',
    centroid FLOAT[384],
    parent_id VARCHAR,
    status VARCHAR DEFAULT 'active',
    version INTEGER DEFAULT 1,
    health_stats VARCHAR DEFAULT '{}'
);

CREATE INDEX IF NOT EXISTS idx_metric_node_status ON metric_node (status);
"""

_ITEM_METRIC_EDGE_DDL = """
CREATE TABLE IF NOT EXISTS item_metric_edge (
    item_id INTEGER,
    node_id VARCHAR,
    weight DOUBLE DEFAULT 0.0,
    created_at BIGINT DEFAULT 0,
    PRIMARY KEY (item_id, node_id)
);

CREATE INDEX IF NOT EXISTS idx_item_metric_edge_node ON item_metric_edge (node_id);
"""


def init_schema(conn: duckdb.DuckDBPyConnection) -> None:
    """Create all tables and indexes if they don't exist."""
    conn.execute(_HN_ITEM_DDL)
    conn.execute(_WATCHLIST_DDL)
    conn.execute(_AUTHOR_PROFILE_DDL)
    conn.execute(_MODERATION_FLAG_DDL)
    conn.execute(_OPINION_SIGNAL_DDL)
    conn.execute(_EMBEDDING_DDL)
    conn.execute(_METRIC_NODE_DDL)
    conn.execute(_ITEM_METRIC_EDGE_DDL)
