from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


# ============================================================
# CHAT REQUEST
# ============================================================

class ChatRequest(BaseModel):
    query: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="The user's HR policy question.",
    )


# ============================================================
# CHAT ANSWER (data payload inside StandardResponse)
# ============================================================

class ChatAnswerData(BaseModel):
    answer: str


# ============================================================
# CHAT HISTORY ITEM
# ============================================================

class ChatHistoryItem(BaseModel):
    id: int
    user_query: str
    bot_response: str
    timestamp: Optional[datetime] = None

    class Config:
        from_attributes = True


# ============================================================
# CHAT HISTORY LIST (data payload inside StandardResponse)
# ============================================================

class ChatHistoryData(BaseModel):
    history: List[ChatHistoryItem]

# ============================================================
# SOURCE (citation) ITEM
# ============================================================

class SourceItem(BaseModel):
    file_name: Optional[str] = None
    file_type: Optional[str] = None
    source: Optional[str] = None
    page_number: Optional[int] = None
    row_number: Optional[int] = None