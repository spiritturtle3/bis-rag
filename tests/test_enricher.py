from app.rag.enricher import enrich_recommendation


def test_enrich_recommendation(monkeypatch):
    fake_standard = {
        "standardNumber": "IS 458:2021",
        "title": "Precast Concrete Pipes",
        "scope": "Specification for concrete pipes.",
        "category": "Concrete Products",
        "applicableDomains": ["Drainage"],
        "productDetails": {"productType": "Concrete Pipes"},
        "keywords": ["concrete pipes"],
        "technicalRequirements": {},
        "testingAndInspection": {},
        "alliedStandards": [],
        "currentEdition": {"year": 2021},
        "amendments": [],
        "compliance": {},
        "procurementRelevance": {},
        "standardRelationships": [],
        "language": "English",
        "multilingualTerms": [],
        "source": {},
    }

    monkeypatch.setattr(
        "app.rag.enricher.get_standard",
        lambda standard_number: fake_standard,
    )

    result = enrich_recommendation(
        {
            "standardNumber": "IS 458:2021",
            "score": 0.95,
            "matchedChunks": 3,
        }
    )

    assert result["standardNumber"] == "IS 458:2021"
    assert result["title"] == "Precast Concrete Pipes"
    assert result["score"] == 0.95
    assert result["matchedChunks"] == 3
    assert result["scope"] == "Specification for concrete pipes."


def test_enrich_missing_standard(monkeypatch):
    monkeypatch.setattr(
        "app.rag.enricher.get_standard",
        lambda standard_number: None,
    )

    result = {
        "standardNumber": "UNKNOWN",
        "score": 0.5,
    }

    assert enrich_recommendation(result) == result