from pydantic import BaseModel


class ItemMetricEdge(BaseModel):
    item_id: int
    node_id: str
    weight: float = 0.0
    created_at: int = 0
