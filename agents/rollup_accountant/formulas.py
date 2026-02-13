"""Pure formula functions for metric rollup computation."""
from __future__ import annotations

import math


def compute_split(positive_share: float, negative_share: float) -> float:
    """Split/controversy score: high when opinion is evenly divided.

    Returns 0..100. Max split when positive == negative == 0.5.
    Uses 1 - |pos - neg| scaled to 100.
    """
    if positive_share + negative_share == 0:
        return 0.0
    return round((1.0 - abs(positive_share - negative_share)) * 100, 2)


def compute_consensus(positive_share: float, negative_share: float) -> tuple[float, float]:
    """Compute positive and negative consensus scores.

    Returns (consensus_pos, consensus_neg), each 0..100.
    High when one side strongly dominates.
    """
    total = positive_share + negative_share
    if total == 0:
        return (0.0, 0.0)
    pos_consensus = round((positive_share / total) * 100, 2) if positive_share > negative_share else 0.0
    neg_consensus = round((negative_share / total) * 100, 2) if negative_share > positive_share else 0.0
    return (pos_consensus, neg_consensus)


def compute_heat(total_intensity: float, unique_authors: int) -> float:
    """Heat score: intensity * unique authors.

    Measures how intensely and broadly a topic is being discussed.
    """
    return round(total_intensity * math.log1p(unique_authors), 2)


def compute_momentum(current_presence: float, baseline_presence: float) -> float:
    """Momentum: current vs baseline presence ratio.

    Returns percentage change. Positive = rising, negative = falling.
    """
    if baseline_presence == 0:
        return 100.0 if current_presence > 0 else 0.0
    return round(((current_presence - baseline_presence) / baseline_presence) * 100, 2)
