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
    """
    Recommend BIS standards for a natural-language query.

    Flow:
        User Query
        ↓
        Multilingual Translation
        ↓
        Hybrid Retrieval
        ↓
        Standard-level Ranking
        ↓
        Relevance Filtering
        ↓
        Confidence Scoring
        ↓
        Confidence Filtering
        ↓
        Metadata Enrichment
        ↓
        Allied/Related Standard Expansion
        ↓
        Recommendations

    `relevance_query` can be supplied when the retrieval query is
    intentionally long, such as a tender document. Retrieval still
    uses the full query, while relevance filtering uses the focused
    product-oriented query.
    """

    if not query or not query.strip():
        return []

    search_query = translate_query(query)

    if not search_query:
        return []

    retrieval_limit = max(
        limit * 3,
        10,
    )

    results = hybrid_search(
        search_query,
        limit=retrieval_limit,
    )

    if not results:
        return []

    ranked = rank_standards(
        search_query,
        results,
        limit=retrieval_limit,
    )

    if not ranked:
        return []

    # Add metadata needed by the relevance filter.
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

    # Use a focused relevance query when provided.
    # This prevents long tender text from diluting
    # meaningful product-term overlap.
    relevance_search_query = (
        relevance_query.strip()
        if relevance_query
        and relevance_query.strip()
        else search_query
    )

    # Remove clearly unrelated standards before confidence scoring.
    relevant = filter_irrelevant(
        relevance_search_query,
        relevance_candidates,
    )

    if not relevant:
        return []

    # Calculate confidence after relevance filtering.
    scored = add_confidence_scores(
        relevant,
        query=search_query,
    )

    if not has_reliable_match(scored):
        return []

    filtered = filter_by_confidence(
        scored
    )

    if not filtered:
        return []

    filtered = filtered[:limit]

    enriched = enrich_recommendations(
        filtered
    )

    expanded = _expand_relationships(
        enriched
    )

    return expanded