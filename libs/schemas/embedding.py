from pydantic import BaseModel


class Embedding(BaseModel):
    item_id: int
    embedding: list[float]
    model_version: str = ""
