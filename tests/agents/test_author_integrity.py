from unittest.mock import patch

import duckdb

from agents.author_integrity.tasks import _compute_bot_likelihood, update_author_profiles
from libs.schemas.hn_item import HNItem
from libs.storage.author_profile_repository import AuthorProfileRepository
from libs.storage.hn_item_repository import HNItemRepository
from libs.storage.schema import init_schema
from tests.agents.test_normalizer import _ConnWrapper


def test_compute_bot_likelihood_normal():
    assert _compute_bot_likelihood(10, 2, 0, 36000) == 0.0


def test_compute_bot_likelihood_high_rate():
    # 100 comments in 1 hour => rate=100, threshold=50 => 2.0 capped to 1.0
    result = _compute_bot_likelihood(100, 0, 0, 3600)
    assert result == 1.0


def test_update_author_profiles():
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    repo = HNItemRepository(conn)
    repo.upsert(HNItem(id=1, type="story", by="pg", author_hash="h1", time=1000))
    repo.upsert(HNItem(id=2, type="comment", by="pg", author_hash="h1", time=2000))
    repo.upsert(HNItem(id=3, type="comment", by="alice", author_hash="h2", time=1500))

    wrapper = _ConnWrapper(conn)
    with patch("agents.author_integrity.tasks.duckdb") as mock_duckdb:
        mock_duckdb.connect.return_value = wrapper
        count = update_author_profiles()

    assert count == 2

    profile_repo = AuthorProfileRepository(conn)
    p1 = profile_repo.get_by_hash("h1")
    assert p1 is not None
    assert p1.story_count == 1
    assert p1.comment_count == 1
    assert p1.first_seen_time == 1000
    assert p1.last_seen_time == 2000

    p2 = profile_repo.get_by_hash("h2")
    assert p2 is not None
    assert p2.comment_count == 1
    conn.close()
