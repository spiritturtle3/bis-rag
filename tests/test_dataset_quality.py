from app.ingestion.dataset_quality import (
    calculate_dataset_quality,
    calculate_standard_quality,
)


def test_high_quality_standard():
    standard = type(
        "Standard",
        (),
        {
            "standardNumber": "IS 1234:2025",
            "scope": "Specification for concrete pipes.",
            "productDetails": {
                "productDescription": "Concrete pipe",
                "intendedUses": ["Drainage"],
            },
            "keywords": ["concrete", "pipe"],
            "technicalRequirements": {
                "keyRequirements": ["Strength requirement"]
            },
            "testingAndInspection": {
                "testMethods": ["Compression test"]
            },
            "alliedStandards": [
                {"standardNumber": "IS 456:2000"}
            ],
            "compliance": {
                "certificationRequired": True
            },
            "procurementRelevance": {
                "specificationPoints": ["Diameter"]
            },
        },
    )()

    result = calculate_standard_quality(standard)

    assert result["quality"] == "high"
    assert result["score"] >= 0.75


def test_placeholder_content_is_not_meaningful():
    standard = type(
        "Standard",
        (),
        {
            "standardNumber": "IS 1234:2025",
            "scope": "Example scope.",
            "productDetails": {},
            "keywords": [],
            "technicalRequirements": {
                "keyRequirements": [
                    "Requirements specified in the standard"
                ]
            },
            "testingAndInspection": {
                "testMethods": [
                    "As specified by the standard"
                ]
            },
            "alliedStandards": [],
            "compliance": {
                "notes": "Verify current applicability"
            },
            "procurementRelevance": {},
        },
    )()

    result = calculate_standard_quality(standard)

    assert result["checks"]["technicalRequirements"] is False
    assert result["checks"]["testingAndInspection"] is False
    assert result["checks"]["compliance"] is False


def test_empty_dataset():
    result = calculate_dataset_quality([])

    assert result["standards"] == 0
    assert result["score"] == 0.0
    assert result["quality"] == "low"