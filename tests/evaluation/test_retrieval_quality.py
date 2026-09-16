from app.rag.hybrid_search import hybrid_search


EVALUATION_QUERIES = [
    {
        "query": "precast concrete pipes",
        "expected_standard": "IS 458:2021",
    },
    {
        "query": "reinforced concrete water tank",
        "expected_standard": "IS 3370 (Part 2):2021",
    },
    {
        "query": "common burnt clay building bricks",
        "expected_standard": "IS 1077:2025",
    },
    {
        "query": "precast concrete circular manhole",
        "expected_standard": "IS 17725:2022",
    },
    {
        "query": "glazed stoneware pipes laying",
        "expected_standard": "IS 4127:2023",
    },
    {
        "query": "autoclaved reinforced cellular concrete wall slabs",
        "expected_standard": "IS 6072:2023",
    },
    {
        "query": "precast concrete cable covers",
        "expected_standard": "IS 5820:2024",
    },
    {
        "query": "gypsum plaster boards and ceiling tiles",
        "expected_standard": "IS 2095 (Part 3):2022",
    },
    {
        "query": "doors windows and sliders performance requirements",
        "expected_standard": "IS 18648:2024",
    },
    {
        "query": "glass fibre reinforced gypsum panels building construction",
        "expected_standard": "IS 17401:2021",
    },
    {
        "query": "earthquake resistant industrial structures",
        "expected_standard": "IS 1893 (Part 4):2024",
    },
    {
        "query": "subsurface investigation for foundations",
        "expected_standard": "IS 1892:2021",
    },
    {
        "query": "stabilized soil blocks for building construction",
        "expected_standard": "IS 1725:2023",
    },
    {
        "query": "measurement of concrete works",
        "expected_standard": "IS 1200 (Part 2):2025",
    },
    {
        "query": "biogas biomethane plant design construction",
        "expected_standard": "IS 9478:2023",
    },
    {
        "query": "measurement of refractory work",
        "expected_standard": "IS 1200 (Part 6):2024",
    },
    {
        "query": "prestressed concrete seven wire strand",
        "expected_standard": "IS 14268:2022",
    },
    {
        "query": "planning and design of ports and harbours",
        "expected_standard": "IS 4651 (Part 4):2023",
    },
    {
        "query": "steel pipes for water supply",
        "expected_standard": "TEST-001",
    },
    {
        "query": "पानी की टंकी के लिए प्रबलित कंक्रीट",
        "expected_standard": "IS 3370 (Part 2):2021",
    },
]


def evaluate_retrieval():
    hit_at_1 = 0
    hit_at_3 = 0
    hit_at_5 = 0

    failures = []

    for item in EVALUATION_QUERIES:
        results = hybrid_search(
            item["query"],
            limit=5,
        )

        standards = [
            result["standardNumber"]
            for result in results
        ]

        expected = item["expected_standard"]

        if (
            len(standards) >= 1
            and standards[0] == expected
        ):
            hit_at_1 += 1

        if expected in standards[:3]:
            hit_at_3 += 1

        if expected in standards[:5]:
            hit_at_5 += 1

        if expected not in standards[:5]:
            failures.append(
                {
                    "query": item["query"],
                    "expected": expected,
                    "results": standards,
                }
            )

    total = len(EVALUATION_QUERIES)

    return {
        "Hit@1": hit_at_1 / total,
        "Hit@3": hit_at_3 / total,
        "Hit@5": hit_at_5 / total,
        "failures": failures,
    }


def test_retrieval_quality():
    metrics = evaluate_retrieval()

    print(
        f"\nHit@1: "
        f"{metrics['Hit@1']:.2%}"
    )

    print(
        f"Hit@3: "
        f"{metrics['Hit@3']:.2%}"
    )

    print(
        f"Hit@5: "
        f"{metrics['Hit@5']:.2%}"
    )

    if metrics["failures"]:
        print("\nFAILED QUERIES:")

        for failure in metrics["failures"]:
            print(
                f"\nQuery: {failure['query']}"
            )
            print(
                f"Expected: "
                f"{failure['expected']}"
            )
            print(
                f"Retrieved: "
                f"{failure['results']}"
            )

    # Baseline expectation.
    # We will improve this after seeing the actual results.
    assert metrics["Hit@3"] >= 0.66