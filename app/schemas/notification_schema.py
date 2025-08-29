from pydantic import BaseModel
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    message = "message"
    response = "response"
    system = "system"

class NotificationSchema(BaseModel):
    id: int
    user_id: int
    type: NotificationType
    content: str
    is_read: bool = False
    created_at: datetime

