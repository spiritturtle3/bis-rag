from app.database.models import BISStandard


STRUCTURAL_REQUIRED_FIELDS = [
    "standardNumber",
    "title",
    "issuingOrganization",
]


def validate_standard(standard: BISStandard) -> list[str]:
    """
    Validate the structural integrity of a BIS standard.

    Missing optional/content fields are not treated as fatal errors.
    They are handled separately as completeness issues.
    """

    errors = []

    for field in STRUCTURAL_REQUIRED_FIELDS:
        value = getattr(standard, field, None)

        if value is None or (
            isinstance(value, str) and not value.strip()
        ):
            errors.append(f"Missing required field: {field}")

    if not standard.standardNumber.strip():
        errors.append("standardNumber cannot be empty")

    if not standard.title.strip():
        errors.append("title cannot be empty")

    return errors


def get_completeness_warnings(
    standard: BISStandard,
) -> list[str]:
    """
    Report fields that are empty but are not structurally required.

    These warnings are useful for improving the dataset later.
    """

    warnings = []

    if not standard.scope.strip():
        warnings.append("scope is empty")

    if not standard.productDetails.productDescription:
        warnings.append(
            "productDetails.productDescription is empty"
        )

    if not standard.keywords:
        warnings.append("keywords are empty")

    if not standard.technicalRequirements.keyRequirements:
        warnings.append(
            "technicalRequirements.keyRequirements are empty"
        )

    if not standard.testingAndInspection.testMethods:
        warnings.append(
            "testingAndInspection.testMethods are empty"
        )

    return warnings


def validate_standards(
    standards: list[BISStandard],
) -> dict:
    """
    Validate a collection of BIS standards.
    """

    valid = []
    invalid = []
    warnings = []

    for standard in standards:
        errors = validate_standard(standard)

        standard_warnings = get_completeness_warnings(
            standard
        )

        if errors:
            invalid.append(
                {
                    "standardNumber": standard.standardNumber,
                    "errors": errors,
                }
            )
        else:
            valid.append(standard)

        if standard_warnings:
            warnings.append(
                {
                    "standardNumber": standard.standardNumber,
                    "warnings": standard_warnings,
                }
            )

    return {
        "valid": valid,
        "invalid": invalid,
        "warnings": warnings,
        "total": len(standards),
        "validCount": len(valid),
        "invalidCount": len(invalid),
        "warningCount": len(warnings),
    }