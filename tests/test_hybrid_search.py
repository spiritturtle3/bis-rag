from app.rag.hybrid_search import hybrid_search


def test_hybrid_search():
    results = hybrid_search(
        "steel pipes for water supply",
        limit=3
    )

    assert len(results) > 0
    assert "text" in results[0]
    assert "hybridScore" in results[0]