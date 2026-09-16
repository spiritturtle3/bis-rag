from app.rag.confidence import (
    STRONG_MATCH_THRESHOLD,
    WEAK_MATCH_THRESHOLD,
    add_confidence_scores,
    build_fallback_response,
    calculate_confidence,
    filter_by_confidence,
    has_reliable_match,
)


def test_calculate_confidence_returns_valid_range():
    result = {
        "score": 0.8,
        "rankingScore": 1.2,
        "matchedChunks": 3,
    }

    confidence = calculate_confidence(result)

    assert 0.0 <= confidence <= 1.0


def test_strong_result_has_high_confidence():
    result = {
        "score": 0.9,
        "rankingScore": 1.8,
        "matchedChunks": 3,
    }

    confidence = calculate_confidence(result)

    assert confidence >= STRONG_MATCH_THRESHOLD


def test_weak_result_can_be_filtered():
    results = [
        {
            "score": 0.05,
            "rankingScore": 0.10,
            "matchedChunks": 1,
        },
        {
            "score": 0.04,
            "rankingScore": 0.08,
            "matchedChunks": 1,
        },
    ]

    scored = add_confidence_scores(results)

    filtered = filter_by_confidence(
        scored,
        threshold=0.60,
    )

    assert filtered == []


def test_reliable_match_detection():
    result = {
        "score": 0.9,
        "rankingScore": 1.8,
        "matchedChunks": 3,
    }

    scored = add_confidence_scores([result])

    assert has_reliable_match(scored) is True


def test_unreliable_match_detection():
    result = {
        "score": 0.05,
        "rankingScore": 0.10,
        "matchedChunks": 1,
    }

    scored = add_confidence_scores([result])

    assert has_reliable_match(scored) is False


def test_fallback_response():
    response = build_fallback_response("laptop computer")

    assert response["query"] == "laptop computer"
    assert response["recommendations"] == []
    assert response["fallback"] is True
    assert "No reliable" in response["message"]