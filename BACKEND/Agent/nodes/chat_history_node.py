from typing import Any, Dict

from sqlalchemy.orm import Session

from BACKEND.Models.model import ChatHistory


# ============================================================
# CONFIGURATION
# ============================================================

# Maximum number of previous chat records sent to the LLM.
#
# 50 records means:
#
#   Query 1 + Response 1
#   Query 2 + Response 2
#   ...
#
# Depending on your application, this can later be changed
# to 30, 40, 50, etc.
#
MAX_HISTORY = 50


# ============================================================
# CHAT HISTORY NODE
# ============================================================

def chat_history_node(
    state: Dict[str, Any],
    db: Session,
) -> Dict[str, Any]:
    """
    LangGraph chat-history node.

    Purpose:

        Fetch the current user's previous conversations
        from the ChatHistory PostgreSQL table.

    Flow:

        user_id
           ↓
        ChatHistory table
           ↓
        latest 50 records
           ↓
        reverse chronological order
           ↓
        format as readable text
           ↓
        state["chat_history"]

    Expected input state:

        {
            "user_id": int,
            "query": str,
        }

    Returned state:

        {
            "chat_history": str,
        }

    Important:

    - Only the current user's history is retrieved.
    - History is NOT converted into HumanMessage / AIMessage.
    - Database history remains plain text for now.
    - This node does NOT modify the database.
    """


    # ========================================================
    # GET USER ID
    # ========================================================

    user_id = state.get(
        "user_id"
    )


    # ========================================================
    # VALIDATE USER ID
    # ========================================================

    if user_id is None:

        print("\n" + "=" * 70)
        print("CHAT HISTORY NODE")
        print("=" * 70)

        print(
            "\nNo user_id provided."
        )

        return {
            "chat_history": "",
        }


    # ========================================================
    # PRINT NODE INFORMATION
    # ========================================================

    print("\n" + "=" * 70)
    print("LANGGRAPH CHAT HISTORY NODE")
    print("=" * 70)

    print(
        f"\nUser ID: {user_id}"
    )

    print(
        f"Maximum history records: "
        f"{MAX_HISTORY}"
    )


    # ========================================================
    # FETCH USER CHAT HISTORY
    # ========================================================
    #
    # We first fetch the newest records.
    #
    # Example DB:
    #
    # id    timestamp
    # 50    newest
    # 49
    # 48
    # ...
    #
    # LIMIT 50
    #
    # Then we reverse the result so the LLM receives:
    #
    # oldest → newest
    #
    # This is more natural for conversation history.
    #
    # ========================================================

    print("\n" + "-" * 70)
    print("FETCHING USER CHAT HISTORY")
    print("-" * 70)

    history_records = (
        db.query(ChatHistory)
        .filter(
            ChatHistory.user_id == user_id
        )
        .order_by(
            ChatHistory.timestamp.desc()
        )
        .limit(
            MAX_HISTORY
        )
        .all()
    )


    # ========================================================
    # NO HISTORY
    # ========================================================

    if not history_records:

        print(
            "\nNo previous chat history found."
        )

        return {
            "chat_history": "",
        }


    # ========================================================
    # REVERSE HISTORY
    # ========================================================
    #
    # Database query:
    #
    # newest → oldest
    #
    # Convert to:
    #
    # oldest → newest
    #
    # ========================================================

    history_records.reverse()


    # ========================================================
    # FORMAT HISTORY
    # ========================================================

    history_parts = []


    for record in history_records:

        user_query = (
            record.user_query
            or ""
        ).strip()

        bot_response = (
            record.bot_response
            or ""
        ).strip()


        # ----------------------------------------------------
        # Skip invalid records
        # ----------------------------------------------------

        if not user_query and not bot_response:
            continue


        # ----------------------------------------------------
        # Format one conversation
        # ----------------------------------------------------

        history_parts.append(
            f"Query: {user_query}\n"
            f"Bot Response: {bot_response}"
        )


    # ========================================================
    # BUILD FINAL CHAT HISTORY
    # ========================================================

    chat_history = "\n\n".join(
        history_parts
    )


    # ========================================================
    # PRINT INFORMATION
    # ========================================================

    print(
        f"\nHistory records retrieved: "
        f"{len(history_records)}"
    )

    print(
        f"History characters: "
        f"{len(chat_history)}"
    )


    # ========================================================
    # PRINT HISTORY
    # ========================================================

    print("\n" + "-" * 70)
    print("USER CHAT HISTORY")
    print("-" * 70)

    if chat_history:

        print(
            f"\n{chat_history}"
        )

    else:

        print(
            "\nNo valid chat history found."
        )


    # ========================================================
    # RETURN UPDATED STATE
    # ========================================================

    return {
        "chat_history": chat_history,
    }


# ============================================================
# TEST HELPER
# ============================================================

def print_chat_history_result(
    result: Dict[str, Any],
) -> None:
    """
    Print chat-history node result.
    """

    print("\n" + "=" * 70)
    print("CHAT HISTORY NODE RESULT")
    print("=" * 70)

    chat_history = result.get(
        "chat_history",
        "",
    )

    if chat_history:

        print(
            f"\n{chat_history}"
        )

    else:

        print(
            "\nNo chat history."
        )


# ============================================================
# TEST CASE 1
# ============================================================

def test_existing_user_history(
    db: Session,
    user_id: int,
):
    """
    Test retrieving chat history for an existing user.

    Pass a real user_id from your users table.
    """

    print("\n" + "=" * 70)
    print("TEST CASE 1: EXISTING USER CHAT HISTORY")
    print("=" * 70)

    state = {
        "user_id": user_id,
        "query": "What is the annual leave policy?",
    }

    result = chat_history_node(
        state=state,
        db=db,
    )

    print_chat_history_result(
        result
    )

    assert (
        "chat_history" in result
    )

    print(
        "\n✓ Test case 1 passed."
    )


# ============================================================
# TEST CASE 2
# ============================================================

def test_user_with_no_history(
    db: Session,
):
    """
    Test a user ID that should have no chat history.

    We use a very large ID to avoid accidentally matching
    a normal user.
    """

    print("\n" + "=" * 70)
    print("TEST CASE 2: USER WITH NO CHAT HISTORY")
    print("=" * 70)

    state = {
        "user_id": 999999999,
        "query": "What is the annual leave policy?",
    }

    result = chat_history_node(
        state=state,
        db=db,
    )

    print_chat_history_result(
        result
    )

    assert (
        result.get(
            "chat_history",
            "",
        ) == ""
    )

    print(
        "\n✓ Test case 2 passed."
    )


# ============================================================
# TEST CASE 3
# ============================================================

def test_missing_user_id(
    db: Session,
):
    """
    Test behavior when user_id is missing.
    """

    print("\n" + "=" * 70)
    print("TEST CASE 3: MISSING USER ID")
    print("=" * 70)

    state = {
        "query": "What is the annual leave policy?",
    }

    result = chat_history_node(
        state=state,
        db=db,
    )

    print_chat_history_result(
        result
    )

    assert (
        result.get(
            "chat_history",
            "",
        ) == ""
    )

    print(
        "\n✓ Test case 3 passed."
    )


# ============================================================
# MAIN TEST
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("CHAT HISTORY NODE TESTS")
    print("=" * 70)

    # --------------------------------------------------------
    # IMPORTANT
    # --------------------------------------------------------
    #
    # Use your existing database session.
    #
    # Change this import if your project exposes
    # SessionLocal from another module.
    #
    # --------------------------------------------------------

    from BACKEND.Database.database import (
        session_local,
    )


    db = session_local()


    try:

        # ====================================================
        # TEST CASE 1
        # ====================================================
        #
        # Replace this with a real user ID from your users
        # table.
        #
        # Example:
        #
        # USER_ID = 1
        #
        # ====================================================

        USER_ID = 1

        test_existing_user_history(
            db=db,
            user_id=USER_ID,
        )


        # ====================================================
        # TEST CASE 2
        # ====================================================

        test_user_with_no_history(
            db=db,
        )


        # ====================================================
        # TEST CASE 3
        # ====================================================

        test_missing_user_id(
            db=db,
        )


        # ====================================================
        # FINAL
        # ====================================================

        print("\n" + "=" * 70)
        print(
            "ALL CHAT HISTORY NODE TESTS COMPLETED"
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

