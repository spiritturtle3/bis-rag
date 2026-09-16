from pathlib import Path
from typing import Any

from app.rag.evidence import build_evidence_for_recommendations
from app.rag.recommendation import recommend_standards
from app.rag.tender_extractor import extract_tender_text
from app.rag.tender_requirements import (
    build_requirement_query,
    extract_tender_requirements,
)


def _build_relevance_query(
    requirements: dict[str, Any],
) -> str:
    """
    Build a focused product-oriented query for relevance filtering.

    Retrieval uses the full tender requirement query, while this
    query focuses on the characteristics that identify the product.
    """

    parts = []

    product = requirements.get("product")

    if product:
        parts.append(str(product))

    for field in (
        "materials",
        "uses",
        "grades",
        "dimensions",
        "performanceRequirements",
    ):
        values = requirements.get(field, [])

        if not values:
            continue

        for value in values:
            value = str(value).strip()

            if value:
                parts.append(value)

    return " ".join(parts).strip()


def recommend_from_tender(
    query: str | None = None,
    pdf_path: str | Path | None = None,
    limit: int = 5,
) -> dict[str, Any]:
    """
    Generate BIS standard recommendations from a natural-language query,
    a tender PDF, or both, including evidence for each recommendation.
    """

    if not query and not pdf_path:
        return {
            "query": "",
            "tenderRequirements": {},
            "recommendations": [],
            "evidence": [],
            "message": "Provide a query or tender PDF.",
        }

    tender_text = ""
    requirements = {}

    if pdf_path:
        tender_text = extract_tender_text(pdf_path)
        requirements = extract_tender_requirements(
            tender_text
        )

    requirement_query = build_requirement_query(
        requirements
    )

    query_parts = []

    if query and query.strip():
        query_parts.append(query.strip())

    if requirement_query:
        query_parts.append(requirement_query)

    combined_query = " ".join(
        query_parts
    ).strip()

    relevance_query = _build_relevance_query(
        requirements
    )

    recommendations = recommend_standards(
        combined_query,
        limit=limit,
        relevance_query=relevance_query or None,
    )

    evidence = build_evidence_for_recommendations(
        recommendations
    )

    return {
        "query": combined_query,
        "tenderRequirements": requirements,
        "recommendations": recommendations,
        "evidence": evidence,
    }