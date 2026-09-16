import re
from collections import defaultdict


def _tokenize(text: str) -> set[str]:
    """Convert text into normalized word tokens."""
    return set(
        re.findall(
            r"\b[a-z0-9]+\b",
            text.lower(),
        )
    )


def _get_score(chunk: dict) -> float:
    """Get the retrieval score from a chunk."""
    return chunk.get(
        "hybridScore",
        chunk.get("score", 0),
    )


def _text_relevance(
    query: str,
    text: str,
) -> float:
    """Calculate lexical relevance between query and chunk text."""
    query_tokens = _tokenize(query)
    text_tokens = _tokenize(text)

    if not query_tokens or not text_tokens:
        return 0.0

    overlap = query_tokens.intersection(text_tokens)

    return len(overlap) / len(query_tokens)


def _semantic_bonus(
    query: str,
    text: str,
) -> float:
    """Give extra weight to important procurement concepts."""
    query_lower = query.lower()
    text_lower = text.lower()

    concept_groups = [
        ["water", "tank", "storage", "reservoir"],
        ["reinforced", "concrete"],
        ["pipe", "pipes"],
        ["brick", "bricks", "masonry"],
        ["door", "doors", "window", "windows"],
        ["earthquake", "seismic"],
        ["plaster", "gypsum"],
    ]

    bonus = 0.0

    for group in concept_groups:
        query_hits = sum(
            word in query_lower
            for word in group
        )

        text_hits = sum(
            word in text_lower
            for word in group
        )

        if query_hits >= 2 and text_hits >= 2:
            bonus += 0.15

    return min(bonus, 0.30)


def rank_standards(
    query: str,
    results: list[dict],
    limit: int = 5,
) -> list[dict]:
    """
    Group retrieved chunks by BIS standard and rank standards.

    Retrieval metadata from all matched chunks is preserved
    for evidence traceability.
    """

    standards = defaultdict(list)

    for result in results:
        standard_number = result.get(
            "standardNumber"
        )

        if not standard_number:
            continue

        standards[
            standard_number
        ].append(result)

    ranked = []

    for standard_number, chunks in standards.items():

        best_chunk = max(
            chunks,
            key=lambda chunk: (
                _get_score(chunk)
                + _text_relevance(
                    query,
                    chunk.get("text", ""),
                )
            ),
        )

        base_score = _get_score(
            best_chunk
        )

        lexical_score = _text_relevance(
            query,
            best_chunk.get("text", ""),
        )

        semantic_bonus = _semantic_bonus(
            query,
            best_chunk.get("text", ""),
        )

        ranking_score = (
            base_score
            + lexical_score
            + semantic_bonus
        )

        matched_chunk_data = []

        for chunk in chunks:
            matched_chunk_data.append(
                {
                    "source": chunk.get(
                        "source"
                    ),
                    "page": chunk.get(
                        "page"
                    ),
                    "chunkIndex": chunk.get(
                        "chunkIndex"
                    ),
                    "text": chunk.get(
                        "text",
                        "",
                    ),
                    "score": _get_score(
                        chunk
                    ),
                }
            )

        ranked.append(
            {
                "standardNumber": standard_number,
                "score": base_score,
                "rankingScore": ranking_score,

                # Best retrieved evidence
                "bestChunk": best_chunk.get(
                    "text",
                    "",
                ),
                "source": best_chunk.get(
                    "source"
                ),
                "page": best_chunk.get(
                    "page"
                ),
                "chunkIndex": best_chunk.get(
                    "chunkIndex"
                ),

                # All chunks matched for this standard
                "matchedChunkData": matched_chunk_data,

                "matchedChunks": len(
                    chunks
                ),
            }
        )

    ranked.sort(
        key=lambda result: result[
            "rankingScore"
        ],
        reverse=True,
    )

    return ranked[:limit]
