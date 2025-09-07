from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum

class NotificationType(str, Enum):
    message = "message"
    application = "application"
    job_update = "job_update"
    system = "system"

class NotificationCreate(BaseModel):
    user_id: int = Field(..., gt=0)
    type: NotificationType
    content: str = Field(..., min_length=1, max_length=500)

class NotificationSchema(BaseModel):
    id: int
    user_id: int
    type: NotificationType
    content: str
    is_read: bool = False
    created_at: datetime

    class Config:
        from_attributes = True

class NotificationMarkRead(BaseModel):
    is_read: bool = True