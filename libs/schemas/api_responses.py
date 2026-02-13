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


class RollupResponse(BaseModel):
    node_id: str
    window: str
    bucket_start: int
    presence: float = 0.0
    sentiment_positive: float = 0.0
    sentiment_negative: float = 0.0
    sentiment_neutral: float = 0.0
    valence_score: float = 0.0
    split_score: float = 0.0
    consensus_pos: float = 0.0
    consensus_neg: float = 0.0
    heat_score: float = 0.0
    momentum: float = 0.0
    unique_authors: int = 0
    thread_count: int = 0


class MetricDetailResponse(BaseModel):
    node_id: str
    label: str = ""
    definition: str = ""
    status: str = "active"
    item_count: int = 0
    latest_rollup: RollupResponse | None = None
