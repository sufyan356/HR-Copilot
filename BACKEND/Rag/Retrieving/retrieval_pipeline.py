from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from BACKEND.Rag.Retrieving.hybrid_search import (
    hybrid_search,
)

from BACKEND.Rag.Retrieving.reranker import (
    rerank_results,
)


# ============================================================
# RETRIEVAL CONFIGURATION
# ============================================================

QDRANT_TOP_K = 5
BM25_TOP_K = 5

RERANKER_TOP_K = 5


# ============================================================
# RETRIEVAL PIPELINE
# ============================================================

def retrieval_pipeline(
    query: str,
    db: Session,
    qdrant_top_k: int = QDRANT_TOP_K,
    bm25_top_k: int = BM25_TOP_K,
    reranker_top_k: int = RERANKER_TOP_K,
    user_id: Optional[int] = None,
    doc_id: Optional[str] = None,
) -> List[Dict[str, Any]]:


    # ========================================================
    # VALIDATE QUERY
    # ========================================================

    if not query or not query.strip():

        return []

    query = query.strip()

    # ========================================================
    # PIPELINE START
    # ========================================================

    print("\n" + "=" * 70)
    print("RETRIEVAL PIPELINE")
    print("=" * 70)

    print(
        f"\nQuery: {query}"
    )

    # ========================================================
    # STEP 1
    # HYBRID SEARCH
    # ========================================================

    print("\n" + "-" * 70)
    print("STEP 1: HYBRID RETRIEVAL")
    print("-" * 70)

    hybrid_results = hybrid_search(
        query=query,
        db=db,
        qdrant_top_k=qdrant_top_k,
        bm25_top_k=bm25_top_k,
        user_id=user_id,
        doc_id=doc_id,
    )

    print(
        f"Hybrid candidates: "
        f"{len(hybrid_results)}"
    )

    # ========================================================
    # NO RESULTS
    # ========================================================

    if not hybrid_results:

        print(
            "\nNo hybrid candidates found."
        )

        return []

    # ========================================================
    # STEP 2
    # CROSS-ENCODER RERANKING
    # ========================================================

    print("\n" + "-" * 70)
    print("STEP 2: CROSS-ENCODER RERANKING")
    print("-" * 70)

    reranked_results = rerank_results(
        query=query,
        candidates=hybrid_results,
        top_k=reranker_top_k,
    )

    print(
        f"Final reranked results: "
        f"{len(reranked_results)}"
    )

    # ========================================================
    # STEP 3
    # FINAL RESULTS
    # ========================================================

    print("\n" + "=" * 70)
    print("RETRIEVAL PIPELINE RESULTS")
    print("=" * 70)

    for number, result in enumerate(
        reranked_results,
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
            f"doc_id: "
            f"{result.get('doc_id')}"
        )

        print(
            f"rerank_score: "
            f"{result.get('rerank_score')}"
        )

        print(
            f"source: "
            f"{result.get('source')}"
        )

        print(
            f"file_name: "
            f"{result.get('file_name')}"
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
                ""
            )
        )

    return reranked_results


# ============================================================
# MAIN TEST
# ============================================================

# def main():

#     print("\n" + "=" * 70)
#     print("RETRIEVAL PIPELINE TEST")
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
#     # Create database session
#     # --------------------------------------------------------

#     from BACKEND.Database.database import (
#         session_local,
#     )

#     db = session_local()

#     try:

#         # ----------------------------------------------------
#         # Run complete retrieval pipeline
#         # ----------------------------------------------------

#         results = retrieval_pipeline(
#             query=query,
#             db=db,
#             qdrant_top_k=5,
#             bm25_top_k=5,
#             reranker_top_k=5,
#         )

#         # ----------------------------------------------------
#         # Summary
#         # ----------------------------------------------------

#         print("\n" + "=" * 70)
#         print("RETRIEVAL PIPELINE SUMMARY")
#         print("=" * 70)

#         print(
#             f"Query: "
#             f"{query}"
#         )

#         print(
#             f"Qdrant Top-K: "
#             f"5"
#         )

#         print(
#             f"BM25 Top-K: "
#             f"5"
#         )

#         print(
#             f"Final Reranker Top-K: "
#             f"5"
#         )

#         print(
#             f"Final results: "
#             f"{len(results)}"
#         )

#         print("\nFinal Chunk IDs:")

#         for number, result in enumerate(
#             results,
#             start=1,
#         ):

#             print(
#                 f"  #{number} "
#                 f"{result.get('chunk_id')}"
#             )

#         print(
#             "\nRetrieval pipeline test "
#             "completed successfully."
#         )

#     finally:

#         # ----------------------------------------------------
#         # Close database session
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