from pprint import pprint

from app.ingestion.dataset_pdf_parser import parse_dataset_pdf


PDF_PATH = "data/raw/10set.pdf"
TARGET_STANDARD = "IS 17725:2022"


def main():
    records = parse_dataset_pdf(PDF_PATH)

    print(f"Parsed records: {len(records)}")

    matches = [
        record
        for record in records
        if record.standardNumber == TARGET_STANDARD
    ]

    if not matches:
        print(
            f"\nCould not find: {TARGET_STANDARD}"
        )
        print("\nAvailable standard numbers:")

        for record in records:
            print(
                f"  - {record.standardNumber}"
            )

        return

    record = matches[0]

    print("\n" + "=" * 90)
    print(f"PARSED RECORD: {TARGET_STANDARD}")
    print("=" * 90)

    fields = [
        "standardNumber",
        "title",
        "scope",
        "productDetails",
        "technicalRequirements",
        "testingAndInspection",
        "compliance",
        "procurementRelevance",
        "alliedStandards",
        "standardRelationships",
        "amendments",
    ]

    data = record.model_dump()

    for field in fields:
        print("\n" + "-" * 90)
        print(f"{field}:")
        pprint(
            data.get(field),
            sort_dicts=False,
        )


if __name__ == "__main__":
    main()