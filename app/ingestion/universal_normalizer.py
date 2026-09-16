from __future__ import annotations

import re
from typing import Any

from app.database.models import BISStandard


def as_list(value: Any) -> list[Any]:
    """
    Convert common input types into a list.
    """
    if value is None:
        return []

    if isinstance(value, list):
        return value

    if isinstance(value, (tuple, set)):
        return list(value)

    if isinstance(value, str):
        value = value.strip()
        return [value] if value else []

    return [value]


def as_string(value: Any, default: str = "") -> str:
    """
    Convert a value into a cleaned string.
    """
    if value is None:
        return default

    if isinstance(value, str):
        return re.sub(r"\s+", " ", value).strip()

    return str(value).strip()


def normalize_standard_number(value: Any) -> str:
    """
    Normalize common Indian Standard number variations.
    """
    value = as_string(value)

    value = re.sub(r"\s+", " ", value)
    value = re.sub(r"\(\s*", "(", value)
    value = re.sub(r"\s*\)", ")", value)
    value = re.sub(
        r"\bPart\s*(\d+)",
        r"Part \1",
        value,
        flags=re.IGNORECASE,
    )

    return value


def normalize_language(value: Any) -> str:
    """
    Normalize language names and codes.
    """
    language = as_string(value).lower()

    mapping = {
        "english": "en",
        "eng": "en",
        "en-us": "en",
        "en-in": "en",
        "hindi": "hi",
        "hin": "hi",
        "हिंदी": "hi",
    }

    return mapping.get(language, language or "en")


def normalize_issuer(value: Any) -> str:
    """
    Normalize issuing organization names.
    """
    issuer = as_string(value)

    if not issuer:
        return "Bureau of Indian Standards"

    aliases = {
        "bis": "Bureau of Indian Standards",
        "bureau of indian standards": "Bureau of Indian Standards",
        "bureau of indian standard": "Bureau of Indian Standards",
    }

    return aliases.get(issuer.lower(), issuer)


def normalize_string_list(value: Any) -> list[str]:
    """
    Convert a field into a unique list of strings.
    """
    values = as_list(value)
    result = []

    for item in values:
        if isinstance(item, dict):
            item = (
                item.get("value")
                or item.get("name")
                or item.get("description")
                or item.get("text")
                or ""
            )

        text = as_string(item)

        if text and text.lower() not in {
            existing.lower() for existing in result
        }:
            result.append(text)

    return result


def normalize_product_details(value: Any) -> dict[str, Any]:
    """
    Normalize productDetails.
    """
    value = value if isinstance(value, dict) else {}

    return {
        "productType": as_string(value.get("productType")),
        "productCategory": as_string(
            value.get("productCategory")
        ),
        "productDescription": as_string(
            value.get("productDescription")
        ),
        "materials": normalize_string_list(
            value.get("materials")
        ),
        "intendedUses": normalize_string_list(
            value.get("intendedUses")
        ),
        "applications": normalize_string_list(
            value.get("applications")
        ),
        "synonyms": normalize_string_list(
            value.get("synonyms")
        ),
    }


def normalize_technical_requirements(
    value: Any,
) -> dict[str, Any]:
    """
    Normalize technicalRequirements.
    """
    value = value if isinstance(value, dict) else {}

    return {
        "keyRequirements": normalize_string_list(
            value.get("keyRequirements")
            or value.get("requirements")
        ),
        "materials": normalize_string_list(
            value.get("materials")
        ),
        "grades": normalize_string_list(
            value.get("grades")
        ),
        "dimensions": normalize_string_list(
            value.get("dimensions")
        ),
        "performanceRequirements": normalize_string_list(
            value.get("performanceRequirements")
        ),
        "designRequirements": normalize_string_list(
            value.get("designRequirements")
        ),
        "specificationRequirements": normalize_string_list(
            value.get("specificationRequirements")
        ),
    }


def normalize_testing_and_inspection(
    value: Any,
) -> dict[str, Any]:
    """
    Normalize testingAndInspection.
    """
    value = value if isinstance(value, dict) else {}

    required = value.get("required", False)

    if isinstance(required, str):
        required = required.lower() in {
            "true",
            "yes",
            "required",
            "mandatory",
        }

    return {
        "required": bool(required),
        "testMethods": normalize_string_list(
            value.get("testMethods")
            or value.get("testingMethods")
        ),
        "relatedTestStandards": normalize_string_list(
            value.get("relatedTestStandards")
        ),
        "inspectionRequirements": normalize_string_list(
            value.get("inspectionRequirements")
        ),
    }


def normalize_allied_standards(
    value: Any,
) -> list[dict[str, Any]]:
    """
    Normalize allied standards represented as strings
    or dictionaries.
    """
    result = []

    for item in as_list(value):

        if isinstance(item, str):
            standard_number = normalize_standard_number(item)

            if standard_number:
                result.append(
                    {
                        "standardNumber": standard_number,
                        "relationshipType": "allied",
                        "title": "",
                        "description": "",
                    }
                )

            continue

        if not isinstance(item, dict):
            continue

        standard_number = normalize_standard_number(
            item.get("standardNumber")
            or item.get("number")
            or item.get("code")
        )

        if not standard_number:
            continue

        result.append(
            {
                "standardNumber": standard_number,
                "relationshipType": as_string(
                    item.get("relationshipType")
                    or item.get("relationship")
                    or "allied"
                ),
                "title": as_string(
                    item.get("title")
                ),
                "description": as_string(
                    item.get("description")
                    or item.get("reason")
                ),
            }
        )

    return result


def normalize_current_edition(
    value: Any,
) -> dict[str, Any]:
    """
    Normalize currentEdition.
    """
    if isinstance(value, str):
        return {
            "edition": value,
            "year": None,
            "publishedDate": None,
            "status": "",
        }

    if not isinstance(value, dict):
        return {
            "edition": "",
            "year": None,
            "publishedDate": None,
            "status": "",
        }

    return {
        "edition": as_string(
            value.get("edition")
        ),
        "year": value.get("year"),
        "publishedDate": value.get("publishedDate"),
        "status": as_string(
            value.get("status")
        ),
    }


def normalize_amendments(
    value: Any,
) -> list[dict[str, Any]]:
    """
    Normalize amendment information.
    """
    result = []

    for index, item in enumerate(
        as_list(value),
        start=1,
    ):

        if isinstance(item, str):
            result.append(
                {
                    "amendmentNumber": str(index),
                    "date": None,
                    "title": item,
                    "description": "",
                }
            )
            continue

        if not isinstance(item, dict):
            continue

        result.append(
            {
                "amendmentNumber": as_string(
                    item.get("amendmentNumber")
                    or item.get("number")
                    or index
                ),
                "date": item.get("date"),
                "title": as_string(
                    item.get("title")
                ),
                "description": as_string(
                    item.get("description")
                ),
            }
        )

    return result


def normalize_compliance(
    value: Any,
) -> dict[str, Any]:
    """
    Normalize compliance information.
    """
    if isinstance(value, str):
        text = as_string(value)
        lowered = text.lower()

        return {
            "mandatory": "mandatory" in lowered,
            "certificationRequired": (
                "certification" in lowered
                or "isi mark" in lowered
                or "bis" in lowered
            ),
            "certificationScheme": "",
            "schemes": [],
            "qualityControlOrder": "",
            "crsApplicability": "",
            "hallmarkingApplicability": "",
            "certificationBody": "",
            "notes": text,
        }

    value = value if isinstance(value, dict) else {}

    return {
        "mandatory": bool(
            value.get("mandatory", False)
        ),
        "certificationRequired": bool(
            value.get("certificationRequired", False)
        ),
        "certificationScheme": as_string(
            value.get("certificationScheme")
        ),
        "schemes": normalize_string_list(
            value.get("schemes")
        ),
        "qualityControlOrder": as_string(
            value.get("qualityControlOrder")
        ),
        "crsApplicability": as_string(
            value.get("crsApplicability")
        ),
        "hallmarkingApplicability": as_string(
            value.get("hallmarkingApplicability")
        ),
        "certificationBody": as_string(
            value.get("certificationBody")
        ),
        "notes": as_string(
            value.get("notes")
        ),
    }


def normalize_procurement_relevance(
    value: Any,
) -> dict[str, Any]:
    """
    Normalize procurement relevance.
    """
    value = value if isinstance(value, dict) else {}

    applicable = value.get(
        "applicableToProcurement",
        False,
    )

    if isinstance(applicable, str):
        applicable = applicable.lower() in {
            "true",
            "yes",
            "applicable",
            "relevant",
        }

    return {
        "applicableToProcurement": bool(applicable),
        "recommendedFor": normalize_string_list(
            value.get("recommendedFor")
        ),
        "specificationPoints": normalize_string_list(
            value.get("specificationPoints")
        ),
        "buyerConsiderations": normalize_string_list(
            value.get("buyerConsiderations")
        ),
        "procurementKeywords": normalize_string_list(
            value.get("procurementKeywords")
        ),
    }


def normalize_source(
    value: Any,
) -> dict[str, Any]:
    """
    Normalize source metadata.
    """
    value = value if isinstance(value, dict) else {}

    return {
        "sourceType": as_string(
            value.get("sourceType")
            or value.get("type")
            or "dataset"
        ),
        "sourceUrl": as_string(
            value.get("sourceUrl")
            or value.get("url")
        ),
        "documentName": as_string(
            value.get("documentName")
            or value.get("fileName")
            or value.get("name")
        ),
        "retrievedDate": value.get(
            "retrievedDate"
        ),
    }


def normalize_standard_record(
    data: dict[str, Any] | BISStandard,
) -> BISStandard:
    """
    Normalize one dataset record.

    Accepts either:
    - a raw dictionary from a future dataset
    - an existing BISStandard object
    """

    # Existing BISStandard objects are already normalized.
    if isinstance(data, BISStandard):
        return data

    if not isinstance(data, dict):
        raise TypeError(
            "Dataset record must be a dictionary "
            "or BISStandard object."
        )

    normalized = {
        "standardNumber": normalize_standard_number(
            data.get("standardNumber")
            or data.get("standard_number")
            or data.get("number")
            or data.get("code")
        ),
        "title": as_string(
            data.get("title")
            or data.get("standardTitle")
            or data.get("name")
        ),
        "issuingOrganization": normalize_issuer(
            data.get("issuingOrganization")
            or data.get("issuer")
            or data.get("organization")
        ),
        "scope": as_string(
            data.get("scope")
            or data.get("description")
            or data.get("applicationScope")
        ),
        "category": as_string(
            data.get("category")
            or data.get("sector")
        ),
        "productDetails": normalize_product_details(
            data.get("productDetails")
        ),
        "keywords": normalize_string_list(
            data.get("keywords")
            or data.get("procurementKeywords")
        ),
        "technicalRequirements": (
            normalize_technical_requirements(
                data.get("technicalRequirements")
            )
        ),
        "testingAndInspection": (
            normalize_testing_and_inspection(
                data.get("testingAndInspection")
                or data.get("testing")
            )
        ),
        "alliedStandards": normalize_allied_standards(
            data.get("alliedStandards")
            or data.get("relatedStandards")
        ),
        "currentEdition": normalize_current_edition(
            data.get("currentEdition")
            or data.get("edition")
        ),
        "amendments": normalize_amendments(
            data.get("amendments")
            or data.get("amendment")
        ),
        "compliance": normalize_compliance(
            data.get("compliance")
            or data.get("certification")
        ),
        "procurementRelevance": (
            normalize_procurement_relevance(
                data.get("procurementRelevance")
            )
        ),
        "standardRelationships": data.get(
            "standardRelationships",
            [],
        ),
        "applicableDomains": normalize_string_list(
            data.get("applicableDomains")
        ),
        "language": normalize_language(
            data.get("language")
        ),
        "multilingualTerms": data.get(
            "multilingualTerms",
            [],
        ),
        "source": normalize_source(
            data.get("source")
        ),
    }

    return BISStandard.model_validate(normalized)


def normalize_dataset(
    records: list[dict[str, Any] | BISStandard],
) -> tuple[list[BISStandard], list[dict[str, Any]]]:
    """
    Normalize an entire dataset.

    Returns:
        valid_records:
            Successfully normalized BISStandard objects.

        errors:
            Records that could not be normalized.
    """
    valid_records = []
    errors = []
    seen_numbers = set()

    for index, record in enumerate(records):

        try:
            standard = normalize_standard_record(record)

            number = (
                standard.standardNumber
                .strip()
                .lower()
            )

            if not number:
                raise ValueError(
                    "Missing standardNumber."
                )

            if number in seen_numbers:
                continue

            seen_numbers.add(number)
            valid_records.append(standard)

        except Exception as exc:
            errors.append(
                {
                    "recordIndex": index,
                    "error": str(exc),
                }
            )

    return valid_records, errors