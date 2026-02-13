from unittest.mock import MagicMock, patch

import duckdb

from agents.opinion_analyst.tasks import analyze_opinions
from libs.schemas.hn_item import HNItem
from libs.schemas.opinion_signal import OpinionSignal
from libs.storage.hn_item_repository import HNItemRepository
from libs.storage.opinion_signal_repository import OpinionSignalRepository
from libs.storage.schema import init_schema
from tests.agents.test_normalizer import _ConnWrapper


def test_analyze_opinions():
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    repo = HNItemRepository(conn)
    repo.upsert(HNItem(id=1, type="comment", text_clean="This is great"))
    repo.upsert(HNItem(id=2, type="comment", text_clean="This is terrible"))
    repo.upsert(HNItem(id=3, type="comment"))  # no text_clean

    mock_model = MagicMock()
    mock_model.predict_batch.return_value = [
        OpinionSignal(item_id=0, valence=80.0, intensity=0.9,
                      confidence=0.95, label="positive", model_version="test"),
        OpinionSignal(item_id=0, valence=-70.0, intensity=0.8,
                      confidence=0.9, label="negative", model_version="test"),
    ]

    wrapper = _ConnWrapper(conn)
    with (
        patch("agents.opinion_analyst.tasks.duckdb") as mock_duckdb,
        patch("agents.opinion_analyst.tasks.get_model", return_value=mock_model),
    ):
        mock_duckdb.connect.return_value = wrapper
        count = analyze_opinions()

    assert count == 2
    signal_repo = OpinionSignalRepository(conn)
    s1 = signal_repo.get_by_item_id(1)
    assert s1 is not None
    assert s1.label == "positive"

    s2 = signal_repo.get_by_item_id(2)
    assert s2 is not None
    assert s2.label == "negative"

    assert signal_repo.get_by_item_id(3) is None
    conn.close()


def test_analyze_opinions_skips_already_analyzed():
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    repo = HNItemRepository(conn)
    repo.upsert(HNItem(id=1, type="comment", text_clean="Already done"))
    sig_repo = OpinionSignalRepository(conn)
    sig_repo.upsert(OpinionSignal(item_id=1, valence=50.0, label="positive"))

    wrapper = _ConnWrapper(conn)
    with patch("agents.opinion_analyst.tasks.duckdb") as mock_duckdb:
        mock_duckdb.connect.return_value = wrapper
        count = analyze_opinions()

    assert count == 0
    conn.close()
