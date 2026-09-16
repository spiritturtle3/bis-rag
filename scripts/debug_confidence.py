from app.rag.query_translator import translate_query
from app.rag.hybrid_search import hybrid_search
from app.rag.ranker import rank_standards
from app.rag.confidence import calculate_confidence


queries = [
    "precast concrete pipes",
    "reinforced concrete water tank",
    "पानी की टंकी के लिए प्रबलित कंक्रीट",
    "laptop computer with 16 GB RAM",
]


for query in queries:
    print("\n" + "=" * 80)
    print(f"QUERY: {query}")

    search_query = translate_query(query)

    print(f"SEARCH QUERY: {search_query}")

    results = hybrid_search(
        search_query,
        limit=15,
    )

    print(f"RETRIEVED CHUNKS: {len(results)}")

    ranked = rank_standards(
        search_query,
        results,
        limit=10,
    )

    print("\nRANKED RESULTS:")

    for index, result in enumerate(ranked, start=1):
        confidence = calculate_confidence(result)

        print(
            f"\n#{index}"
            f"\n  Standard: {result.get('standardNumber')}"
            f"\n  Score: {result.get('score')}"
            f"\n  Ranking score: {result.get('rankingScore')}"
            f"\n  Matched chunks: {result.get('matchedChunks')}"
            f"\n  Confidence: {confidence}"
        )