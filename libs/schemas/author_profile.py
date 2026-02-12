from pydantic import BaseModel


class AuthorProfile(BaseModel):
    author_hash: str
    first_seen_time: int = 0
    last_seen_time: int = 0
    comment_count: int = 0
    story_count: int = 0
    spam_score: float = 0.0
    bot_likelihood: float = 0.0
    influence_cap_state: str = "normal"
