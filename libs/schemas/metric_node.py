from pydantic import BaseModel


class MetricNode(BaseModel):
    node_id: str
    label: str = ""
    definition: str = ""
    centroid: list[float] = []
    parent_id: str | None = None
    status: str = "active"
    version: int = 1
    health_stats: str = "{}"
