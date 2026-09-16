from app.rag.tender_requirements import (
    build_requirement_query,
    extract_tender_requirements,
)


def test_extract_tender_requirements():
    text = """
    Procurement of reinforced concrete water tanks.
    Minimum capacity 50000 litres.
    Concrete grade M30.
    Suitable for potable water.
    BIS certification required.
    Compressive strength testing shall be carried out.
    """

    result = extract_tender_requirements(text)

    assert result["product"] == "reinforced concrete water tanks"
    assert "reinforced concrete" in result["materials"]
    assert "50000 litres" in result["dimensions"]
    assert "M30" in result["grades"]
    assert "BIS certification" in result["certificationRequirements"]
    assert "potable water" in result["uses"]
    assert result["testingRequirements"]


def test_empty_text():
    result = extract_tender_requirements("")

    assert result["product"] == ""
    assert result["materials"] == []
    assert result["dimensions"] == []
    assert result["grades"] == []


def test_does_not_invent_requirements():
    text = "Procurement of concrete water tanks."

    result = extract_tender_requirements(text)

    assert result["product"] == "concrete water tanks"
    assert result["grades"] == []
    assert result["dimensions"] == []
    assert result["certificationRequirements"] == []


def test_build_requirement_query():
    requirements = {
        "product": "reinforced concrete water tanks",
        "materials": ["reinforced concrete"],
        "dimensions": ["50000 litres"],
        "grades": ["M30"],
        "performanceRequirements": [],
        "testingRequirements": ["compressive strength testing"],
        "certificationRequirements": ["BIS certification"],
        "uses": ["potable water"],
    }

    query = build_requirement_query(requirements)

    assert "reinforced concrete water tanks" in query
    assert "50000 litres" in query
    assert "M30" in query
    assert "BIS certification" in query
    