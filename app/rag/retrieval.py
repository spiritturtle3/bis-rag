from app.database.mongodb import db
from app.rag.embeddings import EmbeddingModel


chunks_collection = db["chunks"]
embedding_model = EmbeddingModel()


def vector_search(query: str, limit: int = 5) -> list[dict]:
    """
    Find the most semantically relevant chunks for a query.
    """

    query_embedding = embedding_model.embed_text(query)

    pipeline = [
        {
            "$vectorSearch": {
                "index": "embedding_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": max(limit * 10, 50),
                "limit": limit,
            }
        },
        {
            "$project": {
                "_id": 1,
                "standardNumber": 1,
                "source": 1,
                "page": 1,
                "chunkIndex": 1,
                "text": 1,
                "score": {
                    "$meta": "vectorSearchScore"
                }
            }
        }
    ]

    return list(chunks_collection.aggregate(pipeline))