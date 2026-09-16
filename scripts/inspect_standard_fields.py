from pprint import pprint

from app.database.mongodb import db


STANDARD_NUMBER = "IS 458:2021"


def main():
    standard = db["standards"].find_one(
        {"standardNumber": STANDARD_NUMBER},
        {"_id": 0},
    )

    if not standard:
        print(
            f"Standard not found: {STANDARD_NUMBER}"
        )
        return

    print("=" * 90)
    print(f"STANDARD: {STANDARD_NUMBER}")
    print("=" * 90)

    fields = [
        "standardNumber",
        "title",
        "scope",
        "productDescription",
        "productDetails",
        "technicalRequirements",
        "testingAndInspection",
        "compliance",
        "procurementRelevance",
        "alliedStandards",
        "standardRelationships",
        "amendments",
    ]

    for field in fields:
        print("\n" + "-" * 90)
        print(f"{field}:")
        pprint(
            standard.get(field),
            sort_dicts=False,
        )


if __name__ == "__main__":
    main()