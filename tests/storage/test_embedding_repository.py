import duckdb

from libs.schemas.embedding import Embedding
from libs.storage.embedding_repository import EmbeddingRepository
from libs.storage.schema import init_schema


def _setup() -> tuple[duckdb.DuckDBPyConnection, EmbeddingRepository]:
    conn = duckdb.connect(":memory:")
    init_schema(conn)
    return conn, EmbeddingRepository(conn)


def test_upsert_and_get():
    conn, repo = _setup()
    vec = [0.1] * 384
    emb = Embedding(item_id=1, embedding=vec, model_version="v1")
    repo.upsert(emb)
    result = repo.get_by_item_id(1)
    assert result is not None
    assert len(result.embedding) == 384
    assert abs(result.embedding[0] - 0.1) < 1e-5
    conn.close()


def test_get_not_found():
    conn, repo = _setup()
    assert repo.get_by_item_id(999) is None
    conn.close()


def test_get_by_item_ids():
    conn, repo = _setup()
    for i in range(1, 4):
        repo.upsert(Embedding(item_id=i, embedding=[float(i)] * 384))
    results = repo.get_by_item_ids([1, 3])
    assert len(results) == 2
    conn.close()


def test_get_by_item_ids_empty():
    _, repo = _setup()
    assert repo.get_by_item_ids([]) == []
