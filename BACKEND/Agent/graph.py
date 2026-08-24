from functools import partial
from typing import Any, Dict

from langgraph.graph import StateGraph, END
from sqlalchemy.orm import Session

from BACKEND.Agent.state import HRBotState
from BACKEND.Agent.nodes.chat_history_node import chat_history_node
from BACKEND.Agent.nodes.retrieval_node import retrieval_node
from BACKEND.Agent.nodes.answer_node import answer_node
from BACKEND.Agent.nodes.save_chat_history_node import save_chat_history_node



def build_graph(db: Session):
    """
    Build (and compile) the HR Copilot LangGraph state machine
    for a single request, bound to the given DB session.
    """

    graph_builder = StateGraph(HRBotState)

    # --------------------------------------------------------
    # NODES
    # --------------------------------------------------------

    graph_builder.add_node(
        "chat_history",
        partial(chat_history_node, db=db),
    )

    graph_builder.add_node(
        "retrieval",
        partial(retrieval_node, db=db),
    )

    graph_builder.add_node(
        "answer",
        answer_node,
    )

    graph_builder.add_node(
        "save_chat_history",
        partial(save_chat_history_node, db=db),
    )

    # --------------------------------------------------------
    # EDGES
    # --------------------------------------------------------

    graph_builder.set_entry_point("chat_history")

    graph_builder.add_edge("chat_history", "retrieval")
    graph_builder.add_edge("retrieval", "answer")
    graph_builder.add_edge("answer", "save_chat_history")
    graph_builder.add_edge("save_chat_history", END)

    return graph_builder.compile()


# ============================================================
# CONVENIENCE ENTRYPOINT
# ============================================================

def run_hr_copilot_graph(
    user_id: int,
    query: str,
    db: Session,
) -> Dict[str, Any]:
    """
    Build the graph for this request's DB session and run it
    end-to-end for a single user query.

    Returns the final graph state, which includes:

        {
            "user_id": int,
            "query": str,
            "chat_history": str,
            "retrieval_results": list,
            "context": str,
            "answer": str,
        }
    """

    graph = build_graph(db)

    initial_state: HRBotState = {
        "user_id": user_id,
        "query": query,
    }

    final_state = graph.invoke(initial_state)

    return final_state


# ============================================================
# MANUAL TEST
# ============================================================

if __name__ == "__main__":

    from BACKEND.Database.database import session_local

    db = session_local()

    try:
        result = run_hr_copilot_graph(
            user_id=1,
            query="How many annual leave days do employees receive?",
            db=db,
        )

        print("\nFinal answer:\n", result.get("answer"))

    finally:
        db.close()
