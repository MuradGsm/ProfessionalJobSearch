from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class MessageOut(BaseModel):
    chat_id: str
    user_id: int
    sender_role: str
    text: str
    created_at: datetime = datetime.utcnow()

class MessageCreate(BaseModel):
    recipient_id: int
    text: str

class MessageResponse(BaseModel):
    chat_id: str
    user_id: int
    sender_role: str
    text: str
    created_at: datetime

class ChatListResponse(BaseModel):
    chat_id: str
    other_user_id: int
    other_user_name: str
    other_user_role: str
    last_message: Optional[str] = None
    last_message_time: Optional[datetime] = None