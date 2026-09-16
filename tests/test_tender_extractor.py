from pathlib import Path

import fitz
import pytest

from app.rag.tender_extractor import extract_tender_text


def create_test_pdf(path: Path):
    document = fitz.open()
    page = document.new_page()
    page.insert_text(
        (72, 72),
        "Tender for procurement of reinforced concrete water tanks."
    )
    document.save(path)
    document.close()


def test_extract_tender_text(tmp_path):
    pdf_path = tmp_path / "tender.pdf"
    create_test_pdf(pdf_path)

    text = extract_tender_text(pdf_path)

    assert "reinforced concrete water tanks" in text


def test_missing_pdf_raises_error(tmp_path):
    pdf_path = tmp_path / "missing.pdf"

    with pytest.raises(FileNotFoundError):
        extract_tender_text(pdf_path)


def test_non_pdf_raises_error(tmp_path):
    file_path = tmp_path / "tender.txt"
    file_path.write_text("test")

    with pytest.raises(ValueError):
        extract_tender_text(file_path)


def test_empty_pdf_raises_error(tmp_path):
    pdf_path = tmp_path / "empty.pdf"

    document = fitz.open()
    document.new_page()
    document.save(pdf_path)
    document.close()

    with pytest.raises(ValueError):
        extract_tender_text(pdf_path)