from __future__ import annotations

from typing import TYPE_CHECKING

from libs.schemas.embedding import Embedding

if TYPE_CHECKING:
    import duckdb

_UPSERT_SQL = """
INSERT INTO embedding (item_id, embedding, model_version)
VALUES (?, ?, ?)
ON CONFLICT (item_id) DO UPDATE SET
    embedding = excluded.embedding,
    model_version = excluded.model_version
"""

_COLUMNS = "item_id, embedding, model_version"


def _row_to_embedding(row: tuple[object, ...]) -> Embedding:
    return Embedding(
        item_id=row[0],  # type: ignore[arg-type]
        embedding=list(row[1]) if row[1] else [],  # type: ignore[arg-type]
        model_version=row[2],  # type: ignore[arg-type]
    )


class EmbeddingRepository:
    def __init__(self, conn: duckdb.DuckDBPyConnection) -> None:
        self._conn = conn

    def upsert(self, emb: Embedding) -> None:
        embedding = emb.embedding if emb.embedding else None
        self._conn.execute(_UPSERT_SQL, [emb.item_id, embedding, emb.model_version])

    def get_by_item_id(self, item_id: int) -> Embedding | None:
        row = self._conn.execute(
            f"SELECT {_COLUMNS} FROM embedding WHERE item_id = ?",
            [item_id],
        ).fetchone()
        return _row_to_embedding(row) if row else None

    def get_by_item_ids(self, item_ids: list[int]) -> list[Embedding]:
        if not item_ids:
            return []
        placeholders = ", ".join("?" for _ in item_ids)
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM embedding WHERE item_id IN ({placeholders})",
            item_ids,
        ).fetchall()
        return [_row_to_embedding(r) for r in rows]
