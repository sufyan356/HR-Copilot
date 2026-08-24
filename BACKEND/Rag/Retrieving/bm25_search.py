from typing import List, Dict, Any, Optional

from sqlalchemy.orm import Session
from rank_bm25 import BM25Okapi

from BACKEND.Database.database import session_local
from BACKEND.Models.model import ContextChunks


# ============================================================
# BM25 CONFIGURATION
# ============================================================

BM25_TOP_K = 5


# ============================================================
# GET CHUNKS FROM POSTGRESQL
# ============================================================

def get_chunks_from_postgresql(
    db: Session,
    user_id: Optional[int] = None,
    doc_id: Optional[str] = None,
) -> List[ContextChunks]:
    """
    Fetch chunks from PostgreSQL.

    PostgreSQL is the source of truth for:

        chunk_id
        doc_id
        user_id
        chunk_text
        metadata

    Optional filters:

        user_id
        doc_id
    """

    try:

        query = db.query(ContextChunks)

        # ----------------------------------------------------
        # Filter by user_id if provided
        # ----------------------------------------------------

        if user_id is not None:

            query = query.filter(
                ContextChunks.user_id == user_id
            )

        # ----------------------------------------------------
        # Filter by doc_id if provided
        # ----------------------------------------------------

        if doc_id is not None:

            query = query.filter(
                ContextChunks.doc_id == doc_id
            )

        chunks = query.all()

        return chunks

    except Exception as e:

        raise RuntimeError(
            "Failed to fetch chunks from PostgreSQL: "
            f"{str(e)}"
        ) from e


# ============================================================
# BUILD BM25 INDEX
# ============================================================

def build_bm25_index(
    chunks: List[ContextChunks],
) -> BM25Okapi:
    """
    Build a BM25 index from PostgreSQL chunk text.

    BM25 works with tokens rather than dense vectors.

    Example:

        "Employees receive 20 days annual leave"

    becomes approximately:

        ["employees", "receive", "20", "days",
         "annual", "leave"]
    """

    if not chunks:

        raise ValueError(
            "Cannot build BM25 index because "
            "no chunks were found."
        )

    # --------------------------------------------------------
    # Extract chunk text
    # --------------------------------------------------------

    tokenized_documents = [

        chunk.chunk_text.lower().split()

        for chunk in chunks

    ]

    # --------------------------------------------------------
    # Create BM25 index
    # --------------------------------------------------------

    bm25 = BM25Okapi(
        tokenized_documents
    )

    return bm25


# ============================================================
# BM25 SEARCH
# ============================================================

def bm25_search(
    query: str,
    db: Session,
    top_k: int = BM25_TOP_K,
    user_id: Optional[int] = None,
    doc_id: Optional[str] = None,
) -> List[Dict[str, Any]]:
    """
    Perform BM25 keyword search over PostgreSQL chunks.

    Parameters
    ----------
    query:
        User's search query.

    db:
        SQLAlchemy database session.

    top_k:
        Number of results to return.

    user_id:
        Optional PostgreSQL user filter.

    doc_id:
        Optional document filter.

    Returns
    -------
    List[Dict[str, Any]]

    Example result:

        [
            {
                "chunk_id": "...",
                "doc_id": "...",
                "score": 4.52
            }
        ]

    IMPORTANT:
        BM25 returns chunk IDs and scores.

        Actual chunk text remains in PostgreSQL.
    """

    if not query or not query.strip():

        return []

    # --------------------------------------------------------
    # Validate top_k
    # --------------------------------------------------------

    if top_k <= 0:

        raise ValueError(
            "top_k must be greater than 0."
        )

    # --------------------------------------------------------
    # 1. Fetch chunks from PostgreSQL
    # --------------------------------------------------------

    chunks = get_chunks_from_postgresql(
        db=db,
        user_id=user_id,
        doc_id=doc_id,
    )

    if not chunks:

        print(
            "No PostgreSQL chunks found."
        )

        return []

    print(
        f"PostgreSQL chunks available for BM25: "
        f"{len(chunks)}"
    )

    # --------------------------------------------------------
    # 2. Build BM25 index
    # --------------------------------------------------------

    bm25 = build_bm25_index(
        chunks
    )

    # --------------------------------------------------------
    # 3. Tokenize query
    # --------------------------------------------------------

    tokenized_query = (
        query
        .lower()
        .split()
    )

    # --------------------------------------------------------
    # 4. Calculate BM25 scores
    # --------------------------------------------------------

    scores = bm25.get_scores(
        tokenized_query
    )

    # --------------------------------------------------------
    # 5. Sort indexes by score
    #
    # Highest score first.
    # --------------------------------------------------------

    ranked_indexes = sorted(
        range(len(scores)),
        key=lambda index: scores[index],
        reverse=True,
    )

    # --------------------------------------------------------
    # 6. Select top-k
    # --------------------------------------------------------

    ranked_indexes = ranked_indexes[
        :min(top_k, len(ranked_indexes))
    ]

    # --------------------------------------------------------
    # 7. Build results
    # --------------------------------------------------------

    results = []

    for index in ranked_indexes:

        chunk = chunks[index]

        result = {

            "chunk_id": chunk.chunk_id,

            "doc_id": chunk.doc_id,

            "score": float(
                scores[index]
            ),

        }

        results.append(
            result
        )

    return results


# ============================================================
# PRINT BM25 RESULTS
# ============================================================

def print_bm25_results(
    results: List[Dict[str, Any]],
) -> None:
    """
    Print BM25 search results.
    """

    print("\n" + "=" * 70)
    print("BM25 SEARCH RESULTS")
    print("=" * 70)

    print(
        f"Results returned: "
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
            f"{result['chunk_id']}"
        )

        print(
            f"doc_id:   "
            f"{result['doc_id']}"
        )

        print(
            f"score:    "
            f"{result['score']}"
        )


# ============================================================
# MAIN TEST
# ============================================================

# def main():

#     print("\n" + "=" * 70)
#     print("BM25 POSTGRESQL SEARCH TEST")
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

#     db = session_local()

#     try:

#         # ----------------------------------------------------
#         # Perform BM25 search
#         # ----------------------------------------------------

#         results = bm25_search(
#             query=query,
#             db=db,
#             top_k=5,
#         )

#         # ----------------------------------------------------
#         # Print results
#         # ----------------------------------------------------

#         print_bm25_results(
#             results
#         )

#         # ----------------------------------------------------
#         # Summary
#         # ----------------------------------------------------

#         print("\n" + "=" * 70)
#         print("SEARCH SUMMARY")
#         print("=" * 70)

#         print(
#             f"Query: {query}"
#         )

#         print(
#             f"Results returned: "
#             f"{len(results)}"
#         )

#         print("\nChunk IDs:")

#         for result in results:

#             print(
#                 f"  {result['chunk_id']}"
#             )

#         print("\nBM25 search test completed successfully.")

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