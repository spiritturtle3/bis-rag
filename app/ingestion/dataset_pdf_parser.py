import json
import re
from pathlib import Path

import pymupdf

from app.database.models import BISStandard


MAIN_STANDARD_FIELDS = {
    "standardNumber",
    "title",
    "issuingOrganization",
    "scope",
    "category",
    "applicableDomains",
    "productDetails",
    "keywords",
    "technicalRequirements",
    "testingAndInspection",
    "alliedStandards",
    "currentEdition",
    "amendments",
    "compliance",
    "procurementRelevance",
    "standardRelationships",
    "language",
    "multilingualTerms",
    "source",
}


def extract_pdf_text(pdf_path: str) -> str:
    """Extract the complete text of the PDF."""

    document = pymupdf.open(pdf_path)

    try:
        return "\n".join(
            page.get_text("text")
            for page in document
        )
    finally:
        document.close()


def clean_pdf_artifacts(text: str) -> str:
    """
    Remove known PDF-generated headers/footers that can appear
    inside JSON records after text extraction.
    """

    pattern = (
        r"Construction BIS RAG\s*[—-]\s*tightly filled dataset"
        r"\s*\|\s*\d{1,2}\s+\w+\s+\d{4}"
        r"\s*\n?\s*Page\s+\d+"
    )

    return re.sub(
        pattern,
        "",
        text,
        flags=re.IGNORECASE,
    )


def normalize_json_candidate(candidate: str) -> str:
    """
    Normalize PDF-extracted JSON.

    Handles:
    - literal newlines inside JSON strings
    - page-break artifacts
    - strings that were cut off immediately before a
      JSON closing ] or } because of PDF extraction
    """

    normalized = []
    inside_string = False
    escaped = False

    index = 0

    while index < len(candidate):

        char = candidate[index]

        if inside_string:

            if escaped:
                escaped = False
                normalized.append(char)
                index += 1
                continue

            if char == "\\":
                escaped = True
                normalized.append(char)
                index += 1
                continue

            if char == '"':
                inside_string = False
                normalized.append(char)
                index += 1
                continue

            if char in ("\n", "\r"):

                # Look ahead past whitespace.
                next_index = index + 1

                while (
                    next_index < len(candidate)
                    and candidate[next_index] in " \t\r\n"
                ):
                    next_index += 1

                # If the next meaningful character is a JSON
                # structural closer, the PDF likely cut off
                # the closing quote of this string.
                if (
                    next_index < len(candidate)
                    and candidate[next_index] in "]}},"
                ):
                    normalized.append('"')
                    normalized.append(" ")
                    inside_string = False
                    index += 1
                    continue

                # Normal PDF line wrapping inside a string.
                normalized.append(" ")
                index += 1
                continue

            normalized.append(char)
            index += 1
            continue

        normalized.append(char)

        if char == '"':
            inside_string = True

        index += 1

    return "".join(normalized)

def normalize_record_shape(record: dict) -> dict:
    """
    Normalize known dataset schema variations into the BISStandard shape.
    Keeps the canonical database model unchanged.
    """

    record = dict(record)

    # alliedStandards:
    # ["IS 800", "IS 808"]
    # ->
    # [{"standardNumber": "IS 800", "relationshipType": "allied"}, ...]
    allied = record.get("alliedStandards")

    if isinstance(allied, list):
        normalized_allied = []

        for item in allied:
            if isinstance(item, str):
                normalized_allied.append(
                    {
                        "standardNumber": item,
                        "relationshipType": "allied",
                    }
                )
            elif isinstance(item, dict):
                normalized_allied.append(item)

        record["alliedStandards"] = normalized_allied

    # compliance.notes:
    # ["note 1", "note 2"]
    # ->
    # "note 1; note 2"
    compliance = record.get("compliance")

    if isinstance(compliance, dict):
        compliance = dict(compliance)
        notes = compliance.get("notes")

        if isinstance(notes, list):
            compliance["notes"] = "; ".join(
                str(note) for note in notes
            )

        record["compliance"] = compliance

    # amendments:
    # ["amendment description"]
    # ->
    # [{"description": "amendment description"}]
    amendments = record.get("amendments")

    if isinstance(amendments, list):
        normalized_amendments = []

        for item in amendments:
            if isinstance(item, str):
                normalized_amendments.append(
                    {
                        "description": item,
                    }
                )
            elif isinstance(item, dict):
                normalized_amendments.append(item)

        record["amendments"] = normalized_amendments

    # standardRelationships:
    # {"relatedStandard": "...", "relationship": "..."}
    # ->
    # canonical field names
    relationships = record.get("standardRelationships")

    if isinstance(relationships, list):
        normalized_relationships = []

        for item in relationships:
            if not isinstance(item, dict):
                continue

            item = dict(item)

            if "relatedStandardNumber" not in item:
                item["relatedStandardNumber"] = item.pop(
                    "relatedStandard",
                    "",
                )

            if "relationshipType" not in item:
                item["relationshipType"] = item.pop(
                    "relationship",
                    "related",
                )

            normalized_relationships.append(item)

        record["standardRelationships"] = normalized_relationships

    return record

def extract_json_objects(text: str) -> tuple[list[dict], list[str]]:
    """
    Extract JSON objects from PDF text.

    Supports both:
    1. Direct BISStandard records
    2. Records wrapped inside {"BISStandard": {...}}
    """

    text = clean_pdf_artifacts(text)

    objects = []
    failures = []

    start = None
    depth = 0
    in_string = False
    escape = False

    for index, char in enumerate(text):

        if in_string:
            if escape:
                escape = False
            elif char == "\\":
                escape = True
            elif char == '"':
                in_string = False
            continue

        if char == '"':
            in_string = True

        elif char == "{":
            if depth == 0:
                start = index
            depth += 1

        elif char == "}":
            if depth == 0:
                continue

            depth -= 1

            if depth == 0 and start is not None:

                candidate = text[start:index + 1]
                candidate = normalize_json_candidate(candidate)

                try:
                    parsed = json.loads(candidate)

                    if not isinstance(parsed, dict):
                        start = None
                        continue

                    # Format 1:
                    # {"standardNumber": "...", ...}
                    parsed = normalize_record_shape(parsed)

                    if is_main_standard(parsed):
                        objects.append(parsed)

                    # Format 2:
                    # {"BISStandard": {"standardNumber": "...", ...}}
                    elif isinstance(parsed.get("BISStandard"), dict):
                        wrapped = normalize_record_shape(
                            parsed["BISStandard"]
                        )

                        if is_main_standard(wrapped):
                            objects.append(wrapped)

                except json.JSONDecodeError as exc:
                    failures.append(
                        f"JSON parse error near character "
                        f"{start}: {exc}"
                    )

                start = None

    return objects, failures


def is_main_standard(record: dict) -> bool:
    """
    Determine whether an object is a complete BIS standard record.

    Nested allied-standard objects do not contain the full
    BISStandard structure and are therefore excluded.
    """

    return MAIN_STANDARD_FIELDS.issubset(record.keys())


def extract_dataset_records(pdf_path: str) -> list[dict]:
    """
    Extract all main BIS standard records.

    No record count and no record numbering are hard-coded.
    """

    full_text = extract_pdf_text(pdf_path)

    objects, failures = extract_json_objects(full_text)

    records = [
        obj
        for obj in objects
        if is_main_standard(obj)
    ]

    if failures:
        raise ValueError(
            "The PDF contains JSON parsing failures:\n"
            + "\n".join(failures)
        )

    return records


def parse_dataset_pdf(pdf_path: str) -> list[BISStandard]:
    """
    Parse and validate all BIS standards from a curated PDF.
    """

    path = Path(pdf_path)

    if not path.exists():
        raise FileNotFoundError(
            f"Dataset PDF not found: {pdf_path}"
        )

    raw_records = extract_dataset_records(pdf_path)

    standards = []

    for index, record in enumerate(raw_records, start=1):

        try:
            standard = BISStandard.model_validate(record)

        except Exception as exc:

            standard_number = record.get(
                "standardNumber",
                f"UNKNOWN-{index}",
            )

            raise ValueError(
                f"Invalid BISStandard record #{index} "
                f"({standard_number}): {exc}"
            ) from exc

        standards.append(standard)

    return standards