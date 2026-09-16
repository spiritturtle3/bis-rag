import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from app.rag.retrieval import vector_search
from app.rag.hybrid_search import hybrid_search


QUERY = "precast concrete pipes for drainage systems"


def print_results(title, results, score_field):
    print()
    print("=" * 70)
    print(title)
    print("=" * 70)

    for index, result in enumerate(results, start=1):
        text = result["text"].replace("\n", " ")

        print(f"{index}. {result['standardNumber']}")
        print(f"   Score: {result[score_field]:.6f}")
        print(f"   Text: {text[:300]}")
        print()


def main():
    vector_results = vector_search(QUERY, 5)

    print_results(
        "VECTOR SEARCH",
        vector_results,
        "score",
    )

    hybrid_results = hybrid_search(QUERY, 5)

    print_results(
        "HYBRID SEARCH",
        hybrid_results,
        "hybridScore",
    )


if __name__ == "__main__":
    main()