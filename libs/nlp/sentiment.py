from __future__ import annotations

from libs.schemas.opinion_signal import OpinionSignal

_MODEL_NAME = "cardiffnlp/twitter-roberta-base-sentiment-latest"
_MODEL_VERSION = "twitter-roberta-base-sentiment-latest"

_LABEL_MAP = {
    "positive": "positive",
    "negative": "negative",
    "neutral": "neutral",
}

_VALENCE_MAP = {
    "positive": 1.0,
    "negative": -1.0,
    "neutral": 0.0,
}

_model: SentimentModel | None = None


class SentimentModel:
    def __init__(self) -> None:
        from transformers import AutoModelForSequenceClassification, AutoTokenizer
        import torch

        self._tokenizer = AutoTokenizer.from_pretrained(_MODEL_NAME)
        self._model = AutoModelForSequenceClassification.from_pretrained(_MODEL_NAME)
        self._model.eval()
        self._torch = torch

    def predict(self, text: str) -> OpinionSignal:
        """Predict sentiment for a single text."""
        return self.predict_batch([text])[0]

    def predict_batch(self, texts: list[str]) -> list[OpinionSignal]:
        """Predict sentiment for a batch of texts."""
        torch = self._torch
        inputs = self._tokenizer(
            texts, return_tensors="pt", truncation=True,
            padding=True, max_length=512,
        )
        with torch.no_grad():
            outputs = self._model(**inputs)
        probs = torch.nn.functional.softmax(outputs.logits, dim=-1)

        # Model labels: 0=negative, 1=neutral, 2=positive
        label_names = ["negative", "neutral", "positive"]
        signals: list[OpinionSignal] = []

        for i in range(len(texts)):
            prob_vec = probs[i]
            top_idx = int(torch.argmax(prob_vec).item())
            label = label_names[top_idx]
            confidence = float(prob_vec[top_idx].item())
            valence_dir = _VALENCE_MAP.get(label, 0.0)
            valence = valence_dir * confidence * 100
            intensity = float(max(prob_vec[0].item(), prob_vec[2].item()))

            signals.append(OpinionSignal(
                item_id=0,
                valence=round(valence, 2),
                intensity=round(intensity, 4),
                confidence=round(confidence, 4),
                label=label,
                model_version=_MODEL_VERSION,
            ))

        return signals


def get_model() -> SentimentModel:
    """Lazy singleton loader."""
    global _model  # noqa: PLW0603
    if _model is None:
        _model = SentimentModel()
    return _model
