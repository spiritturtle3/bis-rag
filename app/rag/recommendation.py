import time

from app.database.standard_repository import get_standard
from app.rag.enricher import enrich_recommendations
from app.rag.hybrid_search import hybrid_search
from app.rag.query_translator import translate_query
from app.rag.ranker import rank_standards
from app.rag.confidence import (
    add_confidence_scores,
    filter_by_confidence,
    has_reliable_match,
)
from app.rag.relevance import filter_irrelevant


def _expand_relationships(
    recommendations: list[dict],
) -> list[dict]:
    """
    Add allied and related standards to each primary recommendation.
    """

    expanded = []

    for recommendation in recommendations:
        standard_number = recommendation.get("standardNumber")

        if not standard_number:
            expanded.append(recommendation)
            continue

        standard = get_standard(standard_number)

        if not standard:
            expanded.append(recommendation)
            continue

        allied = standard.get("alliedStandards", [])
        relationships = standard.get(
            "standardRelationships",
            [],
        )

        related_standards = []

        for item in allied:
            related_standards.append(
                {
                    "standardNumber": item.get(
                        "standardNumber"
                    ),
                    "relationshipType": item.get(
                        "relationshipType"
                    ),
                    "title": item.get("title"),
                    "description": item.get(
                        "description"
                    ),
                }
            )

        existing_numbers = {
            item.get("standardNumber")
            for item in related_standards
        }

        for item in relationships:
            related_number = item.get(
                "relatedStandardNumber"
            )

            if (
                not related_number
                or related_number in existing_numbers
            ):
                continue

            related_standards.append(
                {
                    "standardNumber": related_number,
                    "relationshipType": item.get(
                        "relationshipType"
                    ),
                    "title": None,
                    "description": item.get(
                        "description"
                    ),
                }
            )

        enriched_recommendation = dict(
            recommendation
        )

        enriched_recommendation[
            "relatedStandards"
        ] = related_standards

        expanded.append(
            enriched_recommendation
        )

    return expanded


def recommend_standards(
    query: str,
    limit: int = 5,
    relevance_query: str | None = None,
) -> list[dict]:

    total_start = time.perf_counter()

    if not query or not query.strip():
        return []

    # -------------------------
    # Query translation
    # -------------------------
    stage_start = time.perf_counter()

    search_query = translate_query(query)

    print(
        f"TIMING translate_query: "
        f"{time.perf_counter() - stage_start:.3f}s"
    )

    if not search_query:
        return []

    # -------------------------
    # Hybrid retrieval
    # -------------------------
    stage_start = time.perf_counter()

    retrieval_limit = max(
        limit * 3,
        10,
    )

    results = hybrid_search(
        search_query,
        limit=retrieval_limit,
    )

    print(
        f"TIMING hybrid_search: "
        f"{time.perf_counter() - stage_start:.3f}s"
    )

    if not results:
        return []

    # -------------------------
    # Ranking
    # -------------------------
    stage_start = time.perf_counter()

    ranked = rank_standards(
        search_query,
        results,
        limit=retrieval_limit,
    )

    print(
        f"TIMING rank_standards: "
        f"{time.perf_counter() - stage_start:.3f}s"
    )

    if not ranked:
        return []

    # -------------------------
    # Metadata enrichment
    # -------------------------
    stage_start = time.perf_counter()

    relevance_candidates = []

    for result in ranked:
        enriched = dict(result)

        standard = get_standard(
            result.get("standardNumber")
        )

        if standard:
            enriched["title"] = standard.get(
                "title",
                "",
            )
            enriched["scope"] = standard.get(
                "scope",
                "",
            )
            enriched["keywords"] = standard.get(
                "keywords",
                [],
            )

        relevance_candidates.append(enriched)

    print(
        f"TIMING metadata_enrichment: "
        f"{time.perf_counter() - stage_start:.3f}s"
    )

    # -------------------------
    # Relevance filtering
    # -------------------------
    stage_start = time.perf_counter()

    relevance_search_query = (
        relevance_query.strip()
        if relevance_query
        and relevance_query.strip()
        else search_query
    )

    relevant = filter_irrelevant(
        relevance_search_query,
        relevance_candidates,
    )

    print(
        f"TIMING relevance_filter: "
        f"{time.perf_counter() - stage_start:.3f}s"
    )

    if not relevant:
        return []

    # -------------------------
    # Confidence scoring
    # -------------------------
    stage_start = time.perf_counter()

    scored = add_confidence_scores(
        relevant,
        query=search_query,
    )

    print(
        f"TIMING confidence_scoring: "
        f"{time.perf_counter() - stage_start:.3f}s"
    )

    if not has_reliable_match(scored):
        return []

    filtered = filter_by_confidence(
        scored
    )

    if not filtered:
        return []

    filtered = filtered[:limit]

    # -------------------------
    # Final enrichment
    # -------------------------
    stage_start = time.perf_counter()

    enriched = enrich_recommendations(
        filtered
    )

    print(
        f"TIMING enrich_recommendations: "
        f"{time.perf_counter() - stage_start:.3f}s"
    )

    # -------------------------
    # Relationship expansion
    # -------------------------
    stage_start = time.perf_counter()

    expanded = _expand_relationships(
        enriched
    )

    print(
        f"TIMING relationship_expansion: "
        f"{time.perf_counter() - stage_start:.3f}s"
    )

    # -------------------------
    # Total
    # -------------------------
    print(
        f"TIMING TOTAL recommend_standards: "
        f"{time.perf_counter() - total_start:.3f}s"
    )

    return expanded