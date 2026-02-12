import duckdb

from libs.schemas.opinion_signal import OpinionSignal
from libs.storage.opinion_signal_repository import OpinionSignalRepository
from libs.storage.schema import init_schema


def _setup() -> tuple[duckdb.DuckDBPyConnection, OpinionSignalRepository]:
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    return conn, OpinionSignalRepository(conn)


def test_upsert_and_get():
    conn, repo = _setup()
    signal = OpinionSignal(item_id=1, valence=50.0, intensity=0.8,
                           confidence=0.9, label="positive", model_version="v1")
    repo.upsert(signal)
    result = repo.get_by_item_id(1)
    assert result is not None
    assert result.valence == 50.0
    assert result.label == "positive"
    conn.close()


def test_upsert_updates():
    conn, repo = _setup()
    repo.upsert(OpinionSignal(item_id=1, valence=50.0, label="positive"))
    repo.upsert(OpinionSignal(item_id=1, valence=-30.0, label="negative"))
    result = repo.get_by_item_id(1)
    assert result is not None
    assert result.valence == -30.0
    assert result.label == "negative"
    conn.close()


def test_get_not_found():
    conn, repo = _setup()
    assert repo.get_by_item_id(999) is None
    conn.close()


def test_get_by_item_ids():
    conn, repo = _setup()
    for i in range(1, 4):
        repo.upsert(OpinionSignal(item_id=i, valence=float(i * 10)))
    results = repo.get_by_item_ids([1, 3])
    assert len(results) == 2
    conn.close()


def test_get_by_item_ids_empty():
    _, repo = _setup()
    assert repo.get_by_item_ids([]) == []


def test_get_recent():
    conn, repo = _setup()
    for i in range(1, 6):
        repo.upsert(OpinionSignal(item_id=i, valence=float(i)))
    results = repo.get_recent(limit=3)
    assert len(results) == 3
    assert results[0].item_id == 5  # desc order
    conn.close()
