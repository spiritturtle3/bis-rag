from __future__ import annotations

import re
from typing import Any


STANDARD_PATTERN = re.compile(
    r"\bIS\s+\d+(?:\s*\(Part\s+\d+\))?:\d{4}\b",
    re.IGNORECASE,
)


def _normalize_standard_number(value: str) -> str:
    value = re.sub(r"\s+", " ", value.strip())
    value = re.sub(r"\(\s*", "(", value)
    value = re.sub(r"\s*\)", ")", value)
    return value


def _allowed_standards(
    recommendations: list[dict],
) -> set[str]:
    return {
        _normalize_standard_number(
            str(item.get("standardNumber", ""))
        ).lower()
        for item in recommendations
        if item.get("standardNumber")
    }


def _standard_is_allowed(
    standard_number: str,
    allowed: set[str],
) -> bool:
    return (
        _normalize_standard_number(standard_number).lower()
        in allowed
    )


def validate_llm_answer(
    answer: dict[str, Any],
    recommendations: list[dict],
) -> dict[str, Any]:
    """
    Ensure the LLM cannot introduce standards that were not
    present in the final RAG recommendations.
    """

    allowed = _allowed_standards(recommendations)

    validated = dict(answer)

    validated_recommendations = []

    for item in answer.get("recommendations", []):
        if not isinstance(item, dict):
            continue

        standard_number = item.get("standardNumber", "")

        if not standard_number:
            continue

        if _standard_is_allowed(
            standard_number,
            allowed,
        ):
            validated_recommendations.append(item)

    validated["recommendations"] = validated_recommendations

    validated_certification = []

    for item in answer.get("certification", []):
        if not isinstance(item, dict):
            continue

        standard_number = item.get(
            "standardNumber",
            "",
        )

        if (
            standard_number
            and _standard_is_allowed(
                standard_number,
                allowed,
            )
        ):
            validated_certification.append(item)

    validated["certification"] = validated_certification

    validated_testing = []

    for item in answer.get("testing", []):
        if not isinstance(item, dict):
            continue

        standard_number = item.get(
            "standardNumber",
            "",
        )

        if not standard_number:
            validated_testing.append(item)
            continue

        # Testing entries may contain multiple standards.
        mentioned = STANDARD_PATTERN.findall(
            str(standard_number)
        )

        if not mentioned:
            continue

        if all(
            _standard_is_allowed(
                standard,
                allowed,
            )
            for standard in mentioned
        ):
            validated_testing.append(item)

    validated["testing"] = validated_testing

    warnings = list(answer.get("warnings", []))

    removed = []

    for item in answer.get("recommendations", []):
        if not isinstance(item, dict):
            continue

        standard_number = item.get(
            "standardNumber",
            "",
        )

        if (
            standard_number
            and not _standard_is_allowed(
                standard_number,
                allowed,
            )
        ):
            removed.append(standard_number)

    if removed:
        warnings.append(
            "LLM output referenced standards that were not "
            "present in the retrieved RAG results. "
            "Those standards were removed."
        )

    validated["warnings"] = warnings

    return validated