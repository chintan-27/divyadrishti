from pydantic import BaseModel


class HNItem(BaseModel):
    id: int
    type: str | None = None
    by: str | None = None
    author_hash: str | None = None
    time: int | None = None
    text: str | None = None
    text_clean: str | None = None
    parent: int | None = None
    kids: list[int] | None = None
    title: str | None = None
    url: str | None = None
    score: int | None = None
    descendants: int | None = None
    deleted: bool | None = None
    dead: bool | None = None
