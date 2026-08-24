from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from BACKEND.Database.get_db import get_db
from BACKEND.Utils.auth_utils import verify_token
from BACKEND.Models.model import ChatHistory
from BACKEND.Schema.auth_schema import StandardResponse


chatHistoryRouter = APIRouter()


## CHAT HISTORY [FOR USERS]
@chatHistoryRouter.get("/chat-history", response_model=StandardResponse)
async def get_chat_history(current_user = Depends(verify_token), db: Session = Depends(get_db)):

    user_id = current_user["id"]
    user_email = current_user["email"]

    try:
        records = (
            db.query(ChatHistory)
            .filter(ChatHistory.user_id == user_id)
            .order_by(ChatHistory.timestamp.asc())
            .all()
        )

        history = [
            {
                "id": record.id,
                "user_query": record.user_query,
                "bot_response": record.bot_response,
                "timestamp": (
                    record.timestamp.isoformat()
                    if record.timestamp
                    else None
                ),
            }
            for record in records
        ]

        return StandardResponse(
            data={"history": history},
            error=None,
            message="Chat history fetched successfully",
            status=True,
        )

    except Exception as e:
        return StandardResponse(
            data=None,
            error=str(e),
            message="Failed to fetch chat history",
            status=False,
        )
