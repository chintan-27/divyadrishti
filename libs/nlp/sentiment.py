from __future__ import annotations

import json

from libs.nlp.navigator import get_client, get_opinion_model
from libs.schemas.opinion_signal import OpinionSignal

_MODEL_VERSION = "navigator-llama-3.3-70b"

_SYSTEM_PROMPT = """\
You are a sentiment analysis model calibrated for Hacker News tech discourse.
For each text, output a JSON object with these fields:
- "label": one of "positive", "negative", or "neutral"
- "valence": float from -100 to +100 (negative=critical, positive=enthusiastic, 0=neutral)
- "intensity": float from 0 to 1 (how emotionally charged the text is)
- "confidence": float from 0 to 1 (how certain you are about the label)

HN-specific calibration:
- Technical criticism ("this approach is fundamentally flawed") = negative, high intensity
- Dry humor or sarcasm = adjust valence accordingly
- Factual statements without opinion = neutral, low intensity
- Enthusiasm about technology = positive, moderate intensity

Output ONLY a JSON array of objects, one per input text. No other text."""

_model: SentimentModel | None = None


class SentimentModel:
    def __init__(self) -> None:
        self._client = get_client()

    def predict(self, text: str) -> OpinionSignal:
        """Predict sentiment for a single text."""
        return self.predict_batch([text])[0]

    def predict_batch(self, texts: list[str]) -> list[OpinionSignal]:
        """Predict sentiment for a batch of texts."""
        numbered = "\n".join(f"[{i}] {t[:500]}" for i, t in enumerate(texts))
        response = self._client.chat.completions.create(
            model=get_opinion_model(),
            messages=[
                {"role": "system", "content": _SYSTEM_PROMPT},
                {"role": "user", "content": numbered},
            ],
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content or "[]"
        parsed = json.loads(raw)

        # Handle both {"results": [...]} and [...] formats
        if isinstance(parsed, dict):
            parsed = parsed.get("results", parsed.get("data", []))

        signals: list[OpinionSignal] = []
        for i, text in enumerate(texts):
            if i < len(parsed):
                entry = parsed[i]
            else:
                entry = {"label": "neutral", "valence": 0.0, "intensity": 0.0, "confidence": 0.5}

            signals.append(OpinionSignal(
                item_id=0,
                valence=round(float(entry.get("valence", 0.0)), 2),
                intensity=round(float(entry.get("intensity", 0.0)), 4),
                confidence=round(float(entry.get("confidence", 0.5)), 4),
                label=entry.get("label", "neutral"),
                model_version=_MODEL_VERSION,
            ))

        return signals


def get_model() -> SentimentModel:
    """Lazy singleton loader."""
    global _model  # noqa: PLW0603
    if _model is None:
        _model = SentimentModel()
    return _model
