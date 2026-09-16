from app.database.models import BISStandard
from app.ingestion.standard_to_text import standard_to_text


def test_standard_to_text():
    standard = BISStandard(
        standardNumber="IS TEST:2026",
        title="Test Concrete Standard",
        issuingOrganization="Bureau of Indian Standards",
        scope="Concrete products for construction.",
        keywords=["concrete", "construction"],
    )

    text = standard_to_text(standard)

    assert "IS TEST:2026" in text
    assert "Test Concrete Standard" in text
    assert "Concrete products for construction." in text
    assert "concrete, construction" in text


def test_standard_to_text_includes_technical_requirements():
    standard = BISStandard(
        standardNumber="IS TEST:2026",
        title="Test Standard",
        issuingOrganization="Bureau of Indian Standards",
        scope="Test scope.",
        technicalRequirements={
            "keyRequirements": [
                "Minimum strength requirement"
            ],
            "materials": ["Concrete"],
            "grades": ["M30"],
        },
    )

    text = standard_to_text(standard)

    assert "Minimum strength requirement" in text
    assert "Concrete" in text
    assert "M30" in text


def test_standard_to_text_includes_allied_standards():
    standard = BISStandard(
        standardNumber="IS TEST:2026",
        title="Test Standard",
        issuingOrganization="Bureau of Indian Standards",
        scope="Test scope.",
        alliedStandards=[
            {
                "standardNumber": "IS 456:2000",
                "relationshipType": "normative reference",
                "title": "Plain and Reinforced Concrete",
            }
        ],
    )

    text = standard_to_text(standard)

    assert "IS 456:2000" in text
    assert "normative reference" in text
    assert "Plain and Reinforced Concrete" in text