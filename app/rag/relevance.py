from __future__ import annotations

import re


STOPWORDS = {
    "a",
    "an",
    "and",
    "are",
    "as",
    "at",
    "be",
    "by",
    "for",
    "from",
    "in",
    "is",
    "of",
    "on",
    "or",
    "the",
    "to",
    "with",
}


def _tokenize(text: str) -> set[str]:
    tokens = set(
        re.findall(r"\b[a-z0-9]+\b", text.lower())
    )

    return tokens - STOPWORDS


def _overlap(
    query_tokens: set[str],
    text: str,
) -> float:
    tokens = _tokenize(text)

    if not tokens:
        return 0.0

    return len(
        query_tokens.intersection(tokens)
    ) / len(query_tokens)


def _relevance_score(
    query: str,
    result: dict,
) -> float:
    """
    Calculate relevance using meaningful product terms.

    Scope and title alignment are weighted most heavily.
    Generic stopwords are excluded from token matching.
    """

    query_tokens = _tokenize(query)

    if not query_tokens:
        return 0.0

    scope_score = _overlap(
        query_tokens,
        result.get("scope", ""),
    )

    title_score = _overlap(
        query_tokens,
        result.get("title", ""),
    )

    keywords = result.get("keywords", [])

    if isinstance(keywords, list):
        keywords = " ".join(
            str(item)
            for item in keywords
        )

    keyword_score = _overlap(
        query_tokens,
        keywords,
    )

    chunk_score = _overlap(
        query_tokens,
        result.get("bestChunk", ""),
    )

    score = (
        scope_score * 0.45
        + title_score * 0.30
        + keyword_score * 0.20
        + chunk_score * 0.05
    )

    return min(score, 1.0)


def filter_irrelevant(
    query: str,
    results: list[dict],
    threshold: float = 0.10,
) -> list[dict]:
    """
    Remove candidates with weak product/scope alignment.
    """

    filtered = []

    for result in results:
        relevance = _relevance_score(
            query,
            result,
        )

        enriched = dict(result)
        enriched["relevanceScore"] = round(
            relevance,
            4,
        )

        if relevance >= threshold:
            filtered.append(enriched)

    return filtered