from app.database.models import BISStandard
from app.ingestion.standard_chunker import chunk_standard


def test_chunk_standard():
    standard = BISStandard(
        standardNumber="IS TEST:2026",
        title="Test Standard",
        issuingOrganization="Bureau of Indian Standards",
        scope="Test scope.",
        keywords=["concrete", "construction"],
    )

    chunks = chunk_standard(
        standard,
        chunk_size=100,
        overlap=20,
    )

    assert len(chunks) > 0
    assert chunks[0]["standardNumber"] == "IS TEST:2026"
    assert chunks[0]["chunkIndex"] == 0
    assert "IS TEST:2026" in chunks[0]["text"]


def test_chunk_standard_indexes_are_sequential():
    standard = BISStandard(
        standardNumber="IS TEST:2026",
        title="Test Standard",
        issuingOrganization="Bureau of Indian Standards",
        scope="A " * 500,
    )

    chunks = chunk_standard(
        standard,
        chunk_size=100,
        overlap=20,
    )

    indexes = [chunk["chunkIndex"] for chunk in chunks]

    assert indexes == list(range(len(chunks)))


def test_empty_optional_fields_do_not_break_chunking():
    standard = BISStandard(
        standardNumber="IS TEST:2026",
        title="Test Standard",
        issuingOrganization="Bureau of Indian Standards",
        scope="",
    )

    chunks = chunk_standard(standard)

    assert len(chunks) > 0
    assert "IS TEST:2026" in chunks[0]["text"]