from __future__ import annotations

from typing import Any


def _relevance_level(
    confidence: float | None,
    applicability: str | None = None,
) -> str:
    if confidence is None:
        return "Unknown"

    role = (applicability or "").strip().lower()

    if role == "primary":
        if confidence >= 0.30:
            return "High"
        return "Moderate"

    if role == "supporting":
        if confidence >= 0.60:
            return "High"
        if confidence >= 0.30:
            return "Moderate"
        return "Low"

    if role == "related/reference":
        return "Low"

    if confidence >= 0.75:
        return "High"
    if confidence >= 0.50:
        return "Moderate"
    if confidence >= 0.30:
        return "Low"

    return "Very Low"


def _certification_status(
    compliance: dict[str, Any],
) -> str:
    if compliance.get("certificationRequired") is True:
        return "Required"

    if compliance.get("certificationRequired") is False:
        return "Not identified as required"

    return "Not identified"


def _format_certification(
    compliance: dict[str, Any],
) -> dict[str, Any]:
    return {
        "status": _certification_status(compliance),
        "scheme": compliance.get("certificationScheme"),
        "mandatory": compliance.get("mandatory"),
        "crsApplicable": compliance.get(
            "crsApplicability"
        ),
        "hallmarkingApplicable": compliance.get(
            "hallmarkingApplicability"
        ),
        "qualityControlOrder": compliance.get(
            "qualityControlOrder"
        ),
        "note": compliance.get("notes") or None,
    }


def _format_version(
    standard: dict[str, Any],
) -> dict[str, Any]:
    edition = standard.get("currentEdition") or {}
    amendments = standard.get("amendments") or []

    latest_amendment = None

    if amendments:
        latest_amendment = max(
            amendments,
            key=lambda item: str(
                item.get("date", "")
            ),
        )

    return {
        "edition": edition.get("edition"),
        "year": edition.get("year"),
        "status": edition.get("status"),
        "latestAmendment": (
            {
                "amendmentNumber": latest_amendment.get(
                    "amendmentNumber"
                ),
                "date": latest_amendment.get("date"),
                "title": latest_amendment.get("title"),
            }
            if latest_amendment
            else None
        ),
    }


def _format_testing(
    standard: dict[str, Any],
) -> dict[str, Any]:
    testing = (
        standard.get("testingAndInspection") or {}
    )

    return {
        "required": testing.get("required"),
        "testMethods": (
            testing.get("testMethods") or []
        ),
        "relatedTestStandards": (
            testing.get("relatedTestStandards")
            or []
        ),
        "inspectionRequirements": (
            testing.get(
                "inspectionRequirements"
            )
            or []
        ),
    }


def _format_related_standards(
    standard: dict[str, Any],
) -> list[dict[str, Any]]:
    related = (
        standard.get("relatedStandards")
        or standard.get("alliedStandards")
        or []
    )

    formatted = []

    for item in related:
        if not isinstance(item, dict):
            continue

        standard_number = item.get(
            "standardNumber"
        )

        if not standard_number:
            continue

        formatted.append(
            {
                "standardNumber": standard_number,
                "relationship": item.get(
                    "relationshipType"
                ),
                "title": item.get("title"),
                "reason": item.get(
                    "description"
                ),
            }
        )

    return formatted


def _format_evidence(
    standard: dict[str, Any],
) -> list[dict[str, Any]]:
    """
    Format retrieved RAG evidence for the frontend.

    Prefer actual retrieved chunk evidence because it provides
    traceable excerpts from the source used during retrieval.
    """

    matched_chunks = standard.get(
        "matchedChunkData"
    ) or []

    if matched_chunks:
        evidence = []

        for chunk in matched_chunks[:3]:
            if not isinstance(chunk, dict):
                continue

            excerpt = str(
                chunk.get("text") or ""
            ).strip()

            if not excerpt:
                continue

            evidence.append(
                {
                    "source": (
                        chunk.get("source")
                        or "BIS"
                    ),
                    "standardNumber": standard.get(
                        "standardNumber"
                    ),
                    "page": chunk.get("page"),
                    "chunkIndex": chunk.get(
                        "chunkIndex"
                    ),
                    "excerpt": excerpt,
                }
            )

        if evidence:
            return evidence

    # Fallback to source-level evidence references
    # when retrieved chunk data is unavailable.
    source = standard.get("source") or {}

    references = (
        source.get("evidenceReferences") or []
    )

    evidence = []

    for reference in references:
        if not isinstance(reference, dict):
            continue

        evidence.append(
            {
                "source": (
                    source.get("sourceName")
                    or "BIS"
                ),
                "standardNumber": standard.get(
                    "standardNumber"
                ),
                "page": reference.get("page"),
                "section": reference.get(
                    "section"
                ),
                "clause": reference.get(
                    "clause"
                ),
            }
        )

    return evidence


def format_recommendation(
    standard: dict[str, Any],
    llm_recommendation: dict[str, Any] | None = None,
) -> dict[str, Any]:
    procurement = (
        standard.get("procurementRelevance")
        or {}
    )

    compliance = (
        standard.get("compliance") or {}
    )

    llm_recommendation = (
        llm_recommendation or {}
    )

    confidence = standard.get("confidence")

    applicability = llm_recommendation.get(
        "applicability",
        "Supporting",
    )

    return {
        "standardNumber": standard.get(
            "standardNumber"
        ),
        "title": standard.get("title"),
        "applicability": applicability,
        "relevance": {
            "level": _relevance_level(
                confidence,
                applicability,
            ),
        },
        "reason": (
            llm_recommendation.get("reason")
            or standard.get("scope")
        ),
        "version": _format_version(
            standard
        ),
        "certification": _format_certification(
            compliance
        ),
        "testing": _format_testing(
            standard
        ),
        "relatedStandards": (
            _format_related_standards(
                standard
            )
        ),
        "procurement": {
            "applicable": procurement.get(
                "applicableToProcurement"
            ),
            "recommendedFor": (
                procurement.get(
                    "recommendedFor"
                )
                or []
            ),
            "specificationPoints": (
                procurement.get(
                    "specificationPoints"
                )
                or []
            ),
            "buyerConsiderations": (
                procurement.get(
                    "buyerConsiderations"
                )
                or []
            ),
        },
        "evidence": _format_evidence(
            standard
        ),
    }


def _clean_summary(
    summary: str | None,
) -> str:
    if not summary:
        return (
            "The analysis did not generate "
            "a summary."
        )

    summary = str(summary).strip()

    replacements = {
        "requires adherence to": (
            "is identified as applicable to"
        ),
        "must comply with": (
            "is identified as applicable to"
        ),
        "must adhere to": (
            "is identified as applicable to"
        ),
    }

    for old, new in replacements.items():
        summary = summary.replace(
            old,
            new,
        )

    return summary


def format_frontend_response(
    query: str,
    recommendations: list[dict[str, Any]],
    answer: dict[str, Any] | None = None,
) -> dict[str, Any]:
    answer = answer or {}

    llm_recommendations = {
        item.get("standardNumber"): item
        for item in answer.get(
            "recommendations",
            [],
        )
        if (
            isinstance(item, dict)
            and item.get("standardNumber")
        )
    }

    formatted_recommendations = []

    for standard in recommendations:
        standard_number = standard.get(
            "standardNumber"
        )

        formatted_recommendations.append(
            format_recommendation(
                standard,
                llm_recommendations.get(
                    standard_number
                ),
            )
        )

    user_warnings = []

    for warning in answer.get(
        "warnings",
        [],
    ):
        warning_text = str(warning)

        if "LLM output referenced" in warning_text:
            continue

        user_warnings.append(
            warning_text
        )

    return {
        "query": query,
        "summary": _clean_summary(
            answer.get("summary")
        ),
        "recommendations": (
            formatted_recommendations
        ),
        "warnings": user_warnings,
    }
