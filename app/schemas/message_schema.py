from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class MessageCreate(BaseModel):
    recipient_id: int = Field(..., gt=0)
    text: str = Field(..., min_length=1, max_length=1000)

class MessageResponse(BaseModel):
    id: int
    chat_id: str
    sender_id: int
    recipient_id: int
    text: str
    is_read: bool
    created_at: datetime

    class Config:
        from_attributes = True

class ChatListResponse(BaseModel):
    chat_id: str
    other_user_id: int
    other_user_name: str
    other_user_role: str
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None
    unread_count: int = 0
