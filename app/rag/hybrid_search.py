from app.database.mongodb import db
from app.rag.embeddings import EmbeddingModel
from app.rag.retrieval import vector_search


chunks_collection = db["chunks"]
embedding_model = EmbeddingModel()


def keyword_search(query: str, limit: int = 5) -> list[dict]:
    """
    Search chunks using keyword/full-text matching.
    """

    pipeline = [
        {
            "$search": {
                "index": "text_search_index",
                "text": {
                    "query": query,
                    "path": "text"
                }
            }
        },
        {
            "$limit": limit
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
                    "$meta": "searchScore"
                }
            }
        }
    ]

    return list(chunks_collection.aggregate(pipeline))


def hybrid_search(query: str, limit: int = 5) -> list[dict]:
    """
    Combine vector and keyword retrieval using
    Reciprocal Rank Fusion (RRF).
    """

    vector_results = vector_search(query, limit=limit)
    keyword_results = keyword_search(query, limit=limit)

    scores = {}
    documents = {}

    # Vector ranking
    for rank, document in enumerate(vector_results, start=1):
        key = str(document["_id"])

        documents[key] = document
        scores[key] = scores.get(key, 0) + 1 / (60 + rank)

    # Keyword ranking
    for rank, document in enumerate(keyword_results, start=1):
        key = str(document["_id"])

        documents[key] = document
        scores[key] = scores.get(key, 0) + 1 / (60 + rank)

    # Sort by combined RRF score
    ranked = sorted(
        documents,
        key=lambda key: scores[key],
        reverse=True
    )

    results = []

    for key in ranked[:limit]:
        document = documents[key].copy()
        document["hybridScore"] = scores[key]
        results.append(document)

    return results