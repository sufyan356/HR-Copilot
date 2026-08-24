from typing import Any, Dict

from sqlalchemy.orm import Session

from BACKEND.Models.model import ChatHistory


# ============================================================
# SAVE CHAT HISTORY NODE
# ============================================================

def save_chat_history_node(
    state: Dict[str, Any],
    db: Session,
) -> Dict[str, Any]:
    """
    LangGraph node responsible for saving the current
    conversation into PostgreSQL.

    Expected state:

        {
            "user_id": int,
            "query": str,
            "answer": str,
        }

    Database table:

        ChatHistory

        - id
        - user_id
        - user_query
        - bot_response
        - timestamp

    This node does NOT:
        - perform retrieval
        - call the LLM
        - fetch chat history

    It only saves the current conversation.
    """


    # ========================================================
    # GET USER ID
    # ========================================================

    user_id = state.get(
        "user_id"
    )


    # ========================================================
    # GET CURRENT QUERY
    # ========================================================

    query = state.get(
        "query",
        "",
    )


    # ========================================================
    # GET BOT ANSWER
    # ========================================================

    answer = state.get(
        "answer",
        "",
    )


    # ========================================================
    # VALIDATION
    # ========================================================

    if user_id is None:

        print("\n" + "=" * 70)
        print("SAVE CHAT HISTORY NODE")
        print("=" * 70)

        print(
            "\nERROR: user_id is missing."
        )

        return {}


    if not query or not query.strip():

        print(
            "\nERROR: query is empty."
        )

        return {}


    if not answer or not answer.strip():

        print(
            "\nERROR: answer is empty."
        )

        return {}


    query = query.strip()
    answer = answer.strip()


    # ========================================================
    # PRINT NODE INFORMATION
    # ========================================================

    print("\n" + "=" * 70)
    print("LANGGRAPH SAVE CHAT HISTORY NODE")
    print("=" * 70)

    print(
        f"\nUser ID: {user_id}"
    )

    print(
        f"\nUser Query:\n{query}"
    )

    print(
        f"\nBot Answer:\n{answer}"
    )


    # ========================================================
    # CREATE CHAT HISTORY RECORD
    # ========================================================

    chat_record = ChatHistory(

        user_id=user_id,

        user_query=query,

        bot_response=answer,
    )


    # ========================================================
    # SAVE TO DATABASE
    # ========================================================

    print("\n" + "-" * 70)
    print("SAVING CHAT HISTORY TO POSTGRESQL")
    print("-" * 70)

    try:

        db.add(
            chat_record
        )

        db.commit()

        db.refresh(
            chat_record
        )


    except Exception as e:

        # ----------------------------------------------------
        # Rollback is important if INSERT fails.
        # ----------------------------------------------------

        db.rollback()

        print(
            "\nERROR: Failed to save "
            "chat history."
        )

        print(
            f"Error: {e}"
        )

        raise


    # ========================================================
    # SUCCESS
    # ========================================================

    print(
        "\nChat history saved successfully."
    )

    print(
        f"Chat history ID: "
        f"{chat_record.id}"
    )

    print(
        f"User ID: "
        f"{chat_record.user_id}"
    )

    print(
        f"Timestamp: "
        f"{chat_record.timestamp}"
    )


    # ========================================================
    # RETURN STATE
    # ========================================================
    #
    # We don't need to add anything new to the state.
    #
    # The important operation of this node is the database
    # INSERT.
    #
    # Returning the existing values keeps the state available
    # if we inspect the graph result.
    #
    # ========================================================

    return {
        "user_id": user_id,
        "query": query,
        "answer": answer,
    }


# ============================================================
# TEST HELPER
# ============================================================

def print_save_result(
    result: Dict[str, Any],
) -> None:
    """
    Print save-node test result.
    """

    print("\n" + "=" * 70)
    print("SAVE CHAT HISTORY RESULT")
    print("=" * 70)

    print(
        f"\nUser ID: "
        f"{result.get('user_id')}"
    )

    print(
        f"\nQuery:\n"
        f"{result.get('query', '')}"
    )

    print(
        f"\nAnswer:\n"
        f"{result.get('answer', '')}"
    )


# ============================================================
# TEST CASE 1
# ============================================================

def test_save_chat_history(
    db: Session,
    user_id: int,
):
    """
    Test saving one conversation for a real user.
    """

    print("\n" + "=" * 70)
    print("TEST CASE 1: SAVE CHAT HISTORY")
    print("=" * 70)


    state = {

        "user_id": user_id,

        "query": (
            "How many annual leave days "
            "do employees receive?"
        ),

        "answer": (
            "Full-time employees receive "
            "20 days of paid annual leave "
            "per calendar year."
        ),
    }


    result = save_chat_history_node(
        state=state,
        db=db,
    )


    print_save_result(
        result
    )


    assert (
        result.get("user_id")
        == user_id
    )

    assert (
        result.get("query")
        == state["query"]
    )

    assert (
        result.get("answer")
        == state["answer"]
    )


    # --------------------------------------------------------
    # Verify the record actually exists in PostgreSQL.
    # --------------------------------------------------------

    saved_record = (
        db.query(ChatHistory)
        .filter(
            ChatHistory.user_id == user_id,

            ChatHistory.user_query
            == state["query"],

            ChatHistory.bot_response
            == state["answer"],
        )
        .order_by(
            ChatHistory.id.desc()
        )
        .first()
    )


    assert (
        saved_record is not None
    )


    print(
        "\n✓ Test case 1 passed."
    )


# ============================================================
# TEST CASE 2
# ============================================================

def test_missing_user_id(
    db: Session,
):
    """
    Test that the node does not save anything when
    user_id is missing.
    """

    print("\n" + "=" * 70)
    print("TEST CASE 2: MISSING USER ID")
    print("=" * 70)


    state = {

        "query": (
            "How many annual leave days "
            "do employees receive?"
        ),

        "answer": (
            "Employees receive 20 days "
            "of paid annual leave."
        ),
    }


    result = save_chat_history_node(
        state=state,
        db=db,
    )


    assert (
        result == {}
    )


    print(
        "\n✓ Test case 2 passed."
    )


# ============================================================
# TEST CASE 3
# ============================================================

def test_empty_query(
    db: Session,
    user_id: int,
):
    """
    Test that an empty query is not saved.
    """

    print("\n" + "=" * 70)
    print("TEST CASE 3: EMPTY QUERY")
    print("=" * 70)


    state = {

        "user_id": user_id,

        "query": "",

        "answer": (
            "Employees receive 20 days "
            "of paid annual leave."
        ),
    }


    result = save_chat_history_node(
        state=state,
        db=db,
    )


    assert (
        result == {}
    )


    print(
        "\n✓ Test case 3 passed."
    )


# ============================================================
# TEST CASE 4
# ============================================================

def test_empty_answer(
    db: Session,
    user_id: int,
):
    """
    Test that an empty answer is not saved.
    """

    print("\n" + "=" * 70)
    print("TEST CASE 4: EMPTY ANSWER")
    print("=" * 70)


    state = {

        "user_id": user_id,

        "query": (
            "How many annual leave days "
            "do employees receive?"
        ),

        "answer": "",
    }


    result = save_chat_history_node(
        state=state,
        db=db,
    )


    assert (
        result == {}
    )


    print(
        "\n✓ Test case 4 passed."
    )


# ============================================================
# MAIN TEST
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("SAVE CHAT HISTORY NODE TESTS")
    print("=" * 70)


    # ========================================================
    # DATABASE SESSION
    # ========================================================

    from BACKEND.Database.database import (
        session_local,
    )


    db = session_local()


    try:

        # ====================================================
        # IMPORTANT
        # ====================================================
        #
        # Change this to an existing user ID from your
        # users table.
        #
        # Example:
        #
        # USER_ID = 1
        #
        # ====================================================

        USER_ID = 1


        # ====================================================
        # TEST CASE 1
        # ====================================================

        test_save_chat_history(
            db=db,
            user_id=USER_ID,
        )


        # ====================================================
        # TEST CASE 2
        # ====================================================

        test_missing_user_id(
            db=db,
        )


        # ====================================================
        # TEST CASE 3
        # ====================================================

        test_empty_query(
            db=db,
            user_id=USER_ID,
        )


        # ====================================================
        # TEST CASE 4
        # ====================================================

        test_empty_answer(
            db=db,
            user_id=USER_ID,
        )


        # ====================================================
        # FINAL
        # ====================================================

        print("\n" + "=" * 70)
        print(
            "ALL SAVE CHAT HISTORY NODE "
            "TESTS COMPLETED"
        )
        print("=" * 70)


    finally:

        db.close()

        print(
            "\nDatabase connection closed."
        )


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()

