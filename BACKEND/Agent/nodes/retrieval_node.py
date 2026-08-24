from typing import Any, Dict

from sqlalchemy.orm import Session

from BACKEND.Rag.Retrieving.retrieval_pipeline import (
    retrieval_pipeline,
)


# ============================================================
# RETRIEVAL NODE
# ============================================================

def retrieval_node(
    state: Dict[str, Any],
    db: Session,
) -> Dict[str, Any]:
    """
    LangGraph retrieval node.

    Flow:

        user query
             ↓
        retrieval_pipeline()
             ↓
        hybrid retrieval
             ↓
        CrossEncoder reranking
             ↓
        final retrieval_results
             ↓
        build context from chunk_text

    The node returns both:

        retrieval_results
        context

    The database session is passed into the node instead of
    storing it inside the LangGraph state.
    """

    # ========================================================
    # GET QUERY
    # ========================================================

    query = state.get("query", "")

    if not query or not query.strip():
        return {
            "retrieval_results": [],
            "context": "",
        }

    print("\n" + "=" * 70)
    print("LANGGRAPH RETRIEVAL NODE")
    print("=" * 70)

    print(
        f"\nQuery: {query}"
    )

    # ========================================================
    # RUN RETRIEVAL PIPELINE
    # ========================================================

    print("\n" + "-" * 70)
    print("RUNNING RETRIEVAL PIPELINE")
    print("-" * 70)

    retrieval_results = retrieval_pipeline(
        query=query,
        db=db,
    )

    print(
        f"Retrieved results: "
        f"{len(retrieval_results)}"
    )

    # ========================================================
    # BUILD CONTEXT
    # ========================================================
    #
    # Extract chunk_text from the final reranked results.
    #
    # retrieval_results:
    #
    # [
    #     {
    #         "chunk_id": "...",
    #         "chunk_text": "...",
    #         "rerank_score": 7.98,
    #         ...
    #     }
    # ]
    #
    # becomes:
    #
    # context:
    #
    # "chunk text 1
    #
    #  chunk text 2
    #
    #  chunk text 3"
    #
    # ========================================================

    context_parts = []

    for result in retrieval_results:

        chunk_text = result.get(
            "chunk_text"
        )

        if not chunk_text:
            continue

        context_parts.append(
            chunk_text.strip()
        )

    context = "\n\n".join(
        context_parts
    )

    # ========================================================
    # PRINT CONTEXT INFORMATION
    # ========================================================

    print("\n" + "-" * 70)
    print("CONTEXT CREATED")
    print("-" * 70)

    print(
        f"Context chunks: "
        f"{len(context_parts)}"
    )

    print(
        f"Context characters: "
        f"{len(context)}"
    )

    # ========================================================
    # RETURN UPDATED STATE
    # ========================================================

    return {
        "retrieval_results": retrieval_results,
        "context": context,
    }
    
    
# ============================================================
# TEST CASES
# ============================================================

# def test_normal_query(db: Session) -> None:
#     """
#     Test retrieval node with a normal HR policy query.
#     """

#     print("\n" + "=" * 70)
#     print("TEST CASE 1: NORMAL HR QUERY")
#     print("=" * 70)

#     state = {
#         "query": (
#             "How many annual leave days "
#             "do employees receive?"
#         )
#     }

#     result = retrieval_node(
#         state=state,
#         db=db,
#     )

#     retrieval_results = result.get(
#         "retrieval_results",
#         [],
#     )

#     context = result.get(
#         "context",
#         "",
#     )

#     print("\n" + "-" * 70)
#     print("RETRIEVAL NODE RESULT")
#     print("-" * 70)

#     print(
#         f"Retrieval results: "
#         f"{len(retrieval_results)}"
#     )

#     print(
#         f"Context length: "
#         f"{len(context)} characters"
#     )

#     print("\nContext:")
#     print(context)

#     assert len(retrieval_results) > 0, (
#         "Expected retrieval results, "
#         "but received none."
#     )

#     assert context.strip(), (
#         "Expected context, "
#         "but context is empty."
#     )

#     print("\n✓ Test case 1 passed.")


# def test_empty_query(db: Session) -> None:
#     """
#     Test retrieval node with an empty query.
#     """

#     print("\n" + "=" * 70)
#     print("TEST CASE 2: EMPTY QUERY")
#     print("=" * 70)

#     state = {
#         "query": ""
#     }

#     result = retrieval_node(
#         state=state,
#         db=db,
#     )

#     retrieval_results = result.get(
#         "retrieval_results",
#         [],
#     )

#     context = result.get(
#         "context",
#         "",
#     )

#     print(
#         f"Retrieval results: "
#         f"{len(retrieval_results)}"
#     )

#     print(
#         f"Context: "
#         f"'{context}'"
#     )

#     assert retrieval_results == [], (
#         "Expected empty retrieval results."
#     )

#     assert context == "", (
#         "Expected empty context."
#     )

#     print("\n✓ Test case 2 passed.")


# def test_context_contains_annual_leave(
#     db: Session,
# ) -> None:
#     """
#     Verify that the generated context contains
#     the relevant annual-leave policy information.
#     """

#     print("\n" + "=" * 70)
#     print("TEST CASE 3: CONTEXT CONTENT")
#     print("=" * 70)

#     state = {
#         "query": (
#             "How many annual leave days "
#             "do employees receive?"
#         )
#     }

#     result = retrieval_node(
#         state=state,
#         db=db,
#     )

#     context = result.get(
#         "context",
#         "",
#     )

#     print("\nGenerated context:")
#     print(context)

#     context_lower = context.lower()

#     assert "annual leave" in context_lower, (
#         "Expected 'annual leave' "
#         "in the generated context."
#     )

#     assert "20 days" in context_lower, (
#         "Expected '20 days' "
#         "in the generated context."
#     )

#     print("\n✓ Test case 3 passed.")


# # ============================================================
# # MAIN TEST
# # ============================================================

# def main() -> None:
#     """
#     Run retrieval node tests.
#     """

#     print("\n" + "=" * 70)
#     print("RETRIEVAL NODE TEST")
#     print("=" * 70)

#     # --------------------------------------------------------
#     # Create database session
#     # --------------------------------------------------------

#     from BACKEND.Database.database import (
#         session_local,
#     )

#     db = session_local()

#     try:

#         # ----------------------------------------------------
#         # Test 1
#         # ----------------------------------------------------

#         test_normal_query(
#             db=db,
#         )

#         # ----------------------------------------------------
#         # Test 2
#         # ----------------------------------------------------

#         test_empty_query(
#             db=db,
#         )

#         # ----------------------------------------------------
#         # Test 3
#         # ----------------------------------------------------

#         test_context_contains_annual_leave(
#             db=db,
#         )

#         # ----------------------------------------------------
#         # All tests passed
#         # ----------------------------------------------------

#         print("\n" + "=" * 70)
#         print("ALL RETRIEVAL NODE TESTS PASSED")
#         print("=" * 70)

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