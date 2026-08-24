from typing import Any, Dict

from langchain_core.messages import (
    HumanMessage,
    SystemMessage,
)

from BACKEND.Config.llm_model import (
    get_groq_llm,
)

from BACKEND.Prompt.llm_prompt import (
    HR_POLICY_SYSTEM_PROMPT,
)


# ============================================================
# ANSWER NODE
# ============================================================

def answer_node(
    state: Dict[str, Any],
) -> Dict[str, Any]:
    """
    LangGraph answer-generation node.

    Expected state:

        {
            "user_id": int,
            "query": str,
            "chat_history": str,
            "retrieval_results": list,
            "context": str,
            "answer": str,
        }

    Flow:

        user query
             +
        current user's DB chat history
             +
        retrieved HR policy context
             ↓
            LLM
             ↓
          answer

    Important:

    - chat_history comes from the ChatHistory database table.
    - chat_history is plain text.
    - We are NOT converting database history into
      HumanMessage / AIMessage.
    - context contains the retrieved HR policy text.
    - HR policy context is the ONLY factual source for
      HR policy answers.
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

    if not query or not query.strip():

        return {
            "answer": "",
        }

    query = query.strip()


    chat_history = state.get(
        "chat_history",
        "",
    )

    if chat_history is None:
        chat_history = ""

    chat_history = chat_history.strip()


    # ========================================================
    # GET RETRIEVED HR POLICY CONTEXT
    # ========================================================

    context = state.get(
        "context",
        "",
    )

    if context is None:
        context = ""

    context = context.strip()


    # ========================================================
    # PRINT NODE INFORMATION
    # ========================================================

    print("\n" + "=" * 70)
    print("LANGGRAPH ANSWER NODE")
    print("=" * 70)

    print(
        f"\nUser ID: {user_id}"
    )

    print(
        f"\nCurrent query:\n{query}"
    )

    print(
        f"\nChat history characters: "
        f"{len(chat_history)}"
    )

    print(
        f"Context characters: "
        f"{len(context)}"
    )



    if not context:

        answer = (
            "I could not find this information "
            "in the HR policy."
        )

        print("\n" + "-" * 70)
        print("NO HR POLICY CONTEXT FOUND")
        print("-" * 70)

        print(
            f"\nAnswer:\n{answer}"
        )

        return {
            "answer": answer,
        }


    # ========================================================
    # GET CACHED LLM
    # ========================================================

    llm = get_groq_llm()


    # ========================================================
    # BUILD SYSTEM PROMPT
    # ========================================================
    #
    # The prompt contains:
    #
    # 1. HR policy context
    # 2. Current user query
    # 3. User-specific chat history
    #
    # ========================================================

    system_message = SystemMessage(
        content=HR_POLICY_SYSTEM_PROMPT.format(
            context=context,
            query=query,
            chat_history=(
                chat_history
                if chat_history
                else "No previous conversation."
            ),
        )
    )


    # ========================================================
    # BUILD LLM MESSAGE LIST
    # ========================================================
    #
    # We intentionally do NOT pass the DB chat history as
    # HumanMessage / AIMessage.
    #
    # The complete conversation history is already included
    # inside the formatted prompt.
    #
    # ========================================================

    llm_messages = [
        system_message,
        HumanMessage(
            content=query
        ),
    ]


    # ========================================================
    # CALL LLM
    # ========================================================

    print("\n" + "-" * 70)
    print("GENERATING HR POLICY ANSWER")
    print("-" * 70)

    response = llm.invoke(
        llm_messages
    )


    # ========================================================
    # EXTRACT ANSWER
    # ========================================================

    answer = response.content

    if not isinstance(
        answer,
        str,
    ):

        answer = str(answer)

    answer = answer.strip()


    # ========================================================
    # SAFETY FALLBACK
    # ========================================================

    if not answer:

        answer = (
            "I could not find this information "
            "in the HR policy."
        )


    # ========================================================
    # PRINT ANSWER
    # ========================================================

    print("\n" + "-" * 70)
    print("GENERATED HR POLICY ANSWER")
    print("-" * 70)

    print(
        f"\n{answer}"
    )


    # ========================================================
    # RETURN UPDATED STATE
    # ========================================================
    #
    # IMPORTANT:
    #
    # We only return the generated answer here.
    #
    # ChatHistory database insertion will be handled
    # separately.
    #
    # Later the graph/API flow can save:
    #
    # user_id
    # query
    # answer
    #
    # into ChatHistory.
    #
    # ========================================================

    return {
        "answer": answer,
    }


# ============================================================
# PRINT ANSWER RESULT
# ============================================================

def print_answer_result(
    result: Dict[str, Any],
) -> None:
    """
    Print answer-node test result.
    """

    print("\n" + "=" * 70)
    print("ANSWER NODE RESULT")
    print("=" * 70)

    print(
        f"\nAnswer:\n"
        f"{result.get('answer', '')}"
    )


# ============================================================
# TEST CASE 1
# ============================================================

def test_normal_hr_question():

    print("\n" + "=" * 70)
    print("TEST CASE 1: NORMAL HR POLICY QUESTION")
    print("=" * 70)

    query = (
        "How many annual leave days "
        "do employees receive?"
    )

    chat_history = """
Query: What is AI?
Bot Response: AI is Artificial Intelligence.

Query: My name is Muhammad Sufyan.
Bot Response: Great Sufyan, how can I assist you today?
"""

    context = """
record_id: 1
policy_section: Leave Policy
policy_item: Annual Leave
policy_text: Full-time employees are entitled to 20 days
of paid annual leave per calendar year.
value: 20.0
unit: days/year
"""

    state = {

        "user_id": 1,

        "query": query,

        "chat_history": chat_history,

        "retrieval_results": [],

        "context": context,
    }

    result = answer_node(
        state
    )

    print_answer_result(
        result
    )

    assert result.get(
        "answer"
    )

    print(
        "\n✓ Test case 1 passed."
    )


# ============================================================
# TEST CASE 2
# ============================================================

def test_information_not_in_policy():

    print("\n" + "=" * 70)
    print("TEST CASE 2: INFORMATION NOT IN POLICY")
    print("=" * 70)

    query = (
        "What is the employee salary?"
    )

    chat_history = """
Query: What is AI?
Bot Response: AI is Artificial Intelligence.
"""

    context = """
COMPANY HR POLICY HANDBOOK

All full-time employees are entitled to 20 days
of paid annual leave per calendar year.

Employees receive 10 paid sick days per year.
"""

    state = {

        "user_id": 1,

        "query": query,

        "chat_history": chat_history,

        "retrieval_results": [],

        "context": context,
    }

    result = answer_node(
        state
    )

    print_answer_result(
        result
    )

    assert result.get(
        "answer"
    )

    print(
        "\n✓ Test case 2 passed."
    )


# ============================================================
# TEST CASE 3
# ============================================================

def test_chat_history_follow_up():

    print("\n" + "=" * 70)
    print("TEST CASE 3: DATABASE CHAT HISTORY + FOLLOW-UP")
    print("=" * 70)

    # --------------------------------------------------------
    # Previous conversation
    # --------------------------------------------------------

    chat_history = """
Query: How many annual leave days do employees receive?
Bot Response: Employees receive 20 days of paid annual leave
per calendar year.
"""

    # --------------------------------------------------------
    # Current query
    # --------------------------------------------------------

    query = (
        "Can they carry some of it forward?"
    )

    # --------------------------------------------------------
    # Current retrieved policy context
    # --------------------------------------------------------

    context = """
COMPANY HR POLICY HANDBOOK

All full-time employees are entitled to 20 days
of paid annual leave per calendar year.

Unused annual leave can be carried forward to the next year,
up to a maximum of 5 days.
"""

    state = {

        "user_id": 1,

        "query": query,

        "chat_history": chat_history,

        "retrieval_results": [],

        "context": context,
    }

    result = answer_node(
        state
    )

    print_answer_result(
        result
    )

    assert result.get(
        "answer"
    )

    print(
        "\n✓ Test case 3 passed."
    )


# ============================================================
# TEST CASE 4
# ============================================================

def test_empty_chat_history():

    print("\n" + "=" * 70)
    print("TEST CASE 4: NO PREVIOUS CHAT HISTORY")
    print("=" * 70)

    query = (
        "How many sick leave days "
        "do employees receive?"
    )

    context = """
record_id: 4
policy_section: Leave Policy
policy_item: Sick Leave
policy_text: Employees receive 10 paid sick days per year.
value: 10.0
unit: days/year
"""

    state = {

        "user_id": 2,

        "query": query,

        "chat_history": "",

        "retrieval_results": [],

        "context": context,
    }

    result = answer_node(
        state
    )

    print_answer_result(
        result
    )

    assert result.get(
        "answer"
    )

    print(
        "\n✓ Test case 4 passed."
    )


# ============================================================
# MAIN
# ============================================================

def main():

    print("\n" + "=" * 70)
    print("ANSWER NODE TESTS")
    print("=" * 70)

    # --------------------------------------------------------
    # Test 1
    # --------------------------------------------------------

    test_normal_hr_question()

    # --------------------------------------------------------
    # Test 2
    # --------------------------------------------------------

    test_information_not_in_policy()

    # --------------------------------------------------------
    # Test 3
    # --------------------------------------------------------

    test_chat_history_follow_up()

    # --------------------------------------------------------
    # Test 4
    # --------------------------------------------------------

    test_empty_chat_history()

    # --------------------------------------------------------
    # Final
    # --------------------------------------------------------

    print("\n" + "=" * 70)
    print("ALL ANSWER NODE TESTS COMPLETED")
    print("=" * 70)


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    main()

