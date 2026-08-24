from typing import List, Dict, Any

from qdrant_client import models

from BACKEND.Config.qdrant_index import (
    get_qdrant_collection,
    QDRANT_COLLECTION_NAME,
    QDRANT_DENSE_NAME,
)

from BACKEND.Rag.Indexing.embeddings import embed_query


# ============================================================
# CONFIGURATION
# ============================================================

QDRANT_TOP_K = 5


# ============================================================
# QDRANT DENSE SEARCH
# ============================================================

def qdrant_search(
    query: str,
    top_k: int = QDRANT_TOP_K,
    user_id: int | None = None,
    doc_id: str | None = None,
) -> List[Dict[str, Any]]:
    """
    Perform dense vector similarity search in Qdrant.

    Qdrant stores:
        - dense vector
        - chunk_id
        - doc_id
        - metadata

    Qdrant does NOT store:
        - chunk_text

    The chunk_id returned by Qdrant will later be used
    to retrieve the actual chunk_text from PostgreSQL.

    Optional filters:
        user_id
        doc_id
    """

    # ========================================================
    # VALIDATION
    # ========================================================

    if not query or not query.strip():
        return []

    if top_k <= 0:
        raise ValueError(
            "top_k must be greater than 0."
        )

    try:

        # ====================================================
        # 1. CREATE QUERY EMBEDDING
        # ====================================================

        query_embedding = embed_query(query)

        print(
            f"Query embedding dimension: "
            f"{len(query_embedding)}"
        )

        # ====================================================
        # 2. GET QDRANT CLIENT
        # ====================================================

        client = get_qdrant_collection()

        # ====================================================
        # 3. BUILD OPTIONAL FILTER
        # ====================================================

        filter_conditions = []

        # ----------------------------------------------------
        # USER ID FILTER
        # ----------------------------------------------------

        if user_id is not None:

            filter_conditions.append(
                models.FieldCondition(
                    key="user_id",
                    match=models.MatchValue(
                        value=user_id
                    ),
                )
            )

        # ----------------------------------------------------
        # DOCUMENT ID FILTER
        # ----------------------------------------------------

        if doc_id is not None:

            filter_conditions.append(
                models.FieldCondition(
                    key="doc_id",
                    match=models.MatchValue(
                        value=doc_id
                    ),
                )
            )

        # ----------------------------------------------------
        # CREATE FILTER
        # ----------------------------------------------------

        query_filter = None

        if filter_conditions:

            query_filter = models.Filter(
                must=filter_conditions
            )

        # ====================================================
        # 4. SEARCH QDRANT
        # ====================================================

        print("\nSearching Qdrant...")

        search_result = client.query_points(

            collection_name=QDRANT_COLLECTION_NAME,

            query=query_embedding,

            using=QDRANT_DENSE_NAME,

            limit=top_k,

            query_filter=query_filter,

            with_payload=True,

            with_vectors=False,
        )

        points = search_result.points

        # ====================================================
        # 5. FORMAT RESULTS
        # ====================================================

        results = []

        for point in points:

            payload = point.payload or {}

            result = {
                "chunk_id": payload.get(
                    "chunk_id"
                ),

                "doc_id": payload.get(
                    "doc_id"
                ),

                "user_id": payload.get(
                    "user_id"
                ),

                "source": payload.get(
                    "source"
                ),

                "file_name": payload.get(
                    "file_name"
                ),

                "file_type": payload.get(
                    "file_type"
                ),

                "page_number": payload.get(
                    "page_number"
                ),

                "row_number": payload.get(
                    "row_number"
                ),

                "score": point.score,
            }

            results.append(result)

        # ====================================================
        # 6. PRINT RESULTS
        # ====================================================

        print(
            f"Qdrant results: "
            f"{len(results)}"
        )

        for number, result in enumerate(
            results,
            start=1,
        ):

            print("\n" + "-" * 60)

            print(
                f"Result #{number}"
            )

            print(
                f"chunk_id: "
                f"{result['chunk_id']}"
            )

            print(
                f"doc_id: "
                f"{result['doc_id']}"
            )

            print(
                f"user_id: "
                f"{result['user_id']}"
            )

            print(
                f"file_name: "
                f"{result['file_name']}"
            )

            print(
                f"page_number: "
                f"{result['page_number']}"
            )

            print(
                f"row_number: "
                f"{result['row_number']}"
            )

            print(
                f"score: "
                f"{result['score']}"
            )

        return results

    except Exception as e:

        raise RuntimeError(
            "Qdrant dense search failed: "
            f"{str(e)}"
        ) from e


# ============================================================
# MAIN TEST
# ============================================================

# def main():

#     print("\n" + "=" * 70)
#     print("QDRANT DENSE SEARCH TEST")
#     print("=" * 70)

#     # ========================================================
#     # TEST QUERY
#     # ========================================================

#     query = (
#         "How many annual leave days "
#         "do employees receive?"
#     )

#     print(
#         f"\nQuery: {query}"
#     )

#     # ========================================================
#     # SEARCH ONCE
#     # ========================================================

#     results = qdrant_search(
#         query=query,
#         top_k=5,
#     )

#     # ========================================================
#     # SUMMARY
#     # ========================================================

#     print("\n" + "=" * 70)
#     print("SEARCH SUMMARY")
#     print("=" * 70)

#     print(
#         f"Results returned: "
#         f"{len(results)}"
#     )

#     print("\nChunk IDs:")

#     for result in results:

#         print(
#             f"  {result['chunk_id']}"
#         )

#     print(
#         "\nQdrant search test completed successfully."
#     )


# # ============================================================
# # ENTRY POINT
# # ============================================================

# if __name__ == "__main__":

#     main()