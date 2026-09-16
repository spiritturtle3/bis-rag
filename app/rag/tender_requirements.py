import re

from typing import Any


def _clean_text(text: str) -> str:
    """Normalize whitespace while preserving tender meaning."""
    return re.sub(r"\s+", " ", text).strip()


def _extract_matches(
    pattern: str,
    text: str,
) -> list[str]:
    """Return unique regex matches while preserving order."""

    matches = re.findall(
        pattern,
        text,
        flags=re.IGNORECASE,
    )

    results = []

    for match in matches:
        value = (
            match.strip()
            if isinstance(match, str)
            else str(match).strip()
        )

        if value and value.lower() not in {
            item.lower()
            for item in results
        }:
            results.append(value)

    return results


def _extract_section(
    text: str,
    start_patterns: list[str],
    end_patterns: list[str],
) -> str:
    """Extract a section between two headings."""

    start_pattern = "|".join(start_patterns)
    end_pattern = "|".join(end_patterns)

    pattern = (
        rf"(?:{start_pattern})"
        rf"\s*(.*?)(?="
        rf"(?:{end_pattern})"
        rf"|$)"
    )

    match = re.search(
        pattern,
        text,
        flags=re.IGNORECASE,
    )

    if not match:
        return ""

    return match.group(1).strip()


def _extract_requirement_sentences(
    text: str,
    keywords: list[str],
) -> list[str]:
    """Extract sentences containing requirement terms."""

    sentences = re.split(
        r"(?<=[.;])\s+",
        text,
    )

    results = []

    for sentence in sentences:
        sentence = sentence.strip()

        if not sentence:
            continue

        lower = sentence.lower()

        if any(
            keyword.lower() in lower
            for keyword in keywords
        ):
            if sentence.lower() not in {
                item.lower()
                for item in results
            }:
                results.append(sentence)

    return results


def _extract_product(text: str) -> str:
    """
    Identify the main product from common procurement wording.
    """

    patterns = [
        r"\b(?:procurement|purchase|supply|installation)\s+of\s+"
        r"(.{3,120}?)(?=\.)",

        r"\b(?:procure|purchase|supply)\s+"
        r"(.{3,120}?)(?=\.)",
    ]

    for pattern in patterns:
        match = re.search(
            pattern,
            text,
            flags=re.IGNORECASE,
        )

        if match:
            product = match.group(1).strip()

            product = re.sub(
                r"\s+\d+\s*$",
                "",
                product,
            ).strip()

            return product

    product_match = re.search(
        r"\b(?:reinforced concrete water storage tanks?|"
        r"reinforced concrete water tanks?|"
        r"water storage tanks?|"
        r"concrete water tanks?|"
        r"precast concrete pipes?|"
        r"pipes?|bricks?|doors?|windows?|"
        r"panels?|slabs?|cables?|manholes?)\b",
        text,
        flags=re.IGNORECASE,
    )

    if product_match:
        return product_match.group(0).strip()

    return ""


def extract_tender_requirements(
    text: str,
) -> dict[str, Any]:
    """
    Extract procurement requirements from tender text.

    This is a rule-based MVP extractor.
    It only extracts information explicitly present in the tender.
    """

    if not text or not text.strip():
        return {
            "product": "",
            "materials": [],
            "dimensions": [],
            "grades": [],
            "performanceRequirements": [],
            "testingRequirements": [],
            "certificationRequirements": [],
            "uses": [],
            "rawText": "",
        }

    text = _clean_text(text)

    materials = _extract_matches(
        r"\b(?:reinforced concrete|plain concrete|"
        r"concrete|reinforced steel|stainless steel|"
        r"steel|cement|brick|gypsum|glass fibre|"
        r"glass fiber|clay|aluminium|aluminum|"
        r"timber|wood)\b",
        text,
    )

    dimensions = _extract_matches(
        r"\b\d+(?:\.\d+)?\s*"
        r"(?:mm|cm|m|metre|meter|metres|meters|"
        r"kg|tonne|tonnes|litre|litres|liter|liters|l|"
        r"m3|m²|m2)\b",
        text,
    )

    dimension_phrases = _extract_matches(
        r"\b(?:capacity|dimension|dimensions|"
        r"length|width|height|diameter|thickness|"
        r"volume)\s+(?:of\s+)?"
        r"\d+(?:\.\d+)?\s*"
        r"(?:mm|cm|m|m3|m²|m2|litres?|liters?|l)\b",
        text,
    )

    for value in dimension_phrases:
        if value.lower() not in {
            item.lower()
            for item in dimensions
        }:
            dimensions.append(value)

    grades = _extract_matches(
        r"\b(?:M\d{2,3}|Fe\d{2,3})\b",
        text,
    )

    named_grades = re.findall(
        r"\b(?:Grade|Class)\s+([A-Z0-9-]+)\b",
        text,
        flags=re.IGNORECASE,
    )

    for grade in named_grades:
        if grade.lower() not in {
            item.lower()
            for item in grades
        }:
            grades.append(grade)

    performance_section = _extract_section(
        text,
        [
            r"\b\d*\.?\s*technical\s+requirements?\b",
            r"\b\d*\.?\s*performance\s+requirements?\b",
            r"\b\d*\.?\s*product\s+requirements?\b",
        ],
        [
            r"\b\d*\.?\s*testing\s+and\s+inspection\b",
            r"\b\d*\.?\s*testing\s+requirements?\b",
            r"\b\d*\.?\s*certification\s+and\s+compliance\b",
            r"\b\d*\.?\s*certification\s+requirements?\b",
            r"\b\d*\.?\s*procurement\s+requirement\b",
        ],
    )

    performance_keywords = [
        "strength",
        "durable",
        "durability",
        "performance",
        "load",
        "capacity",
        "resistance",
        "water tight",
        "watertight",
        "weather resistant",
        "corrosion resistant",
        "suitable",
        "conform",
        "conformity",
        "applicable requirements",
    ]

    performance = _extract_requirement_sentences(
        performance_section or text,
        performance_keywords,
    )

    testing_section = _extract_section(
        text,
        [
            r"\b\d*\.?\s*testing\s+and\s+inspection\b",
            r"\b\d*\.?\s*testing\s+requirements?\b",
            r"\b\d*\.?\s*inspection\s+requirements?\b",
        ],
        [
            r"\b\d*\.?\s*certification\s+and\s+compliance\b",
            r"\b\d*\.?\s*certification\s+requirements?\b",
            r"\b\d*\.?\s*procurement\s+requirement\b",
        ],
    )

    testing_keywords = [
        "test",
        "testing",
        "inspection",
        "test certificate",
        "quality control",
        "acceptance",
        "conformity",
        "strength test",
        "dimensional check",
    ]

    testing = _extract_requirement_sentences(
        testing_section or text,
        testing_keywords,
    )

    if not testing:
        testing = _extract_matches(
            r"\b(?:test(?:ing)?|inspection|"
            r"test certificate|quality control|"
            r"acceptance test|strength test|"
            r"dimensional check)[^.]{0,120}",
            text,
        )

    certification_section = _extract_section(
        text,
        [
            r"\b\d*\.?\s*certification\s+and\s+compliance\b",
            r"\b\d*\.?\s*certification\s+requirements?\b",
            r"\b\d*\.?\s*compliance\s+requirements?\b",
        ],
        [
            r"\b\d*\.?\s*procurement\s+requirement\b",
            r"\b\d*\.?\s*testing\s+and\s+inspection\b",
        ],
    )

    certification = _extract_matches(
        r"\b(?:BIS certification|BIS certified|"
        r"ISI mark|Product Certification|"
        r"CRS|Compulsory Registration Scheme|"
        r"Hallmarking)\b",
        certification_section or text,
    )

    certification_keywords = [
        "bis",
        "certification",
        "certified",
        "isi mark",
        "product certification",
        "crs",
        "compulsory registration scheme",
        "hallmarking",
        "mandatory",
        "conformity",
    ]

    certification_sentences = _extract_requirement_sentences(
        certification_section or text,
        certification_keywords,
    )

    for sentence in certification_sentences:
        if sentence.lower() not in {
            item.lower()
            for item in certification
        }:
            certification.append(sentence)

    uses = _extract_matches(
        r"\b(?:water supply|sewerage|drainage|"
        r"water storage|potable water|"
        r"general water storage|"
        r"construction|building construction|"
        r"civil works|infrastructure|"
        r"industrial use|underground installation|"
        r"above-ground installation)\b",
        text,
    )

    product = _extract_product(text)

    return {
        "product": product,
        "materials": materials,
        "dimensions": dimensions,
        "grades": grades,
        "performanceRequirements": performance,
        "testingRequirements": testing,
        "certificationRequirements": certification,
        "uses": uses,
        "rawText": text,
    }


def build_requirement_query(
    requirements: dict[str, Any],
) -> str:
    """
    Convert extracted tender requirements into a searchable RAG query.
    """

    parts = []

    product = requirements.get("product")

    if product:
        parts.append(product)

    for field in (
        "materials",
        "dimensions",
        "grades",
        "performanceRequirements",
        "testingRequirements",
        "certificationRequirements",
        "uses",
    ):
        values = requirements.get(field, [])

        if not values:
            continue

        for value in values:
            value = str(value).strip()

            if value:
                parts.append(value)

    return " ".join(parts).strip()