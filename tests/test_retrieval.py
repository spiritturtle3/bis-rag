from app.rag.retrieval import vector_search


def test_vector_search():
    results = vector_search(
        "precast concrete pipes for drainage systems",
        limit=3,
    )

    assert len(results) > 0
    assert "text" in results[0]
    assert "score" in results[0]
    assert "standardNumber" in results[0]


def test_vector_search_returns_relevant_standard():
    results = vector_search(
        "precast concrete pipes for drainage systems",
        limit=5,
    )

    standard_numbers = [
        result["standardNumber"]
        for result in results
    ]

    assert "IS 458:2021" in standard_numbers