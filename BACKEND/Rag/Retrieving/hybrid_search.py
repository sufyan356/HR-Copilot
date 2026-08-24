from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session

from BACKEND.Rag.Retrieving.qdrant_search import (
    qdrant_search,
)

from BACKEND.Rag.Retrieving.bm25_search import (
    bm25_search,
)

from BACKEND.Models.model import ContextChunks


# ============================================================
# HYBRID SEARCH CONFIGURATION
# ============================================================

QDRANT_TOP_K = 5
BM25_TOP_K = 5


# ============================================================
# COMBINE RESULTS
# ============================================================

def combine_results(
    qdrant_results: List[Dict[str, Any]],
    bm25_results: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    Combine Qdrant and BM25 results.

    Duplicate chunks are removed using chunk_id.

    Qdrant results are added first.
    BM25 results are then added if their chunk_id
    does not already exist.

    No score fusion is performed here.

    The actual chunk text is NOT taken from Qdrant.

    It will be fetched from PostgreSQL after
    deduplication.
    """

    combined_results = []

    seen_chunk_ids = set()

    # --------------------------------------------------------
    # Add Qdrant results
    # --------------------------------------------------------

    for result in qdrant_results:

        chunk_id = result.get("chunk_id")

        if not chunk_id:
            continue

        if chunk_id in seen_chunk_ids:
            continue

        seen_chunk_ids.add(chunk_id)

        combined_results.append(
            {
                "chunk_id": chunk_id,
                "doc_id": result.get("doc_id"),
                "source": "qdrant",
                "score": result.get("score"),
            }
        )

    # --------------------------------------------------------
    # Add BM25 results
    # --------------------------------------------------------

    for result in bm25_results:

        chunk_id = result.get("chunk_id")

        if not chunk_id:
            continue

        if chunk_id in seen_chunk_ids:
            continue

        seen_chunk_ids.add(chunk_id)

        combined_results.append(
            {
                "chunk_id": chunk_id,
                "doc_id": result.get("doc_id"),
                "source": "bm25",
                "score": result.get("score"),
            }
        )

    return combined_results


# ============================================================
# FETCH CHUNK TEXT FROM POSTGRESQL
# ============================================================

def attach_chunk_text(
    results: List[Dict[str, Any]],
    db: Session,
    user_id: Optional[int] = None,
    doc_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Fetch chunk text and metadata from PostgreSQL
    using chunk_id.

    Qdrant does NOT store chunk_text.

    PostgreSQL is the source of truth for:

        chunk_text
        chunk_id
        doc_id
        user_id
        source
        file_name
        file_type
        page_number
        row_number

    Only chunks already returned by the hybrid
    retrieval stage are fetched.
    """

    if not results:

        return []

    # --------------------------------------------------------
    # Extract chunk IDs
    # --------------------------------------------------------

    chunk_ids = [
        result["chunk_id"]
        for result in results
        if result.get("chunk_id")
    ]

    if not chunk_ids:

        return []

    # --------------------------------------------------------
    # PostgreSQL query
    # --------------------------------------------------------

    query = (
        db.query(ContextChunks)
        .filter(
            ContextChunks.chunk_id.in_(
                chunk_ids
            )
        )
    )

    # --------------------------------------------------------
    # Optional user filter
    # --------------------------------------------------------

    if user_id is not None:

        query = query.filter(
            ContextChunks.user_id == user_id
        )

    # --------------------------------------------------------
    # Optional document filter
    # --------------------------------------------------------

    if doc_id is not None:

        query = query.filter(
            ContextChunks.doc_id == doc_id
        )

    chunks = query.all()

    # --------------------------------------------------------
    # Create lookup dictionary
    # --------------------------------------------------------

    chunk_lookup = {
        chunk.chunk_id: chunk
        for chunk in chunks
    }

    # --------------------------------------------------------
    # Attach PostgreSQL data
    # --------------------------------------------------------

    enriched_results = []

    for result in results:

        chunk_id = result.get(
            "chunk_id"
        )

        chunk = chunk_lookup.get(
            chunk_id
        )

        # ----------------------------------------------------
        # Skip result if PostgreSQL record does not exist
        # ----------------------------------------------------

        if chunk is None:

            continue

        enriched_result = result.copy()

        # ----------------------------------------------------
        # PostgreSQL chunk text
        # ----------------------------------------------------

        enriched_result[
            "chunk_text"
        ] = chunk.chunk_text

        # ----------------------------------------------------
        # Metadata
        # ----------------------------------------------------

        enriched_result[
            "doc_id"
        ] = chunk.doc_id

        enriched_result[
            "user_id"
        ] = chunk.user_id

        enriched_result[
            "source"
        ] = chunk.source

        enriched_result[
            "file_name"
        ] = chunk.file_name

        enriched_result[
            "file_type"
        ] = chunk.file_type

        enriched_result[
            "page_number"
        ] = chunk.page_number

        enriched_result[
            "row_number"
        ] = chunk.row_number

        enriched_results.append(
            enriched_result
        )

    return enriched_results


# ============================================================
# HYBRID SEARCH
# ============================================================

def hybrid_search(
    query: str,
    db: Session,
    qdrant_top_k: int = QDRANT_TOP_K,
    bm25_top_k: int = BM25_TOP_K,
    user_id: Optional[int] = None,
    doc_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Perform hybrid retrieval.

    Retrieval flow:

        User Query
             |
             +--------------------+
             |                    |
             v                    v
         Qdrant                BM25
         Dense                 Keyword
             |                    |
          Top-K                 Top-K
             |                    |
             +---------+----------+
                       |
                       v
                  Combine
                       |
                       v
                 Deduplicate
                       |
                       v
              PostgreSQL lookup
                  by chunk_id
                       |
                       v
              Attach chunk_text
                       |
                       v
                 Final candidates

    The returned candidates can then be passed
    to the CrossEncoder reranker.

    Parameters
    ----------
    query:
        User query.

    db:
        SQLAlchemy database session.

    qdrant_top_k:
        Number of Qdrant results.

    bm25_top_k:
        Number of BM25 results.

    user_id:
        Optional user filter.

    doc_id:
        Optional document filter.

    Returns
    -------
    List[Dict[str, Any]]
        Hybrid candidates containing chunk_text
        fetched from PostgreSQL.
    """

    if not query or not query.strip():

        return []

    # ========================================================
    # 1. QDRANT DENSE SEARCH
    # ========================================================

    print("\n" + "-" * 70)
    print("RUNNING QDRANT DENSE SEARCH")
    print("-" * 70)

    qdrant_results = qdrant_search(
        query=query,
        top_k=qdrant_top_k,
        user_id=user_id,
        doc_id=doc_id,
    )

    print(
        f"Qdrant results: "
        f"{len(qdrant_results)}"
    )

    # ========================================================
    # 2. BM25 SEARCH
    # ========================================================

    print("\n" + "-" * 70)
    print("RUNNING BM25 SEARCH")
    print("-" * 70)

    bm25_results = bm25_search(
        query=query,
        db=db,
        top_k=bm25_top_k,
        user_id=user_id,
        doc_id=doc_id,
    )

    print(
        f"BM25 results: "
        f"{len(bm25_results)}"
    )

    # ========================================================
    # 3. COMBINE + DEDUPLICATE
    # ========================================================

    print("\n" + "-" * 70)
    print("COMBINING RESULTS")
    print("-" * 70)

    hybrid_results = combine_results(
        qdrant_results=qdrant_results,
        bm25_results=bm25_results,
    )

    print(
        f"Unique hybrid candidates: "
        f"{len(hybrid_results)}"
    )

    # ========================================================
    # 4. FETCH CHUNK TEXT FROM POSTGRESQL
    # ========================================================

    print("\n" + "-" * 70)
    print(
        "FETCHING CHUNK TEXT FROM POSTGRESQL"
    )
    print("-" * 70)

    enriched_results = attach_chunk_text(
        results=hybrid_results,
        db=db,
        user_id=user_id,
        doc_id=doc_id,
    )

    print(
        f"Chunks enriched from PostgreSQL: "
        f"{len(enriched_results)}"
    )

    return enriched_results


# ============================================================
# PRINT HYBRID RESULTS
# ============================================================

def print_hybrid_results(
    results: List[Dict[str, Any]],
) -> None:
    """
    Print hybrid retrieval results.

    Chunk text is included because it is fetched
    from PostgreSQL.
    """

    print("\n" + "=" * 70)
    print("HYBRID SEARCH RESULTS")
    print("=" * 70)

    print(
        f"Unique candidates: "
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
            f"score:    "
            f"{result.get('score')}"
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

        print("\nChunk text:")

        print(
            result.get(
                "chunk_text",
                ""
            )
        )


# ============================================================
# MAIN TEST
# ============================================================

# def main():

#     print("\n" + "=" * 70)
#     print("HYBRID SEARCH TEST")
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
#         session_local
#     )

#     db = session_local()

#     try:

#         # ----------------------------------------------------
#         # Hybrid search
#         # ----------------------------------------------------

#         results = hybrid_search(
#             query=query,
#             db=db,
#             qdrant_top_k=5,
#             bm25_top_k=5,
#         )

#         # ----------------------------------------------------
#         # Print results
#         # ----------------------------------------------------

#         print_hybrid_results(
#             results
#         )

#         # ----------------------------------------------------
#         # Summary
#         # ----------------------------------------------------

#         print("\n" + "=" * 70)
#         print("HYBRID SEARCH SUMMARY")
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
#             f"Unique candidates: "
#             f"{len(results)}"
#         )

#         print(
#             f"PostgreSQL enriched: "
#             f"{len(results)}"
#         )

#         print("\nChunk IDs:")

#         for result in results:

#             print(
#                 f"  {result['chunk_id']} "
#                 f"({result['source']})"
#             )

#         print(
#             "\nHybrid search test completed successfully."
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