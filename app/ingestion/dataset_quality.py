from __future__ import annotations

from typing import Any


PLACEHOLDER_PHRASES = {
    "requirements specified in the standard",
    "as specified by the standard",
    "verify current applicability",
    "as applicable",
    "as per the standard",
    "refer to the standard",
}


FIELD_WEIGHTS = {
    "scope": 0.20,
    "productDetails": 0.20,
    "keywords": 0.10,
    "technicalRequirements": 0.20,
    "testingAndInspection": 0.10,
    "alliedStandards": 0.05,
    "compliance": 0.05,
    "procurementRelevance": 0.10,
}


def _get_field(value: Any, field: str) -> Any:
    """
    Read a field from either a dictionary or a Pydantic model.
    """
    if isinstance(value, dict):
        return value.get(field)

    return getattr(value, field, None)


def _clean(value: Any) -> str:
    if value is None:
        return ""

    if isinstance(value, dict):
        return " ".join(
            _clean(item)
            for item in value.values()
        )

    if isinstance(value, list):
        return " ".join(
            _clean(item)
            for item in value
        )

    return str(value).strip().lower()


def _meaningful_text(value: Any) -> bool:
    text = _clean(value)

    if not text:
        return False

    return not any(
        phrase in text
        for phrase in PLACEHOLDER_PHRASES
    )


def _meaningful_list(value: Any) -> bool:
    if value is None:
        return False

    if not isinstance(value, list):
        return _meaningful_text(value)

    return any(
        _meaningful_text(item)
        for item in value
    )


def _meaningful_dict(
    value: Any,
    fields: list[str],
) -> bool:
    """
    Check actual nested fields.

    Supports both dictionaries and Pydantic models.
    """

    if value is None:
        return False

    for field in fields:
        field_value = _get_field(
            value,
            field,
        )

        if isinstance(field_value, list):
            if _meaningful_list(field_value):
                return True

        elif _meaningful_text(field_value):
            return True

    return False


def calculate_standard_quality(
    standard: Any,
) -> dict[str, Any]:
    """
    Calculate RAG evidence quality for one BIS standard.
    """

    product_details = _get_field(
        standard,
        "productDetails",
    )

    technical = _get_field(
        standard,
        "technicalRequirements",
    )

    testing = _get_field(
        standard,
        "testingAndInspection",
    )

    compliance = _get_field(
        standard,
        "compliance",
    )

    procurement = _get_field(
        standard,
        "procurementRelevance",
    )

    checks = {
        "scope": _meaningful_text(
            _get_field(standard, "scope")
        ),

        "productDetails": _meaningful_dict(
            product_details,
            [
                "productType",
                "productCategory",
                "productDescription",
                "materials",
                "intendedUses",
                "applications",
                "synonyms",
            ],
        ),

        "keywords": _meaningful_list(
            _get_field(
                standard,
                "keywords",
            )
        ),

        "technicalRequirements": _meaningful_dict(
            technical,
            [
                "keyRequirements",
                "materials",
                "grades",
                "dimensions",
                "performanceRequirements",
                "designRequirements",
                "specificationRequirements",
            ],
        ),

        "testingAndInspection": _meaningful_dict(
            testing,
            [
                "testMethods",
                "relatedTestStandards",
                "inspectionRequirements",
            ],
        ),

        "alliedStandards": _meaningful_list(
            _get_field(
                standard,
                "alliedStandards",
            )
        ),

        "compliance": _meaningful_dict(
            compliance,
            [
                "certificationScheme",
                "schemes",
                "qualityControlOrder",
                "crsApplicability",
                "hallmarkingApplicability",
                "certificationBody",
                "notes",
            ],
        ),

        "procurementRelevance": _meaningful_dict(
            procurement,
            [
                "recommendedFor",
                "specificationPoints",
                "buyerConsiderations",
                "procurementKeywords",
            ],
        ),
    }

    weighted_score = sum(
        FIELD_WEIGHTS[field]
        for field, present in checks.items()
        if present
    )

    score = round(
        weighted_score,
        2,
    )

    if score >= 0.75:
        quality = "high"
    elif score >= 0.50:
        quality = "medium"
    else:
        quality = "low"

    return {
        "standardNumber": _get_field(
            standard,
            "standardNumber",
        ),
        "score": score,
        "quality": quality,
        "checks": checks,
    }


def calculate_dataset_quality(
    standards: list[Any],
) -> dict[str, Any]:
    """
    Calculate RAG evidence quality for an entire dataset.
    """

    results = [
        calculate_standard_quality(
            standard
        )
        for standard in standards
    ]

    if not results:
        return {
            "score": 0.0,
            "quality": "low",
            "standards": 0,
            "high": 0,
            "medium": 0,
            "low": 0,
            "results": [],
        }

    average_score = round(
        sum(
            result["score"]
            for result in results
        ) / len(results),
        2,
    )

    high = sum(
        result["quality"] == "high"
        for result in results
    )

    medium = sum(
        result["quality"] == "medium"
        for result in results
    )

    low = sum(
        result["quality"] == "low"
        for result in results
    )

    if average_score >= 0.75:
        quality = "high"
    elif average_score >= 0.50:
        quality = "medium"
    else:
        quality = "low"

    return {
        "score": average_score,
        "quality": quality,
        "standards": len(results),
        "high": high,
        "medium": medium,
        "low": low,
        "results": results,
    }