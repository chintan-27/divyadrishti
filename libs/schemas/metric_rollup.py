from pydantic import BaseModel


class MetricRollup(BaseModel):
    node_id: str
    window: str  # "hour" | "today" | "week" | "month"
    bucket_start: int  # unix timestamp
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
