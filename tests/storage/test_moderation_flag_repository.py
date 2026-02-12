import duckdb

from libs.schemas.moderation_flag import ModerationFlag
from libs.storage.moderation_flag_repository import ModerationFlagRepository
from libs.storage.schema import init_schema


def _setup() -> tuple[duckdb.DuckDBPyConnection, ModerationFlagRepository]:
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    return conn, ModerationFlagRepository(conn)


def test_upsert_and_get():
    conn, repo = _setup()
    flag = ModerationFlag(item_id=1, status="clean", flagged_at=1000)
    repo.upsert(flag)
    result = repo.get_by_item_id(1)
    assert result is not None
    assert result.status == "clean"
    conn.close()


def test_upsert_updates():
    conn, repo = _setup()
    repo.upsert(ModerationFlag(item_id=1, status="clean"))
    repo.upsert(ModerationFlag(item_id=1, status="blocked", reason="offensive"))
    result = repo.get_by_item_id(1)
    assert result is not None
    assert result.status == "blocked"
    assert result.reason == "offensive"
    conn.close()


def test_get_not_found():
    conn, repo = _setup()
    assert repo.get_by_item_id(999) is None
    conn.close()


def test_get_by_status():
    conn, repo = _setup()
    repo.upsert(ModerationFlag(item_id=1, status="clean"))
    repo.upsert(ModerationFlag(item_id=2, status="blocked"))
    repo.upsert(ModerationFlag(item_id=3, status="blocked"))
    blocked = repo.get_by_status("blocked")
    assert len(blocked) == 2
    conn.close()
