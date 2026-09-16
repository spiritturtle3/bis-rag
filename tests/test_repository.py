from app.database.repository import insert_chunk


def test_insert_chunk():
    chunk = {
        "standardNumber": "TEST-001",
        "page": 1,
        "text": "Steel pipes shall meet the specified requirements.",
        "embedding": [0.1, 0.2, 0.3],
    }

    inserted_id = insert_chunk(chunk)

    assert inserted_id is not None