from pydantic import BaseModel
from app.schemas.notification_schema import NotificationSchema

class ApplicationBase(BaseModel):
    status: str = "sent"  
    job_id: int

class ApplicationResponse(ApplicationBase):
    id: int
    user_id: int


class ApplicationWithNotificationResponse(BaseModel):
    application: ApplicationResponse
    notification: NotificationSchema
