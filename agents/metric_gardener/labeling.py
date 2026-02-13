from __future__ import annotations

from collections import Counter


def generate_label(texts: list[str], top_n: int = 3) -> tuple[str, str]:
    """Generate a label and definition from representative texts using TF-IDF-like term extraction.

    Returns (label, definition).
    """
    if not texts:
        return ("unknown", "No texts available")

    # simple term frequency across documents
    word_counts: Counter[str] = Counter()
    doc_count = len(texts)
    doc_freq: Counter[str] = Counter()

    stopwords = frozenset([
        "the", "a", "an", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "shall", "can", "to", "of", "in", "for",
        "on", "with", "at", "by", "from", "as", "into", "through", "during",
        "before", "after", "above", "below", "between", "out", "off", "up",
        "down", "and", "but", "or", "nor", "not", "so", "yet", "both",
        "either", "neither", "each", "every", "all", "any", "few", "more",
        "most", "other", "some", "such", "no", "only", "own", "same", "than",
        "too", "very", "just", "about", "it", "its", "this", "that", "these",
        "those", "i", "you", "he", "she", "we", "they", "me", "him", "her",
        "us", "them", "my", "your", "his", "our", "their", "what", "which",
        "who", "whom", "how", "when", "where", "why", "if", "then", "there",
    ])

    for text in texts:
        words = set()
        for word in text.lower().split():
            cleaned = "".join(c for c in word if c.isalnum())
            if cleaned and len(cleaned) > 2 and cleaned not in stopwords:
                word_counts[cleaned] += 1
                words.add(cleaned)
        doc_freq.update(words)

    # TF-IDF-like scoring: term freq * log(inverse doc freq)
    import math
    scored: list[tuple[str, float]] = []
    for word, tf in word_counts.items():
        df = doc_freq[word]
        if df < 2 and doc_count > 5:
            continue  # skip very rare terms in larger corpora
        idf = math.log(doc_count / max(df, 1)) + 1
        scored.append((word, tf * idf))

    scored.sort(key=lambda x: x[1], reverse=True)
    top_terms = [w for w, _ in scored[:top_n]]

    if not top_terms:
        return ("misc", "Miscellaneous topics")

    label = " / ".join(top_terms[:2]).title()
    definition = f"Topics related to: {', '.join(top_terms)}"
    return (label, definition)
