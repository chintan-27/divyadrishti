from pydantic import BaseModel


class ModerationFlag(BaseModel):
    item_id: int
    status: str = "clean"  # clean | sensitive | blocked
    reason: str | None = None
    flagged_at: int = 0
