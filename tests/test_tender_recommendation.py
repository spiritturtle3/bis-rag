from pathlib import Path

import fitz

from app.rag.tender_recommendation import recommend_from_tender


def create_tender_pdf(path: Path):
    document = fitz.open()
    page = document.new_page()

    page.insert_text(
        (72, 72),
        """
        Procurement of reinforced concrete water tanks.
        Minimum capacity 50000 litres.
        Concrete grade M30.
        Suitable for potable water.
        BIS certification required.
        """
    )

    document.save(path)
    document.close()


def test_query_only():
    result = recommend_from_tender(
        query="precast concrete pipes",
        limit=5,
    )

    assert result["query"]
    assert result["recommendations"]
    assert result["recommendations"][0]["standardNumber"] == "IS 458:2021"


def test_tender_pdf(tmp_path):
    pdf_path = tmp_path / "tender.pdf"
    create_tender_pdf(pdf_path)

    result = recommend_from_tender(
        pdf_path=pdf_path,
        limit=5,
    )

    assert result["tenderRequirements"]
    assert result["tenderRequirements"]["product"] == (
        "reinforced concrete water tanks"
    )
    assert "M30" in result["tenderRequirements"]["grades"]

    assert result["recommendations"]
    assert (
        result["recommendations"][0]["standardNumber"]
        == "IS 3370 (Part 2):2021"
    )


def test_query_and_tender(tmp_path):
    pdf_path = tmp_path / "tender.pdf"
    create_tender_pdf(pdf_path)

    result = recommend_from_tender(
        query="water storage structure",
        pdf_path=pdf_path,
        limit=5,
    )

    assert "water storage structure" in result["query"]
    assert result["recommendations"]


def test_no_input():
    result = recommend_from_tender()

    assert result["recommendations"] == []
    assert "Provide a query" in result["message"]