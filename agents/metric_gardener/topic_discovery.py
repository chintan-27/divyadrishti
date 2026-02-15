from __future__ import annotations

import json

from libs.nlp.navigator import get_client, get_labeling_model
from libs.nlp.embeddings import cosine_similarity, get_model as get_embedding_model

_DISCOVER_PROMPT = """\
You are a topic analyst for a Hacker News intelligence dashboard.

Read the following sample of recent HN stories and comments carefully. Your job is to \
identify the SPECIFIC broad themes and concerns that people are ACTUALLY discussing \
in this content — not generic tech categories.

Rules:
- Extract 10-25 topics that are GROUNDED in the content you see. Every topic must \
relate to something explicitly discussed in at least 2-3 items.
- Labels should be specific and descriptive (3-6 words). NOT vague categories like \
"Cybersecurity" or "Developer Experience". GOOD examples: "LLM Coding Assistant Risks", \
"Rust vs C++ Memory Safety", "Tech Layoffs & Hiring Freezes", "Browser Extension Privacy Abuse".
- Definitions should explain what the concern IS and WHY people care, in 1-2 sentences. \
Include the tension or debate if there is one.
- Keywords should be terms/phrases actually used in the content, not generic synonyms.

For each topic, output a JSON object with:
- "label": specific descriptive name (3-6 words), title case
- "definition": 1-2 sentence description of the concern and why it matters to this community
- "keywords": list of 5-10 terms/phrases drawn from the actual content

Output a JSON object with key "topics" containing the array. No other text."""

_MERGE_THRESHOLD = 0.85
_RETIRE_DAYS = 7


def discover_topics(texts: list[str]) -> list[dict[str, object]]:
    """Phase 1: Ask LLM to identify broad-scale concerns from sample texts."""
    client = get_client()
    numbered = "\n".join(f"[{i}] {t[:200]}" for i, t in enumerate(texts[:50]))

    response = client.chat.completions.create(
        model=get_labeling_model(),
        messages=[
            {"role": "system", "content": _DISCOVER_PROMPT},
            {"role": "user", "content": numbered},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
        timeout=60,
    )
    raw = response.choices[0].message.content or "[]"
    parsed = json.loads(raw)

    if isinstance(parsed, dict):
        parsed = parsed.get("topics", parsed.get("results", parsed.get("data", [])))

    return parsed  # type: ignore[return-value]


def anchor_topics(topics: list[dict[str, object]]) -> list[dict[str, object]]:
    """Phase 2: Embed each topic's label+definition+keywords to create centroid vectors."""
    model = get_embedding_model()
    texts_to_embed = []
    for topic in topics:
        label = str(topic.get("label", ""))
        definition = str(topic.get("definition", ""))
        keywords = topic.get("keywords", [])
        kw_str = ", ".join(str(k) for k in keywords) if isinstance(keywords, list) else ""
        texts_to_embed.append(f"{label}. {definition} Keywords: {kw_str}")

    if not texts_to_embed:
        return []

    embeddings = model.encode_batch(texts_to_embed)
    for topic, emb in zip(topics, embeddings):
        topic["centroid"] = emb

    return topics


def reconcile_topics(
    new_topics: list[dict[str, object]],
    existing_nodes: list[tuple[str, str, list[float]]],
) -> tuple[list[dict[str, object]], list[dict[str, object]], list[str]]:
    """Phase 3: Match new topics against existing nodes.

    Args:
        new_topics: Topics with centroids from anchor_topics().
        existing_nodes: List of (node_id, label, centroid) for active nodes.

    Returns:
        (to_create, to_update, to_retire) — new nodes, merged updates, retired node_ids.
    """
    to_create: list[dict[str, object]] = []
    to_update: list[dict[str, object]] = []
    matched_existing: set[str] = set()

    for topic in new_topics:
        centroid = topic.get("centroid")
        if not centroid or not isinstance(centroid, list):
            continue

        best_sim = -1.0
        best_node_id = None
        best_label = None

        for node_id, label, existing_centroid in existing_nodes:
            if not existing_centroid:
                continue
            sim = cosine_similarity(centroid, existing_centroid)
            if sim > best_sim:
                best_sim = sim
                best_node_id = node_id
                best_label = label

        if best_sim >= _MERGE_THRESHOLD and best_node_id is not None:
            matched_existing.add(best_node_id)
            to_update.append({
                "node_id": best_node_id,
                "label": topic.get("label", best_label),
                "definition": topic.get("definition", ""),
                "centroid": centroid,
            })
        else:
            to_create.append(topic)

    # Nodes not matched by any new topic are candidates for retirement
    to_retire = [
        node_id for node_id, _, _ in existing_nodes
        if node_id not in matched_existing
    ]

    return to_create, to_update, to_retire
