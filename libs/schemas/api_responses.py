from pydantic import BaseModel, Field


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


# --- Metric responses (aligned with frontend types) ---

class SentimentResponse(BaseModel):
    positive: float = 0.0
    negative: float = 0.0
    neutral: float = 0.0


class MetricNodeResponse(BaseModel):
    """Matches frontend MetricNode interface."""
    id: str
    label: str = ""
    definition: str = ""
    presence_pct: float = 0.0
    valence: float = 0.0
    heat: float = 0.0
    momentum: float = 0.0
    sentiment: SentimentResponse = Field(default_factory=SentimentResponse)
    item_count: int = 0


class RollupDataResponse(BaseModel):
    """Matches frontend RollupData interface."""
    window: str = "today"
    presence_pct: float = 0.0
    valence: float = 0.0
    heat: float = 0.0
    momentum: float = 0.0
    split: float = 0.0
    consensus: float = 0.0
    unique_authors: int = 0
    sentiment: SentimentResponse = Field(default_factory=SentimentResponse)


class MetricDetailResponse(BaseModel):
    """Matches frontend MetricDetail interface."""
    id: str
    label: str = ""
    definition: str = ""
    rollup: RollupDataResponse = Field(default_factory=RollupDataResponse)
    example_items: list[StoryResponse] = Field(default_factory=list)


class MetricExampleResponse(BaseModel):
    item_id: int
    title: str | None = None
    text: str | None = None
    weight: float = 0.0


class RankingEntryResponse(BaseModel):
    """Matches frontend RankingEntry interface."""
    rank: int
    metric: MetricNodeResponse


# Keep internal rollup response for /series endpoint
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


class SeriesPointResponse(BaseModel):
    """Matches frontend SeriesPoint interface."""
    ts: str
    presence_pct: float = 0.0
    valence: float = 0.0
    heat: float = 0.0
    momentum: float = 0.0
