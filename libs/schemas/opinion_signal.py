from pydantic import BaseModel


class OpinionSignal(BaseModel):
    item_id: int
    valence: float = 0.0  # -100..+100
    intensity: float = 0.0  # 0..1
    confidence: float = 0.0  # 0..1
    label: str = "neutral"  # positive | negative | neutral
    model_version: str = ""
