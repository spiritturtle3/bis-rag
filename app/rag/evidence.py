import re
from typing import Any

MEANINGFUL_SECTIONS = (
    "Scope",
    "Product Details",
    "Technical Requirements",
    "Testing and Inspection",
    "Procurement Relevance",
    "Compliance",
    "Current Edition",
    "Amendments",
)


def _unique(values: list[str]) -> list[str]:
    result = []

    for value in values:
        value = str(value).strip()

        if value and value.lower() not in {
            item.lower() for item in result
        }:
            result.append(value)

    return result


def _clean_excerpt(text: str) -> str:
    text = str(text).strip()

    if not text:
        return ""

    section_pattern = re.compile(
        r"(?m)^(?:"
        + "|".join(
            re.escape(section)
            for section in MEANINGFUL_SECTIONS
        )
        + r"):\s*"
    )

    match = section_pattern.search(text)

    if match:
        return text[match.start():].strip()

    return text


def _build_chunk_evidence(
    recommendation: dict,
) -> list[dict]:
    """
    Build evidence from the strongest matched chunks.

    Up to three chunks are returned so the evidence can cover
    different parts of a standard such as scope, requirements,
    testing, compliance, and procurement relevance.
    """

    matched_chunks = recommendation.get(
        "matchedChunkData",
        [],
    )

    if not matched_chunks:
        best_chunk = recommendation.get(
            "bestChunk"
        )

        if not best_chunk:
            return []

        matched_chunks = [
            {
                "source": recommendation.get(
                    "source"
                ),
                "page": recommendation.get(
                    "page"
                ),
                "chunkIndex": recommendation.get(
                    "chunkIndex"
                ),
                "text": best_chunk,
                "score": recommendation.get(
                    "score",
                    0,
                ),
            }
        ]

    # Prefer chunks with stronger retrieval scores.
    ranked_chunks = sorted(
        matched_chunks,
        key=lambda chunk: chunk.get(
            "score",
            0,
        ),
        reverse=True,
    )

    evidence = []

    for chunk in ranked_chunks[:3]:
        excerpt = _clean_excerpt(
            chunk.get("text", "")
        )

        if not excerpt:
            continue

        evidence.append(
            {
                "source": chunk.get(
                    "source"
                )
                or "BIS",
                "standardNumber": recommendation.get(
                    "standardNumber"
                ),
                "page": chunk.get(
                    "page"
                ),
                "chunkIndex": chunk.get(
                    "chunkIndex"
                ),
                "excerpt": excerpt,
            }
        )

    return evidence


def build_evidence(
    recommendation: dict,
) -> dict:
    product_details = (
        recommendation.get(
            "productDetails"
        )
        or {}
    )

    technical = (
        recommendation.get(
            "technicalRequirements"
        )
        or {}
    )

    procurement = (
        recommendation.get(
            "procurementRelevance"
        )
        or {}
    )

    edition = (
        recommendation.get(
            "currentEdition"
        )
        or {}
    )

    amendments = (
        recommendation.get(
            "amendments"
        )
        or {}
    )

    evidence_points = []

    scope = recommendation.get(
        "scope"
    )

    if scope:
        evidence_points.append(
            scope
        )

    evidence_points.extend(
        _unique(
            product_details.get(
                "intendedUses",
                [],
            )
            + product_details.get(
                "applications",
                [],
            )
            + product_details.get(
                "synonyms",
                [],
            )
        )
    )

    evidence_points.extend(
        _unique(
            technical.get(
                "keyRequirements",
                [],
            )
            + technical.get(
                "performanceRequirements",
                [],
            )
            + technical.get(
                "designRequirements",
                [],
            )
        )
    )

    evidence_points.extend(
        _unique(
            procurement.get(
                "specificationPoints",
                [],
            )
            + procurement.get(
                "buyerConsiderations",
                [],
            )
        )
    )

    return {
        "standardNumber": recommendation.get(
            "standardNumber"
        ),
        "title": recommendation.get(
            "title"
        ),
        "confidence": recommendation.get(
            "confidence"
        ),
        "evidencePoints": evidence_points,
        "evidence": _build_chunk_evidence(
            recommendation
        ),
        "scope": scope or "",
        "currentEdition": edition,
        "amendments": amendments,
        "certification": recommendation.get(
            "compliance"
        ),
        "procurementRelevance": procurement,
        "matchedChunks": recommendation.get(
            "matchedChunks",
            0,
        ),
        "source": recommendation.get(
            "source"
        ),
    }


def build_evidence_for_recommendations(
    recommendations: list[dict],
) -> list[dict]:
    return [
        build_evidence(recommendation)
        for recommendation in recommendations
    ]
