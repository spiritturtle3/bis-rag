import re

from app.database.models import BISStandard


def normalize_standard_number(value: str) -> str:
    """Normalize spacing inside BIS standard numbers."""
    value = value.strip()

    # Normalize whitespace.
    value = re.sub(r"\s+", " ", value)

    # Normalize spaces around parentheses.
    value = re.sub(r"\(\s*", "(", value)
    value = re.sub(r"\s*\)", ")", value)

    # Normalize "Part1" -> "Part 1".
    value = re.sub(r"\bPart\s*(\d+)", r"Part \1", value)

    return value


def normalize_standard(data: dict) -> BISStandard:
    """Validate and normalize a BIS standard record."""
    data = dict(data)

    if data.get("standardNumber"):
        data["standardNumber"] = normalize_standard_number(
            data["standardNumber"]
        )

    return BISStandard.model_validate(data)