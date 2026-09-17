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

    Deduplicate by standardNumber and keep the
    highest-scoring chunk for each standard.
    """

    import time
    from concurrent.futures import ThreadPoolExecutor

    start = time.perf_counter()

    # Retrieve extra chunks so deduplication does not
    # reduce the final result set too aggressively.
    retrieval_limit = max(limit * 3, 10)

    with ThreadPoolExecutor(max_workers=2) as executor:
        vector_future = executor.submit(
            vector_search,
            query,
            retrieval_limit
        )
        keyword_future = executor.submit(
            keyword_search,
            query,
            retrieval_limit
        )

        vector_results = vector_future.result()
        keyword_results = keyword_future.result()

    print(
        f"TIMING parallel retrieval: "
        f"{time.perf_counter() - start:.3f}s"
    )

    scores = {}
    documents = {}

    for rank, document in enumerate(vector_results, start=1):
        key = str(document["_id"])

        scores[key] = (
            scores.get(key, 0)
            + 1 / (60 + rank)
        )

        documents[key] = document

    for rank, document in enumerate(keyword_results, start=1):
        key = str(document["_id"])

        scores[key] = (
            scores.get(key, 0)
            + 1 / (60 + rank)
        )

        documents[key] = document

    ranked_chunks = sorted(
        documents,
        key=lambda key: scores[key],
        reverse=True
    )

    # Keep only the strongest chunk for each standard.
    best_by_standard = {}

    for key in ranked_chunks:
        document = documents[key]
        standard_number = document.get("standardNumber")

        if not standard_number:
            continue

        if standard_number not in best_by_standard:
            result = document.copy()
            result["hybridScore"] = scores[key]
            best_by_standard[standard_number] = result

    return list(best_by_standard.values())[:limit]