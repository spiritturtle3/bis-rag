from concurrent.futures import ThreadPoolExecutor

from app.database.standard_repository import get_standard


def _build_status_summary(standard: dict) -> dict:
    edition = standard.get("currentEdition") or {}
    amendments = standard.get("amendments") or []
    compliance = standard.get("compliance") or {}
    procurement = standard.get("procurementRelevance") or {}

    latest_amendment = amendments[-1] if amendments else None

    return {
        "currentEdition": {
            "edition": edition.get("edition"),
            "year": edition.get("year"),
            "publishedDate": edition.get("publishedDate"),
            "status": edition.get("status"),
        },
        "latestAmendment": latest_amendment,
        "certification": {
            "required": compliance.get("certificationRequired"),
            "scheme": compliance.get("certificationScheme"),
            "mandatory": compliance.get("mandatory"),
            "crsApplicable": compliance.get("crsApplicability"),
            "hallmarkingApplicable": compliance.get(
                "hallmarkingApplicability"
            ),
        },
        "procurement": {
            "applicable": procurement.get(
                "applicableToProcurement"
            ),
            "recommendedFor": procurement.get(
                "recommendedFor", []
            ),
            "specificationPoints": procurement.get(
                "specificationPoints", []
            ),
            "buyerConsiderations": procurement.get(
                "buyerConsiderations", []
            ),
        },
    }


def enrich_recommendation(
    result: dict,
    standard: dict | None = None,
) -> dict:
    standard_number = result.get("standardNumber")

    if not standard_number:
        return result

    if standard is None:
        standard = get_standard(standard_number)

    if not standard:
        return result

    return {
        "standardNumber": standard.get("standardNumber"),
        "title": standard.get("title"),
        "score": result.get("score"),
        "rankingScore": result.get("rankingScore"),
        "relevanceScore": result.get("relevanceScore"),
        "confidence": result.get("confidence"),
        "matchedChunks": result.get("matchedChunks", 0),
        "bestChunk": result.get("bestChunk", ""),
        "page": result.get("page"),
        "chunkIndex": result.get("chunkIndex"),
        "matchedChunkData": result.get(
            "matchedChunkData", []
        ),
        "scope": standard.get("scope"),
        "category": standard.get("category"),
        "applicableDomains": standard.get(
            "applicableDomains", []
        ),
        "productDetails": standard.get(
            "productDetails", {}
        ),
        "keywords": standard.get("keywords", []),
        "technicalRequirements": standard.get(
            "technicalRequirements", {}
        ),
        "testingAndInspection": standard.get(
            "testingAndInspection", {}
        ),
        "alliedStandards": standard.get(
            "alliedStandards", []
        ),
        "standardRelationships": standard.get(
            "standardRelationships", []
        ),
        "currentEdition": standard.get(
            "currentEdition"
        ),
        "amendments": standard.get("amendments", []),
        "compliance": standard.get("compliance", {}),
        "procurementRelevance": standard.get(
            "procurementRelevance", {}
        ),
        "language": standard.get("language", "en"),
        "multilingualTerms": standard.get(
            "multilingualTerms", []
        ),
        "source": standard.get("source", {}),
        "statusSummary": _build_status_summary(
            standard
        ),
    }


def enrich_recommendations(
    results: list[dict],
) -> list[dict]:
    if not results:
        return []

    standard_numbers = [
        result.get("standardNumber")
        for result in results
        if result.get("standardNumber")
    ]

    with ThreadPoolExecutor(
        max_workers=min(5, len(standard_numbers))
    ) as executor:
        standards = list(
            executor.map(
                get_standard,
                standard_numbers,
            )
        )

    standard_map = {
        standard.get("standardNumber"): standard
        for standard in standards
        if standard
    }

    return [
        enrich_recommendation(
            result,
            standard_map.get(
                result.get("standardNumber")
            ),
        )
        for result in results
    ]