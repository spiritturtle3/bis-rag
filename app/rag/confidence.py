from __future__ import annotations

import re
from typing import Any


STRONG_MATCH_THRESHOLD = 0.60
WEAK_MATCH_THRESHOLD = 0.30


def _tokenize(text: str) -> set[str]:
    """Convert text into normalized word tokens."""
    return set(re.findall(r"\b[a-z0-9]+\b", text.lower()))


def _ranking_strength(ranking_score: float) -> float:
    """Convert ranking score into a bounded signal."""
    return min(max(ranking_score, 0.0), 1.0)


def _chunk_strength(matched_chunks: int) -> float:
    """Measure strength from the number of matched chunks."""
    return min(max(matched_chunks, 0) / 3.0, 1.0)


def _relative_strength(
    result: dict[str, Any],
    results: list[dict[str, Any]],
) -> float:
    """Measure how strongly a result stands out from candidates."""

    if not results:
        return 0.0

    scores = [
        float(item.get("rankingScore", 0.0))
        for item in results
    ]

    maximum_score = max(scores)

    if maximum_score <= 0:
        return 0.0

    ranking_score = float(
        result.get("rankingScore", 0.0)
    )

    return min(
        max(ranking_score / maximum_score, 0.0),
        1.0,
    )


def _scope_relevance(
    query: str,
    scope: str,
) -> float:
    """
    Measure lexical alignment between query and standard scope.
    """

    query_tokens = _tokenize(query)
    scope_tokens = _tokenize(scope)

    if not query_tokens or not scope_tokens:
        return 0.0

    overlap = query_tokens.intersection(scope_tokens)

    return len(overlap) / len(query_tokens)


def calculate_confidence(
    result: dict[str, Any],
    results: list[dict[str, Any]] | None = None,
    query: str = "",
) -> float:
    """
    Calculate heuristic confidence.

    This is NOT a probability.

    Signals:
      - ranking strength
      - relative ranking
      - matched chunks
      - scope relevance
    """

    if results is None:
        results = [result]

    ranking_score = float(
        result.get("rankingScore", 0.0)
    )

    matched_chunks = int(
        result.get("matchedChunks", 0)
    )

    ranking_signal = _ranking_strength(
        ranking_score
    )

    relative_signal = _relative_strength(
        result,
        results,
    )

    chunk_signal = _chunk_strength(
        matched_chunks
    )

    confidence = (
        0.40 * ranking_signal
        + 0.35 * relative_signal
        + 0.15 * chunk_signal
    )

    # Scope is used as a relevance adjustment rather
    # than a hard filter, so allied standards can remain.
    if query:
        scope = result.get("scope") or ""

        if scope:
            scope_signal = _scope_relevance(
                query,
                scope,
            )

            # Strong scope alignment gets a small boost.
            if scope_signal >= 0.15:
                confidence += 0.10

            # Clearly unrelated scope gets a strong penalty.
            elif scope_signal < 0.08:
                confidence *= 0.40

            # Weak scope alignment gets a moderate penalty.
            elif scope_signal < 0.12:
                confidence *= 0.75

    return round(
        min(max(confidence, 0.0), 1.0),
        4,
    )


def add_confidence_scores(
    results: list[dict[str, Any]],
    query: str = "",
) -> list[dict[str, Any]]:
    """Add confidence scores to all ranked results."""

    scored_results = []

    for result in results:
        enriched = dict(result)

        enriched["confidence"] = calculate_confidence(
            result,
            results,
            query=query,
        )

        scored_results.append(enriched)

    return scored_results


def filter_by_confidence(
    results: list[dict[str, Any]],
    threshold: float = WEAK_MATCH_THRESHOLD,
) -> list[dict[str, Any]]:
    """Remove recommendations below minimum confidence."""

    return [
        result
        for result in results
        if float(
            result.get("confidence", 0.0)
        ) >= threshold
    ]


def has_reliable_match(
    results: list[dict[str, Any]],
    threshold: float = STRONG_MATCH_THRESHOLD,
) -> bool:
    """Check whether at least one strong recommendation exists."""

    return any(
        float(
            result.get("confidence", 0.0)
        ) >= threshold
        for result in results
    )


def build_fallback_response(
    query: str,
) -> dict[str, Any]:
    """Response returned when no reliable standard is identified."""

    return {
        "query": query,
        "recommendations": [],
        "fallback": True,
        "message": (
            "No reliable matching Indian Standard was found "
            "in the available dataset."
        ),
    }