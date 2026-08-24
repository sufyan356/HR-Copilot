from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from BACKEND.Database.get_db import get_db
from BACKEND.Utils.auth_utils import verify_token
from BACKEND.Schema.chat_schema import ChatRequest
from BACKEND.Schema.auth_schema import StandardResponse
from BACKEND.Agent.graph import run_hr_copilot_graph


chatRouter = APIRouter()


## CHAT [FOR USERS]
@chatRouter.post("/chat", response_model=StandardResponse)
async def chat(req: ChatRequest, current_user = Depends(verify_token), db: Session = Depends(get_db)):

    user_id = current_user["id"]
    user_email = current_user["email"]

    try:
        final_state = run_hr_copilot_graph(
            user_id=user_id,
            query=req.query,
            db=db,
        )

        answer = final_state.get("answer", "")
        results = final_state.get("retrieval_results", [])

        results = sorted(results, key=lambda r: r.get("rerank_score", 0), reverse=True)

        sources = []

        for r in results:
            entry = {
                "file_name": r.get("file_name"),
                "file_type": r.get("file_type"),
                "source": r.get("source"),
                "page_number": r.get("page_number"),
                "row_number": r.get("row_number"),
            }

            if entry in sources:
                continue

            sources.append(entry)

            if len(sources) == 3:
                break

        return StandardResponse(
            data={"answer": answer, "sources": sources},
            error=None,
            message="Answer generated successfully",
            status=True,
        )

    except Exception as e:
        return StandardResponse(
            data=None,
            error=str(e),
            message="Chat failed",
            status=False,
        )