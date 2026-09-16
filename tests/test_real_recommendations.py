import pytest

from app.rag.recommendation import recommend_standards


@pytest.mark.parametrize(
    "query, expected_standard",
    [
        (
            "precast concrete pipes",
            "IS 458:2021",
        ),
        (
            "reinforced concrete water tank",
            "IS 3370 (Part 2):2021",
        ),
        (
            "पानी की टंकी के लिए प्रबलित कंक्रीट",
            "IS 3370 (Part 2):2021",
        ),
    ],
)
def test_supported_queries(query, expected_standard):
    results = recommend_standards(query, limit=5)

    assert results, f"No recommendations returned for: {query}"

    standard_numbers = [
        result["standardNumber"]
        for result in results
    ]

    assert (
        expected_standard in standard_numbers
    ), (
        f"Expected {expected_standard} for '{query}', "
        f"got {standard_numbers}"
    )


def test_unsupported_product_is_rejected():
    results = recommend_standards(
        "laptop computer with 16 GB RAM",
        limit=5,
    )

    assert results == []