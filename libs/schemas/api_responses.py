from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str = "ok"


class StoryResponse(BaseModel):
    id: int
    title: str | None = None
    url: str | None = None
    score: int | None = None
    by: str | None = None
    time: int | None = None
    descendants: int | None = None
    type: str | None = None


class CommentResponse(BaseModel):
    id: int
    by: str | None = None
    text: str | None = None
    time: int | None = None
    parent: int | None = None


class MetricNodeResponse(BaseModel):
    node_id: str
    label: str = ""
    definition: str = ""
    status: str = "active"
    item_count: int = 0


class MetricExampleResponse(BaseModel):
    item_id: int
    title: str | None = None
    text: str | None = None
    weight: float = 0.0
