from app.database.mongodb import db


chunks_collection = db["chunks"]


def insert_chunk(chunk: dict) -> str:
    """
    Insert a single RAG chunk into MongoDB.
    """
    result = chunks_collection.insert_one(chunk)
    return str(result.inserted_id)