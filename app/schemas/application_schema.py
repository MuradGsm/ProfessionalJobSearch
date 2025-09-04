from pydantic import BaseModel
from app.schemas.notification_schema import NotificationSchema
from enum import Enum


class ApplicationStatusEnum(str, Enum):
    SENT = "sent"
    REVIEWED = "reviewed"
    REJECTED = "rejected"


class ApplicationBase(BaseModel):
    status: ApplicationStatusEnum = ApplicationStatusEnum.SENT
    job_id: int


class ApplicationResponse(ApplicationBase):
    id: int
    user_id: int

    class Config:
        from_attributes = True


class ApplicationWithNotificationResponse(BaseModel):
    application: ApplicationResponse
    notification: NotificationSchema

    class Config:
        from_attributes = True


        
