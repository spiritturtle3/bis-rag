from app.database.mongodb import db

standards_collection = db["standards"]


def insert_standard(standard: dict) -> str:
    result = standards_collection.insert_one(standard)
    return str(result.inserted_id)


def get_standard(standard_number: str):
    return standards_collection.find_one(
        {"standardNumber": standard_number}
    )


def upsert_standard(standard: dict) -> str:
    result = standards_collection.update_one(
        {"standardNumber": standard["standardNumber"]},
        {"$set": standard},
        upsert=True,
    )

    if result.upserted_id:
        return str(result.upserted_id)

    existing = get_standard(standard["standardNumber"])
    return str(existing["_id"])


def get_standard_id(standard_number: str) -> str:
    standard = get_standard(standard_number)

    if standard is None:
        raise ValueError(
            f"Standard not found: {standard_number}"
        )

    return str(standard["_id"])