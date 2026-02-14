from unittest.mock import patch

import duckdb

from agents.moderator.tasks import moderate_items
from libs.schemas.hn_item import HNItem
from libs.storage.hn_item_repository import HNItemRepository
from libs.storage.moderation_flag_repository import ModerationFlagRepository
from libs.storage.schema import init_schema
from tests.agents.test_normalizer import _ConnWrapper


def test_moderate_items():
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    repo = HNItemRepository(conn)
    repo.upsert(HNItem(id=1, type="comment", text_clean="nice comment"))
    repo.upsert(HNItem(id=2, type="comment", text_clean="email me at foo@bar.com"))
    repo.upsert(HNItem(id=3, type="comment", text_clean="kys lol"))

    wrapper = _ConnWrapper(conn)
    with patch("agents.moderator.tasks.get_worker_conn", return_value=wrapper):
        count = moderate_items()

    assert count == 3
    flag_repo = ModerationFlagRepository(conn)

    f1 = flag_repo.get_by_item_id(1)
    assert f1 is not None
    assert f1.status == "clean"

    f2 = flag_repo.get_by_item_id(2)
    assert f2 is not None
    assert f2.status == "sensitive"

    # verify PII was redacted in hn_item
    item2 = repo.get_by_id(2)
    assert item2 is not None
    assert "[EMAIL]" in (item2.text_clean or "")

    f3 = flag_repo.get_by_item_id(3)
    assert f3 is not None
    assert f3.status == "blocked"
    conn.close()
