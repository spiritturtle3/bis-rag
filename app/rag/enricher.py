from app.database.standard_repository import get_standard


def _build_status_summary(standard: dict) -> dict:
    """
    Build a concise procurement-focused status summary.
    """

    edition = standard.get("currentEdition") or {}
    amendments = standard.get("amendments") or []
    compliance = standard.get("compliance") or {}
    procurement = standard.get("procurementRelevance") or {}

    latest_amendment = None

    if amendments:
        latest_amendment = amendments[-1]

    return {
        "currentEdition": {
            "edition": edition.get("edition"),
            "year": edition.get("year"),
            "publishedDate": edition.get(
                "publishedDate"
            ),
            "status": edition.get("status"),
        },
        "latestAmendment": latest_amendment,
        "certification": {
            "required": compliance.get(
                "certificationRequired"
            ),
            "scheme": compliance.get(
                "certificationScheme"
            ),
            "mandatory": compliance.get(
                "mandatory"
            ),
            "crsApplicable": compliance.get(
                "crsApplicability"
            ),
            "hallmarkingApplicable": compliance.get(
                "hallmarkingApplicability"
            ),
        },
        "procurement": {
            "applicable": procurement.get(
                "applicableToProcurement"
            ),
            "recommendedFor": procurement.get(
                "recommendedFor",
                [],
            ),
            "specificationPoints": procurement.get(
                "specificationPoints",
                [],
            ),
            "buyerConsiderations": procurement.get(
                "buyerConsiderations",
                [],
            ),
        },
    }


def enrich_recommendation(result: dict) -> dict:
    """
    Add full BIS standard metadata to a ranked recommendation
    while preserving ranking and retrieval evidence.
    """

    standard_number = result.get(
        "standardNumber"
    )

    if not standard_number:
        return result

    standard = get_standard(
        standard_number
    )

    if not standard:
        return result

    enriched = {
        "standardNumber": standard.get(
            "standardNumber"
        ),
        "title": standard.get("title"),

        # Ranking information
        "score": result.get("score"),
        "rankingScore": result.get(
            "rankingScore"
        ),
        "relevanceScore": result.get(
            "relevanceScore"
        ),
        "confidence": result.get(
            "confidence"
        ),
        "matchedChunks": result.get(
            "matchedChunks",
            0,
        ),

        # Retrieved evidence
        "bestChunk": result.get(
            "bestChunk",
            "",
        ),
        "page": result.get("page"),
        "chunkIndex": result.get(
            "chunkIndex"
        ),
        "matchedChunkData": result.get(
            "matchedChunkData",
            [],
        ),

        # Core applicability
        "scope": standard.get("scope"),
        "category": standard.get("category"),
        "applicableDomains": standard.get(
            "applicableDomains",
            [],
        ),
        "productDetails": standard.get(
            "productDetails",
            {},
        ),
        "keywords": standard.get(
            "keywords",
            [],
        ),

        # Technical information
        "technicalRequirements": standard.get(
            "technicalRequirements",
            {},
        ),
        "testingAndInspection": standard.get(
            "testingAndInspection",
            {},
        ),

        # Relationships
        "alliedStandards": standard.get(
            "alliedStandards",
            [],
        ),
        "standardRelationships": standard.get(
            "standardRelationships",
            [],
        ),

        # Version and compliance
        "currentEdition": standard.get(
            "currentEdition"
        ),
        "amendments": standard.get(
            "amendments",
            [],
        ),
        "compliance": standard.get(
            "compliance",
            {},
        ),

        # Procurement
        "procurementRelevance": standard.get(
            "procurementRelevance",
            {},
        ),

        # Language/source
        "language": standard.get(
            "language",
            "en",
        ),
        "multilingualTerms": standard.get(
            "multilingualTerms",
            [],
        ),
        "source": standard.get(
            "source",
            {},
        ),

        # Concise procurement summary
        "statusSummary": _build_status_summary(
            standard
        ),
    }

    return enriched


def enrich_recommendations(
    results: list[dict],
) -> list[dict]:
    """
    Enrich all ranked recommendations with MongoDB metadata.
    """

    return [
        enrich_recommendation(result)
        for result in results
    ]
