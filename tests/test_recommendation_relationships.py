from unittest.mock import patch

from app.rag.recommendation import _expand_relationships


def test_expands_allied_standards():
    recommendations = [
        {
            "standardNumber": "IS 3370 (Part 2):2021",
            "title": "Concrete Structures",
            "score": 0.9,
        }
    ]

    standard = {
        "standardNumber": "IS 3370 (Part 2):2021",
        "alliedStandards": [
            {
                "standardNumber": "IS 456:2000",
                "relationshipType": "Referenced Standard",
                "title": "Plain and Reinforced Concrete",
                "description": "General concrete provisions.",
            }
        ],
        "standardRelationships": [],
    }

    with patch(
        "app.rag.recommendation.get_standard",
        return_value=standard,
    ):
        result = _expand_relationships(
            recommendations
        )

    related = result[0]["relatedStandards"]

    assert len(related) == 1
    assert related[0]["standardNumber"] == "IS 456:2000"
    assert (
        related[0]["relationshipType"]
        == "Referenced Standard"
    )


def test_expands_standard_relationships():
    recommendations = [
        {
            "standardNumber": "IS 3370 (Part 1):2021",
            "score": 0.8,
        }
    ]

    standard = {
        "standardNumber": "IS 3370 (Part 1):2021",
        "alliedStandards": [],
        "standardRelationships": [
            {
                "relatedStandardNumber": "IS 3370 (Part 2):2021",
                "relationshipType": "Related Part",
                "description": "Related liquid-retaining standard.",
            }
        ],
    }

    with patch(
        "app.rag.recommendation.get_standard",
        return_value=standard,
    ):
        result = _expand_relationships(
            recommendations
        )

    related = result[0]["relatedStandards"]

    assert len(related) == 1
    assert (
        related[0]["standardNumber"]
        == "IS 3370 (Part 2):2021"
    )


def test_does_not_duplicate_related_standard():
    recommendations = [
        {
            "standardNumber": "IS 3370 (Part 2):2021",
            "score": 0.9,
        }
    ]

    standard = {
        "standardNumber": "IS 3370 (Part 2):2021",
        "alliedStandards": [
            {
                "standardNumber": "IS 456:2000",
                "relationshipType": "Referenced Standard",
            }
        ],
        "standardRelationships": [
            {
                "relatedStandardNumber": "IS 456:2000",
                "relationshipType": "Related Standard",
            }
        ],
    }

    with patch(
        "app.rag.recommendation.get_standard",
        return_value=standard,
    ):
        result = _expand_relationships(
            recommendations
        )

    related = result[0]["relatedStandards"]

    assert len(related) == 1
    assert related[0]["standardNumber"] == "IS 456:2000"