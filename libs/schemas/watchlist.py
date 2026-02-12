from pydantic import BaseModel


class WatchlistEntry(BaseModel):
    story_id: int
    priority_score: float = 0.0
    ttl_expires: int = 0
    last_fetched: int | None = None
