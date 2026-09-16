from app.ingestion.universal_normalizer import (
    normalize_dataset,
    normalize_standard_record,
)

def test_normalizes_string_fields():
    record = {
        "standard_number": "IS 1234 ( Part 1 ) : 2025",
        "name": "Example Standard",
        "issuer": "BIS",
        "scope": "Example scope",
        "language": "English",
        "keywords": "pipes",
    }

    result = normalize_standard_record(record)

    assert result.standardNumber == "IS 1234 (Part 1) : 2025"
    assert result.issuingOrganization == "Bureau of Indian Standards"
    assert result.language == "en"
    assert result.keywords == ["pipes"]

def test_normalizes_allied_strings():
    record = {
        "standardNumber": "IS 1234:2025",
        "title": "Example Standard",
        "scope": "Example scope",
        "alliedStandards": ["IS 456:2000"],
    }

    result = normalize_standard_record(record)

    assert len(result.alliedStandards) == 1
    assert result.alliedStandards[0].standardNumber == "IS 456:2000"

def test_normalizes_dataset_and_removes_duplicates():
    records = [
        {
            "standardNumber": "IS 1234:2025",
            "title": "Example Standard",
            "scope": "Example scope",
        },
        {
            "standardNumber": "IS 1234:2025",
            "title": "Duplicate Standard",
            "scope": "Duplicate scope",
        },
    ]

    valid_records, errors = normalize_dataset(records)

    assert len(valid_records) == 1
    assert errors == []