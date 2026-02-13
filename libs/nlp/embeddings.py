from __future__ import annotations

import math

import numpy as np

_MODEL_NAME = "all-MiniLM-L6-v2"
_model: EmbeddingModel | None = None


def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Compute cosine similarity between two vectors."""
    va = np.array(a, dtype=np.float32)
    vb = np.array(b, dtype=np.float32)
    dot = float(np.dot(va, vb))
    norm_a = float(np.linalg.norm(va))
    norm_b = float(np.linalg.norm(vb))
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def softmax_weights(similarities: list[float], temperature: float = 1.0) -> list[float]:
    """Apply softmax to similarity scores."""
    arr = np.array(similarities, dtype=np.float64) / temperature
    arr -= np.max(arr)  # numerical stability
    exp = np.exp(arr)
    total = float(np.sum(exp))
    if total == 0:
        return [0.0] * len(similarities)
    return (exp / total).tolist()  # type: ignore[return-value]


class EmbeddingModel:
    def __init__(self) -> None:
        from sentence_transformers import SentenceTransformer
        self._model = SentenceTransformer(_MODEL_NAME)

    def encode(self, text: str) -> list[float]:
        """Encode a single text to a 384-dim vector."""
        vec = self._model.encode(text, convert_to_numpy=True)
        return vec.tolist()  # type: ignore[union-attr]

    def encode_batch(self, texts: list[str]) -> list[list[float]]:
        """Encode a batch of texts."""
        vecs = self._model.encode(texts, convert_to_numpy=True)
        return [v.tolist() for v in vecs]  # type: ignore[union-attr]


def get_model() -> EmbeddingModel:
    """Lazy singleton loader."""
    global _model  # noqa: PLW0603
    if _model is None:
        _model = EmbeddingModel()
    return _model
