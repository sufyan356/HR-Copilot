from typing import List, Dict, Any

from BACKEND.Config.reranker_model import (
    get_reranker,
)


# ============================================================
# RERANKER CONFIGURATION
# ============================================================

DEFAULT_TOP_K = 5


# ============================================================
# RERANK CANDIDATES
# ============================================================

def rerank_results(
    query: str,
    candidates: List[Dict[str, Any]],
    top_k: int = DEFAULT_TOP_K,
) -> List[Dict[str, Any]]:
    """
    Rerank hybrid search candidates using a CrossEncoder.

    The CrossEncoder receives:

        query + chunk_text

    and produces a relevance score.

    Parameters
    ----------
    query:
        User's search query.

    candidates:
        Candidates returned by hybrid_search().
        Each candidate must contain:
            - chunk_id
            - chunk_text

    top_k:
        Number of final results to return.

    Returns
    -------
    List[Dict[str, Any]]
        Reranked top-k candidates.
    """

    # ========================================================
    # VALIDATION
    # ========================================================

    if not query or not query.strip():
        return []

    if not candidates:
        return []

    if top_k <= 0:
        return []

    # ========================================================
    # GET CACHED RERANKER
    # ========================================================

    reranker = get_reranker()

    # ========================================================
    # PREPARE QUERY + CHUNK TEXT PAIRS
    # ========================================================

    pairs = []

    valid_candidates = []

    for candidate in candidates:

        chunk_text = candidate.get("chunk_text")

        if not chunk_text:
            continue

        pairs.append(
            [
                query,
                chunk_text,
            ]
        )

        valid_candidates.append(candidate)

    if not pairs:
        return []

    # ========================================================
    # GENERATE CROSS-ENCODER SCORES
    # ========================================================

    print("\n" + "-" * 70)
    print("RUNNING CROSS-ENCODER RERANKER")
    print("-" * 70)

    print(
        f"Candidates received: "
        f"{len(valid_candidates)}"
    )

    print(
        "Generating reranker scores..."
    )

    scores = reranker.predict(
        pairs
    )

    # ========================================================
    # ATTACH RERANKER SCORE
    # ========================================================

    reranked_results = []

    for candidate, score in zip(
        valid_candidates,
        scores,
    ):

        result = dict(candidate)

        result["rerank_score"] = float(
            score
        )

        reranked_results.append(
            result
        )

    # ========================================================
    # SORT BY RERANKER SCORE
    # ========================================================

    reranked_results.sort(
        key=lambda item: item["rerank_score"],
        reverse=True,
    )

    # ========================================================
    # RETURN TOP-K
    # ========================================================

    final_results = reranked_results[
        :top_k
    ]

    print(
        f"Reranked results: "
        f"{len(final_results)}"
    )

    return final_results


# ============================================================
# PRINT RERANKED RESULTS
# ============================================================

def print_reranked_results(
    results: List[Dict[str, Any]],
) -> None:
    """
    Print final reranked results.
    """

    print("\n" + "=" * 70)
    print("RERANKED RESULTS")
    print("=" * 70)

    print(
        f"Final results: "
        f"{len(results)}"
    )

    for number, result in enumerate(
        results,
        start=1,
    ):

        print("\n" + "-" * 70)

        print(
            f"#{number}"
        )

        print(
            f"chunk_id: "
            f"{result.get('chunk_id')}"
        )

        print(
            f"doc_id:   "
            f"{result.get('doc_id')}"
        )

        print(
            f"source:   "
            f"{result.get('source')}"
        )

        print(
            f"rerank_score: "
            f"{result.get('rerank_score')}"
        )

        print(
            f"user_id:  "
            f"{result.get('user_id')}"
        )

        print(
            f"file_name: "
            f"{result.get('file_name')}"
        )

        print(
            f"file_type: "
            f"{result.get('file_type')}"
        )

        print(
            f"page_number: "
            f"{result.get('page_number')}"
        )

        print(
            f"row_number: "
            f"{result.get('row_number')}"
        )

        print(
            "\nChunk text:"
        )

        print(
            result.get(
                "chunk_text",
                "",
            )
        )


# ============================================================
# MAIN TEST
# ============================================================

# def main():

#     print("\n" + "=" * 70)
#     print("RERANKER TEST")
#     print("=" * 70)

#     # --------------------------------------------------------
#     # Test query
#     # --------------------------------------------------------

#     query = (
#         "How many annual leave days "
#         "do employees receive?"
#     )

#     print(
#         f"\nQuery: {query}"
#     )

#     # --------------------------------------------------------
#     # Import database session
#     # --------------------------------------------------------

#     from BACKEND.Database.database import (
#         session_local,
#     )

#     # --------------------------------------------------------
#     # Import hybrid search
#     # --------------------------------------------------------

#     from BACKEND.Rag.Retrieving.hybrid_search import (
#         hybrid_search,
#     )

#     # --------------------------------------------------------
#     # Create database session
#     # --------------------------------------------------------

#     db = session_local()

#     try:

#         # ====================================================
#         # 1. HYBRID SEARCH
#         # ====================================================

#         print("\n" + "-" * 70)
#         print("RUNNING HYBRID SEARCH")
#         print("-" * 70)

#         hybrid_results = hybrid_search(
#             query=query,
#             db=db,
#             qdrant_top_k=5,
#             bm25_top_k=5,
#         )

#         print(
#             f"Hybrid candidates: "
#             f"{len(hybrid_results)}"
#         )

#         # ====================================================
#         # 2. RERANK
#         # ====================================================

#         results = rerank_results(
#             query=query,
#             candidates=hybrid_results,
#             top_k=5,
#         )

#         # ====================================================
#         # 3. PRINT RESULTS
#         # ====================================================

#         print_reranked_results(
#             results
#         )

#         # ====================================================
#         # SUMMARY
#         # ====================================================

#         print("\n" + "=" * 70)
#         print("RERANKER SUMMARY")
#         print("=" * 70)

#         print(
#             f"Query: {query}"
#         )

#         print(
#             f"Hybrid candidates: "
#             f"{len(hybrid_results)}"
#         )

#         print(
#             f"Final Top-K: "
#             f"{len(results)}"
#         )

#         print("\nFinal ranking:")

#         for number, result in enumerate(
#             results,
#             start=1,
#         ):

#             print(
#                 f"  #{number} "
#                 f"{result.get('chunk_id')} "
#                 f"-> "
#                 f"{result.get('rerank_score')}"
#             )

#         print(
#             "\nReranker test completed successfully."
#         )

#     finally:

#         # ----------------------------------------------------
#         # Close database connection
#         # ----------------------------------------------------

#         db.close()

#         print(
#             "\nDatabase connection closed."
#         )


# # ============================================================
# # ENTRY POINT
# # ============================================================

# if __name__ == "__main__":
#     main()