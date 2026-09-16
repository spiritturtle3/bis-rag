from app.rag.ranker import rank_standards


def test_rank_standards_groups_chunks():
    results = [
        {
            "standardNumber": "IS 458:2021",
            "hybridScore": 0.90,
            "text": "pipe requirements",
        },
        {
            "standardNumber": "IS 458:2021",
            "hybridScore": 0.85,
            "text": "pipe testing",
        },
        {
            "standardNumber": "IS 17725:2022",
            "hybridScore": 0.88,
            "text": "manhole requirements",
        },
    ]

    ranked = rank_standards(
        "precast concrete pipes",
        results,
    )

    assert len(ranked) == 2
    assert ranked[0]["standardNumber"] == "IS 458:2021"
    assert ranked[0]["score"] == 0.90
    assert ranked[0]["matchedChunks"] == 2
    assert ranked[1]["standardNumber"] == "IS 17725:2022"


def test_rank_standards_prefers_relevant_standard():
    results = [
        {
            "standardNumber": "IS 5820:2024",
            "hybridScore": 0.020,
            "text": "Precast concrete cable covers",
        },
        {
            "standardNumber": "IS 458:2021",
            "hybridScore": 0.018,
            "text": "Precast concrete pipes for drainage",
        },
    ]

    ranked = rank_standards(
        "precast concrete pipes for drainage systems",
        results,
        limit=2,
    )

    assert ranked[0]["standardNumber"] == "IS 458:2021"


def test_rank_standards_respects_limit():
    results = [
        {
            "standardNumber": "IS 1:2020",
            "score": 0.90,
            "text": "result",
        },
        {
            "standardNumber": "IS 2:2020",
            "score": 0.80,
            "text": "result",
        },
        {
            "standardNumber": "IS 3:2020",
            "score": 0.70,
            "text": "result",
        },
    ]

    ranked = rank_standards(
        "test query",
        results,
        limit=2,
    )

    assert len(ranked) == 2


def test_rank_standards_ignores_missing_standard_number():
    results = [
        {
            "score": 0.95,
            "text": "invalid result",
        },
        {
            "standardNumber": "IS 458:2021",
            "score": 0.90,
            "text": "pipe requirements",
        },
    ]

    ranked = rank_standards(
        "concrete pipes",
        results,
    )

    assert len(ranked) == 1
    assert ranked[0]["standardNumber"] == "IS 458:2021"