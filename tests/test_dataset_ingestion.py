from pathlib import Path

from app.ingestion.pipeline import ingest_dataset_pdf


def test_ingest_dataset_pdf(monkeypatch):
    inserted = []

    def fake_upsert(standard):
        inserted.append(standard)
        return "test-id"

    monkeypatch.setattr(
        "app.ingestion.pipeline.upsert_standard",
        fake_upsert,
    )

    pdf_path = Path("data/raw/10set.pdf")

    result = ingest_dataset_pdf(str(pdf_path))

    assert result["total"] == 10
    assert result["inserted"] == 10
    assert len(inserted) == 10