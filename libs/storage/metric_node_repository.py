from __future__ import annotations

from typing import TYPE_CHECKING

from libs.schemas.metric_node import MetricNode

if TYPE_CHECKING:
    import duckdb

_UPSERT_SQL = """
INSERT INTO metric_node (
    node_id, label, definition, centroid, parent_id, status, version, health_stats
) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
ON CONFLICT (node_id) DO UPDATE SET
    label = excluded.label,
    definition = excluded.definition,
    centroid = excluded.centroid,
    parent_id = COALESCE(excluded.parent_id, metric_node.parent_id),
    status = excluded.status,
    version = excluded.version,
    health_stats = excluded.health_stats
"""

_COLUMNS = "node_id, label, definition, centroid, parent_id, status, version, health_stats"


def _row_to_node(row: tuple[object, ...]) -> MetricNode:
    return MetricNode(
        node_id=row[0],  # type: ignore[arg-type]
        label=row[1],  # type: ignore[arg-type]
        definition=row[2],  # type: ignore[arg-type]
        centroid=list(row[3]) if row[3] else [],  # type: ignore[arg-type]
        parent_id=row[4],  # type: ignore[arg-type]
        status=row[5],  # type: ignore[arg-type]
        version=row[6],  # type: ignore[arg-type]
        health_stats=row[7],  # type: ignore[arg-type]
    )


class MetricNodeRepository:
    def __init__(self, conn: duckdb.DuckDBPyConnection) -> None:
        self._conn = conn

    def upsert(self, node: MetricNode) -> None:
        centroid = node.centroid if node.centroid else None
        self._conn.execute(
            _UPSERT_SQL,
            [node.node_id, node.label, node.definition, centroid,
             node.parent_id, node.status, node.version, node.health_stats],
        )

    def get_by_id(self, node_id: str) -> MetricNode | None:
        row = self._conn.execute(
            f"SELECT {_COLUMNS} FROM metric_node WHERE node_id = ?",
            [node_id],
        ).fetchone()
        return _row_to_node(row) if row else None

    def get_active(self) -> list[MetricNode]:
        rows = self._conn.execute(
            f"SELECT {_COLUMNS} FROM metric_node WHERE status = 'active'"
        ).fetchall()
        return [_row_to_node(r) for r in rows]

    def get_all_centroids(self) -> list[tuple[str, list[float]]]:
        """Return (node_id, centroid) for all active nodes."""
        rows = self._conn.execute(
            "SELECT node_id, centroid FROM metric_node WHERE status = 'active'"
        ).fetchall()
        return [(r[0], list(r[1]) if r[1] else []) for r in rows]
