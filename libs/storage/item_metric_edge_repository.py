from __future__ import annotations

from typing import TYPE_CHECKING

from libs.schemas.item_metric_edge import ItemMetricEdge

if TYPE_CHECKING:
    import duckdb

_UPSERT_SQL = """
INSERT INTO item_metric_edge (item_id, node_id, weight, created_at)
VALUES (?, ?, ?, ?)
ON CONFLICT (item_id, node_id) DO UPDATE SET
    weight = excluded.weight,
    created_at = excluded.created_at
"""

_COLUMNS = "item_id, node_id, weight, created_at"


def _row_to_edge(row: tuple[object, ...]) -> ItemMetricEdge:
    return ItemMetricEdge(
        item_id=row[0],  # type: ignore[arg-type]
        node_id=row[1],  # type: ignore[arg-type]
        weight=row[2],  # type: ignore[arg-type]
        created_at=row[3],  # type: ignore[arg-type]
    )


class ItemMetricEdgeRepository:
    def __init__(self, conn: duckdb.DuckDBPyConnection) -> None:
        self._conn = conn

    def upsert(self, edge: ItemMetricEdge) -> None:
        self._conn.execute(
            _UPSERT_SQL,
            [edge.item_id, edge.node_id, edge.weight, edge.created_at],
        )

    def get_edges_for_item(self, item_id: int) -> list[ItemMetricEdge]:
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM item_metric_edge WHERE item_id = ?",
            [item_id],
        ).fetchall()
        return [_row_to_edge(r) for r in rows]

    def get_edges_for_node(self, node_id: str, limit: int = 50) -> list[ItemMetricEdge]:
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM item_metric_edge "
            "WHERE node_id = ? ORDER BY weight DESC LIMIT ?",
            [node_id, limit],
        ).fetchall()
        return [_row_to_edge(r) for r in rows]
