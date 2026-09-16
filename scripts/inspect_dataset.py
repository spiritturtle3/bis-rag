import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.ingestion.dataset_pdf_parser import parse_dataset_pdf
from app.ingestion.validator import (
    get_completeness_warnings,
    validate_standards,
)


PDF_PATH = PROJECT_ROOT / "data" / "raw" / "10set.pdf"


def main():
    standards = parse_dataset_pdf(str(PDF_PATH))
    validation = validate_standards(standards)

    print()
    print("=" * 60)
    print("BIS DATASET INSPECTION")
    print("=" * 60)

    print(f"Total records:   {validation['total']}")
    print(f"Valid records:   {validation['validCount']}")
    print(f"Invalid records: {validation['invalidCount']}")
    print(f"With warnings:   {validation['warningCount']}")

    print()
    print("STANDARDS")
    print("-" * 60)

    for index, standard in enumerate(standards, start=1):
        warnings = get_completeness_warnings(standard)

        print(f"{index}. {standard.standardNumber}")
        print(f"   Title: {standard.title}")
        print(
            f"   Scope: "
            f"{'YES' if standard.scope.strip() else 'EMPTY'}"
        )
        print(f"   Keywords: {len(standard.keywords)}")
        print(
            f"   Technical requirements: "
            f"{len(standard.technicalRequirements.keyRequirements)}"
        )
        print(
            f"   Test methods: "
            f"{len(standard.testingAndInspection.testMethods)}"
        )
        print(
            f"   Allied standards: "
            f"{len(standard.alliedStandards)}"
        )

        if warnings:
            print("   Warnings:")
            for warning in warnings:
                print(f"      - {warning}")

        print()

    print("=" * 60)


if __name__ == "__main__":
    main()