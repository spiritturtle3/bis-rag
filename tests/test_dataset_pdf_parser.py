from pathlib import Path

from app.ingestion.dataset_pdf_parser import parse_dataset_pdf


def test_parse_dataset_pdf():
    pdf_path = Path("data/raw/10set.pdf")

    standards = parse_dataset_pdf(str(pdf_path))

    assert len(standards) == 10

    standard_numbers = {
        standard.standardNumber
        for standard in standards
    }

    assert "IS 3370 (Part 1):2021" in standard_numbers
    assert "IS 3370 (Part 2):2021" in standard_numbers
    assert "IS 458:2021" in standard_numbers