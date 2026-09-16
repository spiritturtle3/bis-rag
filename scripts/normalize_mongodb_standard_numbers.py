import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.database.mongodb import db
from app.ingestion.standard_normalizer import normalize_standard_number


def main():
    standards = db["standards"]
    chunks = db["chunks"]

    standard_updates = 0
    chunk_updates = 0

    for document in standards.find({}, {"_id": 1, "standardNumber": 1}):
        old_number = document.get("standardNumber")

        if not old_number:
            continue

        new_number = normalize_standard_number(old_number)

        if old_number != new_number:
            standards.update_one(
                {"_id": document["_id"]},
                {"$set": {"standardNumber": new_number}},
            )
            standard_updates += 1

            result = chunks.update_many(
                {"standardNumber": old_number},
                {"$set": {"standardNumber": new_number}},
            )

            chunk_updates += result.modified_count

            print(f"{old_number} -> {new_number}")
            print(f"  chunks updated: {result.modified_count}")

    print()
    print(f"Standards updated: {standard_updates}")
    print(f"Chunks updated: {chunk_updates}")


if __name__ == "__main__":
    main()