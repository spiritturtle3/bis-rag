from app.database.models import BISStandard
from app.ingestion.validator import (
    get_completeness_warnings,
    validate_standard,
    validate_standards,
)


def make_standard(**overrides):
    data = {
        "standardNumber": "IS TEST:2026",
        "title": "Test Standard",
        "issuingOrganization": "Bureau of Indian Standards",
        "scope": "Test scope",
    }

    data.update(overrides)

    return BISStandard(**data)


def test_valid_standard():
    standard = make_standard()

    errors = validate_standard(standard)

    assert errors == []


def test_missing_title():
    standard = make_standard(title="")

    errors = validate_standard(standard)

    assert "Missing required field: title" in errors


def test_empty_scope_is_warning():
    standard = make_standard(scope="")

    errors = validate_standard(standard)

    assert errors == []

    warnings = get_completeness_warnings(standard)

    assert "scope is empty" in warnings


def test_validate_standards():
    standards = [
        make_standard(),
        make_standard(
            standardNumber="IS TEST 2:2026",
            title="Another Standard",
        ),
    ]

    result = validate_standards(standards)

    assert result["total"] == 2
    assert result["validCount"] == 2
    assert result["invalidCount"] == 0