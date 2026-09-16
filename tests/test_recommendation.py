from app.rag.recommendation import recommend_standards


def test_recommend_standards(monkeypatch):

    def fake_hybrid_search(query, limit):
        assert query == "precast concrete pipes"
        assert limit == 15

        return [
            {
                "standardNumber": "IS 458:2021",
                "hybridScore": 0.80,
                "text": "Precast concrete pipes",
            },
            {
                "standardNumber": "IS 458:2021",
                "hybridScore": 0.75,
                "text": "Concrete pipe requirements",
            },
            {
                "standardNumber": "IS 17725:2022",
                "hybridScore": 0.65,
                "text": "Precast concrete circular manhole",
            },
        ]

    def fake_enrich_recommendations(results):
        return results

    monkeypatch.setattr(
        "app.rag.recommendation.hybrid_search",
        fake_hybrid_search,
    )

    monkeypatch.setattr(
        "app.rag.recommendation.enrich_recommendations",
        fake_enrich_recommendations,
    )

    results = recommend_standards(
        "precast concrete pipes",
        limit=5,
    )

    assert len(results) == 2
    assert results[0]["standardNumber"] == "IS 458:2021"
    assert results[1]["standardNumber"] == "IS 17725:2022"


def test_recommend_standards_returns_empty_for_no_results(
    monkeypatch,
):

    def fake_hybrid_search(query, limit):
        return []

    monkeypatch.setattr(
        "app.rag.recommendation.hybrid_search",
        fake_hybrid_search,
    )

    results = recommend_standards(
        "unknown product",
        limit=5,
    )

    assert results == []


def test_recommend_standards_rejects_weak_results(
    monkeypatch,
):

    def fake_hybrid_search(query, limit):
        return [
            {
                "standardNumber": "IS 458:2021",
                "hybridScore": 0.01,
                "text": "Completely unrelated content",
            },
        ]

    monkeypatch.setattr(
        "app.rag.recommendation.hybrid_search",
        fake_hybrid_search,
    )

    results = recommend_standards(
        "medical imaging equipment",
        limit=5,
    )

    assert results == []