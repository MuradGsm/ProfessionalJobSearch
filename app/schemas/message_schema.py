from pydantic import BaseModel
from datetime import datetime

class Message(BaseModel):
    chat_id: int
    user_id: int
    text: str
    timestamp: datetime | None = None