from app.rag.evidence import (
    build_evidence,
    build_evidence_for_recommendations,
)


def test_build_evidence():
    recommendation = {
        "standardNumber": "IS 3370 (Part 2):2021",
        "title": "Concrete Structures for Retaining Aqueous Liquids",
        "confidence": 0.91,
        "scope": (
            "This standard specifies requirements for the design "
            "and construction of reinforced concrete structures."
        ),
        "productDetails": {
            "intendedUses": ["Water tanks", "Reservoirs"],
            "applications": ["Water supply"],
            "synonyms": ["Reinforced concrete water tank"],
        },
        "technicalRequirements": {
            "keyRequirements": ["Structural design", "Durability"],
            "performanceRequirements": ["Structural strength"],
            "designRequirements": ["Crack control"],
        },
        "procurementRelevance": {
            "specificationPoints": ["Concrete", "Reinforcement"],
            "buyerConsiderations": ["Current edition"],
        },
        "currentEdition": {
            "edition": "Second Revision",
            "year": 2021,
        },
        "amendments": [
            {
                "amendmentNumber": "1",
                "date": "2024",
            }
        ],
        "compliance": {
            "certificationRequired": False,
        },
        "matchedChunks": 4,
        "source": {
            "sourceName": "Bureau of Indian Standards",
        },
    }

    result = build_evidence(recommendation)

    assert result["standardNumber"] == "IS 3370 (Part 2):2021"
    assert result["confidence"] == 0.91
    assert result["scope"]
    assert "Water tanks" in result["evidencePoints"]
    assert "Structural design" in result["evidencePoints"]
    assert result["currentEdition"]["year"] == 2021
    assert result["amendments"]
    assert result["source"]["sourceName"] == "Bureau of Indian Standards"


def test_missing_optional_fields_do_not_fail():
    recommendation = {
        "standardNumber": "IS 1234:2025",
        "title": "Example Standard",
    }

    result = build_evidence(recommendation)

    assert result["standardNumber"] == "IS 1234:2025"
    assert result["evidencePoints"] == []
    assert result["scope"] == ""
    assert result["evidence"] == []


def test_build_evidence_from_retrieved_chunk():
    recommendation = {
        "standardNumber": "IS 3370 (Part 2):2021",
        "title": "Concrete Structures",
        "source": {
            "sourceType": "BIS",
            "sourceName": "Bureau of Indian Standards",
        },
        "page": 3,
        "chunkIndex": 2,
        "bestChunk": (
            "Scope: This standard specifies requirements "
            "for concrete structures retaining aqueous liquids.\n\n"
            "Technical Requirements:\n"
            "Concrete requirements and crack control."
        ),
    }

    result = build_evidence(recommendation)

    assert len(result["evidence"]) == 1

    evidence = result["evidence"][0]

    assert evidence["standardNumber"] == "IS 3370 (Part 2):2021"
    assert evidence["page"] == 3
    assert evidence["chunkIndex"] == 2
    assert "Scope:" in evidence["excerpt"]
    assert "aqueous liquids" in evidence["excerpt"]


def test_evidence_excerpt_prefers_meaningful_section():
    recommendation = {
        "standardNumber": "IS 3370 (Part 2):2021",
        "source": {
            "sourceName": "Bureau of Indian Standards",
        },
        "bestChunk": (
            "equired: True\n"
            "Related Test Standards: IS 456:2000\n\n"
            "Scope: This standard specifies requirements "
            "for liquid-retaining structures.\n\n"
            "Technical Requirements:\n"
            "Reinforced concrete and durability."
        ),
        "page": None,
        "chunkIndex": 2,
    }

    result = build_evidence(recommendation)

    excerpt = result["evidence"][0]["excerpt"]

    assert not excerpt.startswith("equired:")
    assert "Scope:" in excerpt


def test_build_evidence_for_multiple_recommendations():
    recommendations = [
        {
            "standardNumber": "IS 458:2021",
            "title": "Precast Concrete Pipes",
        },
        {
            "standardNumber": "IS 3370 (Part 2):2021",
            "title": "Concrete Structures",
        },
    ]

    results = build_evidence_for_recommendations(recommendations)

    assert len(results) == 2
    assert results[0]["standardNumber"] == "IS 458:2021"
    assert results[1]["standardNumber"] == "IS 3370 (Part 2):2021"
