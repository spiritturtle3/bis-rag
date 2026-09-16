from pathlib import Path

from app.ingestion.pdf_extractor import extract_pdf


def test_extract_pdf():
    pdf_path = Path("data/test/sample.pdf")

    pages = extract_pdf(str(pdf_path))

    assert len(pages) > 0
    assert pages[0]["page"] == 1
    assert pages[0]["text"] != ""