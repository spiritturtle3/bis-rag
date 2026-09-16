from app.database.standard_repository import (
    insert_standard,
    get_standard,
    upsert_standard,
)


def test_standard_repository():
    standard = {
        "standardNumber": "TEST-STD-001",
        "title": "Synthetic Test Standard",
        "category": "Product Standard",
        "language": "en",
    }

    upsert_standard(standard)

    result = get_standard("TEST-STD-001")

    assert result is not None
    assert result["standardNumber"] == "TEST-STD-001"
    assert result["title"] == "Synthetic Test Standard"