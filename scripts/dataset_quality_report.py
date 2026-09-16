from app.database.mongodb import db


def is_empty(value) -> bool:
    if value is None:
        return True

    if isinstance(value, str):
        return not value.strip()

    if isinstance(value, (list, dict)):
        return len(value) == 0

    return False


def nested_empty(
    document: dict,
    parent: str,
    child: str,
) -> bool:
    parent_value = document.get(parent)

    if not isinstance(parent_value, dict):
        return True

    return is_empty(parent_value.get(child))


def main():
    collection = db["standards"]

    standards = list(
        collection.find(
            {},
            {"_id": 0},
        )
    )

    print("=" * 90)
    print("BIS DATASET QUALITY REPORT")
    print("=" * 90)

    print(f"\nTotal standards: {len(standards)}")

    # Synthetic records are useful for unit tests but
    # should not affect BIS dataset quality assessment.
    bis_standards = [
        standard
        for standard in standards
        if not standard.get(
            "standardNumber",
            "",
        ).startswith("TEST-")
    ]

    print(
        f"BIS standards assessed: "
        f"{len(bis_standards)}"
    )

    for standard in bis_standards:
        number = standard.get(
            "standardNumber",
            "UNKNOWN",
        )

        title = standard.get(
            "title",
            "UNKNOWN",
        )

        missing = []

        if is_empty(standard.get("scope")):
            missing.append("scope")

        if nested_empty(
            standard,
            "productDetails",
            "productDescription",
        ):
            missing.append(
                "productDetails.productDescription"
            )

        if is_empty(
            standard.get(
                "technicalRequirements"
            )
        ):
            missing.append(
                "technicalRequirements"
            )

        if is_empty(
            standard.get(
                "testingAndInspection"
            )
        ):
            missing.append(
                "testingAndInspection"
            )

        if is_empty(
            standard.get("compliance")
        ):
            missing.append("compliance")

        if is_empty(
            standard.get(
                "procurementRelevance"
            )
        ):
            missing.append(
                "procurementRelevance"
            )

        if is_empty(
            standard.get(
                "alliedStandards"
            )
        ):
            missing.append(
                "alliedStandards"
            )

        if is_empty(
            standard.get(
                "standardRelationships"
            )
        ):
            missing.append(
                "standardRelationships"
            )

        if is_empty(
            standard.get("amendments")
        ):
            missing.append("amendments")

        print("\n" + "-" * 90)
        print(f"Standard: {number}")
        print(f"Title: {title}")

        if missing:
            print("Missing/empty fields:")
            for field in missing:
                print(f"  - {field}")
        else:
            print("Missing/empty fields: None")

    print("\n" + "=" * 90)
    print("SUMMARY")
    print("=" * 90)

    fields = [
        "scope",
        "productDetails.productDescription",
        "technicalRequirements",
        "testingAndInspection",
        "compliance",
        "procurementRelevance",
        "alliedStandards",
        "standardRelationships",
        "amendments",
    ]

    for field in fields:
        count = 0

        for standard in bis_standards:
            if "." in field:
                parent, child = field.split(
                    ".",
                    1,
                )

                if nested_empty(
                    standard,
                    parent,
                    child,
                ):
                    count += 1
            elif is_empty(
                standard.get(field)
            ):
                count += 1

        print(
            f"{field:40} "
            f"{count}/{len(bis_standards)} empty"
        )


if __name__ == "__main__":
    main()