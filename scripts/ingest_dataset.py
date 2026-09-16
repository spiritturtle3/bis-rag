import argparse
import json
import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.standard_repository import get_standard
from app.ingestion.dataset_pdf_parser import parse_dataset_pdf
from app.ingestion.dataset_quality import calculate_dataset_quality
from app.ingestion.universal_normalizer import normalize_dataset
from app.ingestion.validator import validate_standards
from app.ingestion.pipeline import ingest_dataset_to_chunks


def check_existing_standards(standards):
    """
    Check which normalized standards already exist in MongoDB.
    """
    existing = []
    new = []

    for standard in standards:
        standard_number = standard.standardNumber

        if get_standard(standard_number):
            existing.append(standard_number)
        else:
            new.append(standard_number)

    return existing, new


def print_report(
    pdf_path,
    records,
    standards,
    normalization_errors,
    validation,
    existing,
    new,
    quality,
):
    print("=" * 60)
    print("BIS DATASET DRY RUN")
    print("=" * 60)

    print(f"PDF: {pdf_path}")
    print()

    print(f"Records found:          {len(records)}")
    print(f"Records normalized:     {len(standards)}")
    print(f"Valid standards:        {len(validation['valid'])}")
    print(f"Invalid standards:      {validation['invalidCount']}")
    print(f"Normalization errors:   {len(normalization_errors)}")
    print(f"Already in database:    {len(existing)}")
    print(f"New standards:          {len(new)}")

    print()
    print("DATASET QUALITY")
    print("-" * 60)

    print(f"Quality:        {quality['quality'].upper()}")
    print(f"Average score:  {quality['score']}")
    print(f"High quality:   {quality['high']}")
    print(f"Medium quality: {quality['medium']}")
    print(f"Low quality:    {quality['low']}")

    print()

    if existing:
        print("ALREADY IN DATABASE")
        print("-" * 60)

        for standard_number in existing:
            print(f"↺ {standard_number}")

        print()

    if new:
        print("NEW STANDARDS")
        print("-" * 60)

        for standard_number in new:
            print(f"+ {standard_number}")

        print()

    if normalization_errors:
        print("NORMALIZATION ERRORS")
        print("-" * 60)

        for error in normalization_errors:
            print(error)

        print()

    if validation["invalid"]:
        print("INVALID STANDARDS")
        print("-" * 60)

        for standard in validation["invalid"]:
            print(f"✗ {standard.standardNumber}")

        print()

    print("=" * 60)
    print("DRY RUN COMPLETE")
    print("=" * 60)

    print("No MongoDB changes were made.")


def run_dry_run(pdf_path):
    """
    Parse, normalize, validate, score quality and check
    MongoDB duplicates without modifying the database.
    """

    records = parse_dataset_pdf(str(pdf_path))

    standards, normalization_errors = normalize_dataset(
        records
    )

    validation = validate_standards(standards)

    valid_standards = validation["valid"]

    existing, new = check_existing_standards(
        valid_standards
    )

    quality = calculate_dataset_quality(
        valid_standards
    )

    print_report(
        pdf_path=pdf_path,
        records=records,
        standards=standards,
        normalization_errors=normalization_errors,
        validation=validation,
        existing=existing,
        new=new,
        quality=quality,
    )


def run_ingestion(pdf_path):
    """
    Perform the actual MongoDB ingestion.
    """

    print("Starting BIS dataset ingestion...")
    print(f"PDF: {pdf_path}")
    print()
    print(
        "Parsing, normalizing, validating, "
        "chunking and embedding..."
    )
    print()

    result = ingest_dataset_to_chunks(
        str(pdf_path)
    )

    print("=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)

    print(f"Records found:       {result['total']}")
    print(f"Records normalized:  {result['normalized']}")
    print(f"Standards:           {result['standards']}")
    print(f"Total chunks:        {result['chunks']}")

    if result.get("normalizationErrors"):
        print()
        print("Normalization errors:")

        for error in result["normalizationErrors"]:
            print(f"  {error}")

    print()
    print("Chunks per standard:")
    print("-" * 60)

    for item in result["results"]:
        print(
            f"{item['standardNumber']}: "
            f"{item['chunks']} chunks"
        )

    print()
    print(json.dumps(result, indent=2, default=str))


def main():
    parser = argparse.ArgumentParser(
        description=(
            "Parse, validate and ingest a BIS dataset PDF."
        )
    )

    parser.add_argument(
        "pdf_path",
        help="Path to the BIS dataset PDF",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help=(
            "Parse, normalize, validate, score quality "
            "and check duplicates without changing MongoDB."
        ),
    )

    args = parser.parse_args()

    pdf_path = Path(args.pdf_path)

    if not pdf_path.exists():
        print(f"ERROR: File not found: {pdf_path}")
        sys.exit(1)

    if pdf_path.suffix.lower() != ".pdf":
        print("ERROR: Input file must be a PDF.")
        sys.exit(1)

    try:
        if args.dry_run:
            run_dry_run(pdf_path)
        else:
            run_ingestion(pdf_path)

    except Exception as exc:
        print()
        print(f"ERROR: {exc}")
        sys.exit(1)


if __name__ == "__main__":
    main()