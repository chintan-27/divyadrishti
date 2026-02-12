import duckdb

from libs.schemas.author_profile import AuthorProfile
from libs.storage.author_profile_repository import AuthorProfileRepository
from libs.storage.schema import init_schema


def _setup() -> tuple[duckdb.DuckDBPyConnection, AuthorProfileRepository]:
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    return conn, AuthorProfileRepository(conn)


def test_upsert_and_get():
    conn, repo = _setup()
    profile = AuthorProfile(author_hash="abc123", first_seen_time=1000, last_seen_time=2000,
                            comment_count=5, story_count=2)
    repo.upsert(profile)
    result = repo.get_by_hash("abc123")
    assert result is not None
    assert result.comment_count == 5
    assert result.story_count == 2
    conn.close()


def test_upsert_keeps_earliest_first_seen():
    conn, repo = _setup()
    repo.upsert(AuthorProfile(author_hash="a", first_seen_time=1000, last_seen_time=1000))
    repo.upsert(AuthorProfile(author_hash="a", first_seen_time=500, last_seen_time=2000))
    result = repo.get_by_hash("a")
    assert result is not None
    assert result.first_seen_time == 500
    assert result.last_seen_time == 2000
    conn.close()


def test_get_not_found():
    conn, repo = _setup()
    assert repo.get_by_hash("nonexistent") is None
    conn.close()


def test_get_all():
    conn, repo = _setup()
    repo.upsert(AuthorProfile(author_hash="a", comment_count=1))
    repo.upsert(AuthorProfile(author_hash="b", comment_count=2))
    all_profiles = repo.get_all()
    assert len(all_profiles) == 2
    conn.close()
